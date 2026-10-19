"""Offline schema-compatibility check: the working tree against every committed version.

The registry enforces compatibility when a schema is registered, but that happens after a merge.
This check runs before, on a PC or in CI, without a registry: it rebuilds every distinct version of
each subject from the git history of schemas/events and checks the current schema against them
with the reference Apache Avro checker, at the level set in the catalogue.

- BACKWARD: the new schema can read data written with the previous version.
- BACKWARD_TRANSITIVE: the new schema can read data written with every earlier version. Kuizi uses
  this level because Kafka keeps days of events, the warehouse keeps months, and replays (T031)
  read old data with today's schema.
- FORWARD / FULL (and their _TRANSITIVE forms) are supported for completeness.

CI must fetch the full history (actions/checkout with fetch-depth: 0); in a shallow clone the check
only sees the commits it has and says so.
"""

from __future__ import annotations

import io
import subprocess
import tarfile
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from avro.compatibility import ReaderWriterCompatibilityChecker, SchemaCompatibilityType

from . import Paths
from .avsc import SchemaError, canonical, load_sources, parse_avro


class GitError(Exception):
    """git is missing or the reference cannot be read."""


@dataclass
class Version:
    commit: str
    schema: dict


@dataclass
class Report:
    level: str
    checked: int = 0
    versions: int = 0
    problems: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def compatible(reader: dict, writer: dict) -> tuple[bool, list[str]]:
    """Can a consumer using `reader` decode data written with `writer`?"""
    result = ReaderWriterCompatibilityChecker().get_compatibility(parse_avro(reader), parse_avro(writer))
    if result.compatibility is SchemaCompatibilityType.compatible:
        return True, []
    kinds = sorted(i.name.upper() for i in result.incompatibilities)
    details = sorted(result.messages)
    where = sorted(result.locations)
    return False, [f"{', '.join(kinds)} at {', '.join(where)}: {'; '.join(details)}"]


def check_pair(new: dict, old: dict, level: str) -> list[str]:
    """Problems of `new` against one earlier version `old` at the given level (transitivity aside)."""
    problems = []
    base = level.removesuffix("_TRANSITIVE")
    if base in ("BACKWARD", "FULL"):
        ok, why = compatible(reader=new, writer=old)
        if not ok:
            problems += [f"new schema cannot read data written with this version ({w})" for w in why]
    if base in ("FORWARD", "FULL"):
        ok, why = compatible(reader=old, writer=new)
        if not ok:
            problems += [f"consumers on this version cannot read data written with the new schema ({w})" for w in why]
    return problems


def check_subject(subject: str, new: dict, history: list[Version], level: str) -> list[str]:
    if not history:
        return []
    targets = history if level.endswith("_TRANSITIVE") else history[-1:]
    problems = []
    for version in targets:
        for problem in check_pair(new, version.schema, level):
            problems.append(f"{subject}: against the version of commit {version.commit[:10]}: {problem}")
    return problems


# ---------------------------------------------------------------------------
# History from git
# ---------------------------------------------------------------------------


def git(root: Path, *args: str, binary: bool = False) -> str | bytes:
    try:
        run = subprocess.run(["git", *args], cwd=root, capture_output=True, check=False, timeout=120)
    except FileNotFoundError:
        raise GitError("git is not installed") from None
    if run.returncode != 0:
        raise GitError(f"git {' '.join(args)}: {run.stderr.decode(errors='replace').strip()}")
    return run.stdout if binary else run.stdout.decode()


def subjects_in_tree(events_dir: Path) -> dict[str, dict]:
    """Expanded schemas by registry subject, read from one copy of schemas/events.

    Only needs the catalogue's topics and the .avsc files, so it also reads older layouts.
    """
    catalogue = yaml.safe_load((events_dir / "catalogue.yaml").read_text(encoding="utf-8")) or {}
    topics = {name: entry.get("topic") for name, entry in (catalogue.get("events") or {}).items()}
    sources = load_sources(events_dir)
    out = {}
    for name in sources.events:
        topic = topics.get(name)
        if topic:
            out[f"{topic}-value"] = sources.expanded(name)
    return out


def history(paths: Paths, ref: str = "HEAD") -> tuple[dict[str, list[Version]], list[str]]:
    """Every distinct committed version of every subject, oldest first, reachable from `ref`."""
    notes = []
    root = paths.root
    if git(root, "rev-parse", "--is-shallow-repository").strip() == "true":
        notes.append("shallow clone: only the fetched commits are checked (CI needs fetch-depth: 0)")
    try:
        git(root, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
    except GitError:
        notes.append(f"no commit '{ref}' yet: nothing to compare with")
        return {}, notes
    commits = git(root, "log", "--format=%H", "--reverse", ref, "--", Paths.EVENTS_REL).split()
    versions: dict[str, list[Version]] = {}
    seen: dict[str, set[str]] = {}
    for commit in commits:
        archive = git(root, "archive", "--format=tar", commit, Paths.EVENTS_REL, binary=True)
        with tempfile.TemporaryDirectory(prefix="kuizi-schemas-") as tmp:
            with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
                tar.extractall(tmp, filter="data")
            events_dir = Path(tmp) / Paths.EVENTS_REL
            if not (events_dir / "catalogue.yaml").is_file():
                continue
            try:
                subjects = subjects_in_tree(events_dir)
            except (SchemaError, yaml.YAMLError, KeyError, TypeError) as error:
                notes.append(f"commit {commit[:10]} skipped: its schemas do not load ({error})")
                continue
        for subject, schema in subjects.items():
            key = canonical(schema)
            if key in seen.setdefault(subject, set()):
                continue
            seen[subject].add(key)
            versions.setdefault(subject, []).append(Version(commit, schema))
    return versions, notes


def check_against_history(paths: Paths, level: str, ref: str = "HEAD") -> Report:
    report = Report(level=level)
    past, report.notes = history(paths, ref)
    current = subjects_in_tree(paths.events)
    for subject, schema in sorted(current.items()):
        report.checked += 1
        report.versions += len(past.get(subject, []))
        report.problems += check_subject(subject, schema, past.get(subject, []), level)
    for subject in sorted(set(past) - set(current)):
        report.problems.append(
            f"{subject}: was committed before but has no schema now; subjects are never"
            " removed (deprecate the event in the catalogue instead)"
        )
    return report
