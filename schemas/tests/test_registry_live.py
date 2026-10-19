"""Against the real local schema registry (Redpanda, make up), on throwaway subjects deleted afterwards.

These prove acceptance criterion 1: the schemas are versioned in the registry, each subject is set to
BACKWARD_TRANSITIVE, and the registry itself refuses an incompatible change. Each verdict is also
compared with the offline checker, so the check that runs before merge agrees with the registry.
"""

from __future__ import annotations

import copy
import json

import pytest

from kuizi_schemas import cli
from kuizi_schemas.avsc import parse_fastavro, to_registry_string
from kuizi_schemas.compat import check_pair
from kuizi_schemas.examples import contains, load_examples, normalise
from kuizi_schemas.registry import IncompatibleSchema, Registry
from kuizi_schemas.wire import decode, encode

pytestmark = pytest.mark.registry

LEVEL = "BACKWARD_TRANSITIVE"


def with_field(schema: dict, field: dict) -> dict:
    schema = copy.deepcopy(schema)
    schema["fields"].append(field)
    return schema


def start_subject(registry: Registry, subject: str, schema: dict) -> None:
    registry.set_compatibility(subject, LEVEL)
    registry.register(subject, to_registry_string(schema))


def test_registry_rejects_a_new_required_field(live_registry, test_prefix, sources):
    subject = f"{test_prefix}learner.item.answered.v1-value"
    v1 = sources.expanded("item.answered")
    start_subject(live_registry, subject, v1)
    breaking = with_field(v1, {"name": "grade_band", "type": "string", "privacy": "personal", "doc": "x"})
    assert check_pair(breaking, v1, LEVEL), "the offline check rejects it too"
    with pytest.raises(IncompatibleSchema, match="READER_FIELD_MISSING_DEFAULT_VALUE"):
        live_registry.register(subject, to_registry_string(breaking))
    assert live_registry.versions(subject) == [1]


def test_registry_rejects_a_type_change(live_registry, test_prefix, sources):
    subject = f"{test_prefix}learner.session.end.v1-value"
    v1 = sources.expanded("session.end")
    start_subject(live_registry, subject, v1)
    breaking = copy.deepcopy(v1)
    next(f for f in breaking["fields"] if f["name"] == "duration_ms")["type"] = "string"
    assert check_pair(breaking, v1, LEVEL)
    ok, messages = live_registry.check(subject, to_registry_string(breaking))
    assert not ok and messages
    with pytest.raises(IncompatibleSchema):
        live_registry.register(subject, to_registry_string(breaking))


def test_registry_accepts_an_optional_field(live_registry, test_prefix, sources):
    subject = f"{test_prefix}learner.item.presented.v1-value"
    v1 = sources.expanded("item.presented")
    start_subject(live_registry, subject, v1)
    v2 = with_field(v1, {"name": "layout", "type": ["null", "string"], "default": None, "privacy": "none", "doc": "x"})
    assert check_pair(v2, v1, LEVEL) == []
    live_registry.register(subject, to_registry_string(v2))
    assert live_registry.versions(subject) == [1, 2]
    assert live_registry.compatibility_level(subject) == LEVEL


def test_registry_enforces_transitive_compatibility(live_registry, test_prefix, sources):
    """v3 is compatible with v2 alone, but not with v1: BACKWARD would let it through, the registry does not."""
    subject = f"{test_prefix}learner.hint.shown.v1-value"
    v1 = sources.expanded("hint.shown")
    start_subject(live_registry, subject, v1)
    v2 = with_field(v1, {"name": "rank", "type": "int", "default": 0, "privacy": "none", "doc": "x"})
    live_registry.register(subject, to_registry_string(v2))
    v3 = copy.deepcopy(v2)
    del next(f for f in v3["fields"] if f["name"] == "rank")["default"]
    assert check_pair(v3, v2, "BACKWARD") == [] and check_pair(v3, v1, "BACKWARD")
    with pytest.raises(IncompatibleSchema, match="oldSchemaVersion: 1"):
        live_registry.register(subject, to_registry_string(v3))


def test_register_command_versions_every_event(live_registry, test_prefix, catalogue, sources, paths, capsys):
    args = ["register", "--url", live_registry.url, "--subject-prefix", test_prefix]
    assert cli.main(args) == 0
    assert cli.main(args) == 0  # idempotent: the second run changes nothing
    out = capsys.readouterr().out
    assert out.count("registered version 1") == 15 and out.count("unchanged, version 1") == 15
    cache: dict[int, dict] = {}

    def parsed_for_id(schema_id: int) -> dict:
        if schema_id not in cache:
            cache[schema_id] = parse_fastavro(json.loads(live_registry.schema_by_id(schema_id)))
        return cache[schema_id]

    for name, event in catalogue.events.items():
        subject = test_prefix + event.subject
        assert live_registry.compatibility_level(subject) == LEVEL
        registered = live_registry.lookup(subject, to_registry_string(sources.expanded(name)))
        assert registered and registered["version"] == 1
        # Every example round-trips through the registry: encode with the ID, decode with the schema
        # fetched back by ID, as a Kafka consumer does.
        for record in load_examples(paths, event):
            data = encode(registered["id"], parse_fastavro(sources.expanded(name)), record)
            schema_id, decoded = decode(data, parsed_for_id)
            assert schema_id == registered["id"] and contains(record, normalise(decoded))
