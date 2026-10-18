"""The registry client, the `register` command and the wire format, against an in-process fake registry."""

from __future__ import annotations

import copy
import json
import shutil

import pytest

from kuizi_schemas import Paths, cli
from kuizi_schemas.avsc import expand, load_sources, parse_fastavro, to_registry_string
from kuizi_schemas.examples import contains, load_examples, normalise
from kuizi_schemas.registry import IncompatibleSchema, Registry, RegistryError, registry_url
from kuizi_schemas.wire import WireFormatError, decode, encode


def register(fake, *extra):
    return cli.main(["register", "--url", fake.url, *extra])


def test_register_creates_every_subject_with_backward_transitive(fake_registry, catalogue, capsys):
    assert register(fake_registry) == 0
    subjects = {event.subject for event in catalogue.events.values()}
    assert set(fake_registry.subjects) == subjects
    assert all(fake_registry.config[s] == "BACKWARD_TRANSITIVE" for s in subjects)
    assert capsys.readouterr().out.count("registered version 1") == len(subjects)


def test_register_is_idempotent(fake_registry, capsys):
    assert register(fake_registry) == 0
    capsys.readouterr()
    assert register(fake_registry) == 0
    out = capsys.readouterr().out
    assert "registered" not in out and out.count("unchanged, version 1") == 15


def test_dry_run_registers_nothing(fake_registry, capsys):
    assert register(fake_registry, "--dry-run") == 0
    assert fake_registry.subjects == {}
    assert "would register a new version" in capsys.readouterr().out


def test_register_refuses_everything_when_one_subject_is_incompatible(fake_registry, sources, capsys):
    registry = Registry(fake_registry.url)
    old = copy.deepcopy(sources.expanded("item.answered"))
    next(f for f in old["fields"] if f["name"] == "attempt")["type"] = "string"
    registry.register("learner.item.answered.v1-value", to_registry_string(old))
    assert register(fake_registry) == 1
    assert "nothing was registered" in capsys.readouterr().out
    assert list(fake_registry.subjects) == ["learner.item.answered.v1-value"]


def test_subject_prefix(fake_registry):
    assert register(fake_registry, "--subject-prefix", "preview-42.") == 0
    assert all(s.startswith("preview-42.learner.") for s in fake_registry.subjects)


def test_client_calls(fake_registry, sources):
    registry = Registry(fake_registry.url)
    subject = "learner.session.end.v1-value"
    schema = to_registry_string(sources.expanded("session.end"))
    assert registry.reachable()
    assert registry.versions(subject) == []
    assert registry.lookup(subject, schema) is None
    assert registry.compatibility_level(subject) is None
    registry.set_compatibility(subject, "BACKWARD_TRANSITIVE")
    schema_id = registry.register(subject, schema)
    assert registry.versions(subject) == [1]
    assert registry.lookup(subject, schema)["id"] == schema_id
    assert json.loads(registry.schema_by_id(schema_id)) == json.loads(schema)
    assert registry.check(subject, schema) == (True, [])
    breaking = copy.deepcopy(sources.expanded("session.end"))
    breaking["fields"].append({"name": "x", "type": "string", "privacy": "none", "doc": "x"})
    ok, messages = registry.check(subject, to_registry_string(breaking))
    assert not ok and messages
    with pytest.raises(IncompatibleSchema):
        registry.register(subject, to_registry_string(breaking))
    registry.delete_subject(subject)
    assert registry.subjects() == [] and registry.compatibility_level(subject) is None
    registry.delete_subject(subject)  # deleting again is harmless


def test_unreachable_registry_says_how_to_fix_it(capsys):
    registry = Registry("http://127.0.0.1:9", timeout=2)
    assert not registry.reachable()
    with pytest.raises(RegistryError, match="make up"):
        registry.subjects()
    assert cli.main(["register", "--url", "http://127.0.0.1:9"]) == 2
    assert "cannot reach the schema registry" in capsys.readouterr().err


def test_registry_url_comes_from_the_environment_then_dotenv(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("# comment\nKAFKA_PORT=19092\nSCHEMA_REGISTRY_URL=http://localhost:18081/\n")
    monkeypatch.delenv("SCHEMA_REGISTRY_URL", raising=False)
    assert registry_url(env) == "http://localhost:18081"
    monkeypatch.setenv("SCHEMA_REGISTRY_URL", "http://registry.internal:8081")
    assert registry_url(env) == "http://registry.internal:8081"
    monkeypatch.delenv("SCHEMA_REGISTRY_URL")
    with pytest.raises(RegistryError, match="not set"):
        registry_url(tmp_path / "missing.env")


def test_wire_format_round_trip_with_registry_ids(fake_registry, catalogue, sources, paths):
    registry = Registry(fake_registry.url)
    assert register(fake_registry) == 0
    cache: dict[int, dict] = {}

    def parsed_for_id(schema_id):
        if schema_id not in cache:
            cache[schema_id] = parse_fastavro(json.loads(registry.schema_by_id(schema_id)))
        return cache[schema_id]

    for name, event in catalogue.events.items():
        schema = to_registry_string(sources.expanded(name))
        schema_id = registry.lookup(event.subject, schema)["id"]
        for record in load_examples(paths, event):
            data = encode(schema_id, parse_fastavro(sources.expanded(name)), record)
            assert data[0] == 0 and int.from_bytes(data[1:5], "big") == schema_id
            got_id, decoded = decode(data, parsed_for_id)
            assert got_id == schema_id and contains(record, normalise(decoded))


def test_wire_format_rejects_foreign_bytes():
    with pytest.raises(WireFormatError):
        decode(b"\x00\x01", lambda _: {})
    with pytest.raises(WireFormatError, match="magic"):
        decode(b"\x07\x00\x00\x00\x01rest", lambda _: {})


def test_expand_writes_one_file_per_subject(tmp_path, capsys):
    assert cli.main(["expand", "--out", str(tmp_path)]) == 0
    files = sorted(p.name for p in tmp_path.iterdir())
    assert len(files) == 15 and "learner.item.answered.v1-value.avsc" in files
    schema = json.loads((tmp_path / "learner.item.answered.v1-value.avsc").read_text())
    parse_fastavro(schema)


def test_docs_command_is_a_no_op_when_current(capsys):
    assert cli.main(["docs"]) == 0
    assert "already up to date" in capsys.readouterr().out


def test_register_checks_every_registered_version_even_when_the_subject_level_is_weaker(
    fake_registry, paths, tmp_path, capsys
):
    """The subject exists at the registry's default level (BACKWARD). The new schema is compatible with
    the latest version only; the transitive pre-check still refuses it, before anything is registered."""
    shutil.copytree(paths.events, tmp_path / Paths.EVENTS_REL)
    path = tmp_path / Paths.EVENTS_REL / "session.end.avsc"
    original = json.loads(path.read_text())
    rank = {"name": "rank", "type": "int", "privacy": "none", "doc": "x"}
    changed = copy.deepcopy(original)
    changed["fields"].append(rank)
    path.write_text(json.dumps(changed))
    sources = load_sources(tmp_path / Paths.EVENTS_REL)
    v1 = expand(original, sources.common)
    v2 = expand({**changed, "fields": [*original["fields"], {**rank, "default": 0}]}, sources.common)
    registry = Registry(fake_registry.url)
    subject = "learner.session.end.v1-value"
    registry.register(subject, to_registry_string(v1))
    registry.register(subject, to_registry_string(v2))
    assert registry.compatibility_level(subject) is None  # still the registry default
    assert cli.main(["--root", str(tmp_path), "register", "--url", fake_registry.url]) == 1
    out = capsys.readouterr().out
    assert "nothing was registered" in out and "READER_FIELD_MISSING_DEFAULT_VALUE" in out
    assert list(fake_registry.subjects) == [subject]
