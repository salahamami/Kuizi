"""The offline compatibility check accepts safe changes and rejects breaking ones, against git history."""

from __future__ import annotations

import copy
import json
import shutil
import subprocess
from pathlib import Path

import pytest
from kuizi_schemas import Paths, cli
from kuizi_schemas.compat import check_against_history, check_pair, history

LEVEL = "BACKWARD_TRANSITIVE"


def answered(sources):
    return copy.deepcopy(sources.expanded("item.answered"))


def add_field(schema, field):
    schema = copy.deepcopy(schema)
    schema["fields"].append(field)
    return schema


OPTIONAL = {"name": "extra_note_id", "type": ["null", "string"], "default": None, "privacy": "none", "doc": "x"}
REQUIRED = {"name": "extra_note_id", "type": "string", "privacy": "none", "doc": "x"}


def test_adding_an_optional_field_is_compatible(sources):
    old = answered(sources)
    assert check_pair(add_field(old, OPTIONAL), old, "BACKWARD") == []


def test_adding_a_required_field_is_rejected(sources):
    old = answered(sources)
    problems = check_pair(add_field(old, REQUIRED), old, "BACKWARD")
    assert problems and "READER_FIELD_MISSING_DEFAULT_VALUE" in problems[0]


def test_changing_a_field_type_is_rejected(sources):
    old = answered(sources)
    new = copy.deepcopy(old)
    next(f for f in new["fields"] if f["name"] == "attempt")["type"] = "string"
    assert check_pair(new, old, "BACKWARD")


def test_enum_defaults_let_symbols_come_and_go(sources):
    old = answered(sources)
    new = copy.deepcopy(old)
    kind = next(f for f in new["fields"] if f["name"] == "response")["type"]["fields"][0]["type"]
    kind["symbols"] = [s for s in kind["symbols"] if s != "SKIPPED"] + ["GRAPH"]
    # A reader meeting an unknown symbol falls back to the enum default (UNKNOWN), in both directions.
    assert check_pair(new, old, "FULL") == []
    del kind["default"]
    assert check_pair(new, old, "BACKWARD"), "without a default, a removed symbol breaks old data"


def test_forward_level_checks_the_other_direction(sources):
    old = answered(sources)
    new = copy.deepcopy(old)
    new["fields"] = [f for f in new["fields"] if f["name"] != "attempt"]  # attempt has no default
    assert check_pair(new, old, "BACKWARD") == []  # a new reader simply ignores it
    assert check_pair(new, old, "FORWARD")  # an old reader needs it and has no default


# ---------------------------------------------------------------------------
# Against git history, in a throwaway repository
# ---------------------------------------------------------------------------


def git(root: Path, *args: str) -> None:
    env = {
        "GIT_AUTHOR_NAME": "t023-test",
        "GIT_AUTHOR_EMAIL": "t023-test@invalid",
        "GIT_COMMITTER_NAME": "t023-test",
        "GIT_COMMITTER_EMAIL": "t023-test@invalid",
        "PATH": "/usr/bin:/bin:/usr/local/bin",
        "HOME": str(root),
    }
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, env=env)


@pytest.fixture
def repo(tmp_path, paths) -> Paths:
    """A git repository holding a copy of schemas/events, with one commit."""
    shutil.copytree(paths.events, tmp_path / Paths.EVENTS_REL)
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-q", "-m", "v1")
    return Paths(tmp_path)


def edit_answered(repo: Paths, change) -> None:
    path = repo.events / "item.answered.avsc"
    schema = json.loads(path.read_text())
    change(schema)
    path.write_text(json.dumps(schema, indent=2))


def commit(repo: Paths, message: str) -> None:
    git(repo.root, "commit", "-q", "-am", message)


def test_unchanged_schemas_pass(repo):
    report = check_against_history(repo, LEVEL)
    assert report.problems == []
    assert report.checked == 15 and report.versions == 15


def test_an_incompatible_working_tree_change_is_rejected(repo, capsys):
    edit_answered(repo, lambda s: s["fields"].append(REQUIRED))
    report = check_against_history(repo, LEVEL)
    assert len(report.problems) == 1
    assert report.problems[0].startswith("learner.item.answered.v1-value: against the version of commit")
    assert "READER_FIELD_MISSING_DEFAULT_VALUE" in report.problems[0]
    assert cli.main(["--root", str(repo.root), "compat"]) == 1
    assert "FAIL" in capsys.readouterr().out


def test_a_compatible_change_passes(repo):
    edit_answered(repo, lambda s: s["fields"].append(OPTIONAL))
    assert check_against_history(repo, LEVEL).problems == []


def test_transitive_catches_what_backward_misses(repo):
    edit_answered(repo, lambda s: s["fields"].append({**OPTIONAL, "type": "int", "default": 0, "name": "extra"}))
    commit(repo, "v2: optional field with a default")

    def drop_default(schema):
        field = next(f for f in schema["fields"] if f["name"] == "extra")
        del field["default"]

    edit_answered(repo, drop_default)
    # Against v2 alone the change looks fine (v2 data has the field) ...
    assert check_against_history(repo, "BACKWARD").problems == []
    # ... but data written with v1 has no value for it and no default to fall back on.
    problems = check_against_history(repo, "BACKWARD_TRANSITIVE").problems
    assert len(problems) == 1 and "learner.item.answered.v1-value" in problems[0]
    versions, _ = history(repo)
    assert len(versions["learner.item.answered.v1-value"]) == 2


def test_an_incompatible_committed_change_is_still_rejected(repo):
    edit_answered(repo, lambda s: s["fields"].append(REQUIRED))
    commit(repo, "bad change")
    assert check_against_history(repo, LEVEL).problems  # the older commit is still in the history


def test_removing_an_event_is_reported(repo):
    (repo.events / "tts.played.avsc").unlink()
    text = repo.catalogue.read_text()
    start = text.index("  tts.played:")
    end = text.index("\n\n", start)
    repo.catalogue.write_text(text[:start] + text[end + 2 :])
    problems = check_against_history(repo, LEVEL).problems
    assert any("learner.tts.played.v1-value: was committed before" in p for p in problems)


def test_a_repository_without_commits_has_nothing_to_compare(tmp_path, paths):
    shutil.copytree(paths.events, tmp_path / Paths.EVENTS_REL)
    git(tmp_path, "init", "-q", "-b", "main")
    report = check_against_history(Paths(tmp_path), LEVEL)
    assert report.problems == [] and report.versions == 0
    assert any("nothing to compare" in n for n in report.notes)


def test_a_folder_outside_git_fails_clearly(tmp_path, paths, capsys):
    shutil.copytree(paths.events, tmp_path / Paths.EVENTS_REL)
    assert cli.main(["--root", str(tmp_path), "compat"]) == 1
    assert "cannot read the git history" in capsys.readouterr().out
