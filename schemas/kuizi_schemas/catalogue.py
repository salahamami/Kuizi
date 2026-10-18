"""Read the data catalogue (schemas/events/catalogue.yaml) and check it against the schemas."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from . import Paths
from .avsc import Sources, find_field, iter_fields

PRIVACY_ORDER = ["none", "pseudonymous", "personal", "sensitive"]
LEVELS = {"BACKWARD", "BACKWARD_TRANSITIVE", "FORWARD", "FORWARD_TRANSITIVE", "FULL", "FULL_TRANSITIVE"}
ORIGINS = {"app", "server"}
# Envelope fields an app always knows, so every app-produced event must fill them. session_id and
# session_seq are required per event in the catalogue (a notification can be opened outside a session).
APP_ENVELOPE = {"client_ts", "device", "app_version"}
TICKET = re.compile(r"T\d{3}")
# When a model input exists: before the learner answers, or only once the attempt is submitted.
KNOWN = {"presentation": "At presentation", "after_answer": "After the answer (one step later)"}
MAX_KAFKA_DAYS = 30  # Kafka copies must expire within the 30-day erasure deadline (T018)
MAX_WAREHOUSE_MONTHS = 24  # raw telemetry rule (T018)


class CatalogueError(Exception):
    """The catalogue is malformed or disagrees with the schemas; one problem per line."""


@dataclass
class Event:
    name: str
    schema: str
    topic: str
    description: str
    owner: str
    producer: dict
    consumers: list[dict]
    retention: dict
    required_envelope: list[str]
    examples: str
    sensitive_readers: list[dict] = field(default_factory=list)

    @property
    def subject(self) -> str:
        return f"{self.topic}-value"


@dataclass
class Catalogue:
    raw: dict
    events: dict[str, Event]

    @property
    def compatibility(self) -> str:
        return self.raw["compatibility"]

    @property
    def privacy(self) -> dict:
        return self.raw["privacy"]

    @property
    def sensitive_records(self) -> list[str]:
        return list(self.privacy.get("sensitive_records", []))

    @property
    def forbidden_names(self) -> set[str]:
        return set(self.privacy.get("forbidden_field_names", []))

    @property
    def ml_features(self) -> list[dict]:
        return list(self.raw.get("ml_features", []))

    @property
    def ml_review(self) -> str | None:
        return self.raw.get("ml_review")

    @property
    def common_consumers(self) -> list[dict]:
        return list(self.raw.get("consumers_of_every_event", []))


def load_catalogue(path: Path) -> Catalogue:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise CatalogueError(f"{path.name}: cannot be read ({error})") from None
    if not isinstance(raw, dict):
        raise CatalogueError(f"{path.name}: must be a mapping")
    problems = []
    for key in ("version", "steward", "compatibility", "topic_prefix", "key", "privacy", "events"):
        if key not in raw:
            problems.append(f"missing top-level key '{key}'")
    if problems:
        raise CatalogueError("\n".join(problems))
    events = {}
    for name, entry in (raw.get("events") or {}).items():
        if not isinstance(entry, dict):
            problems.append(f"events.{name}: must be a mapping")
            continue
        missing = [
            k
            for k in (
                "schema",
                "topic",
                "description",
                "owner",
                "producer",
                "consumers",
                "retention",
                "required_envelope",
                "examples",
            )
            if k not in entry
        ]
        if missing:
            problems.append(f"events.{name}: missing {', '.join(missing)}")
            continue
        extra = set(entry) - set(Event.__dataclass_fields__)
        if extra:
            problems.append(f"events.{name}: unknown keys {', '.join(sorted(extra))}")
            continue
        events[name] = Event(name=name, **entry)
    if problems:
        raise CatalogueError("\n".join(problems))
    return Catalogue(raw, events)


def known_roles(paths: Paths) -> set[str] | None:
    if not paths.agents.is_dir():
        return None
    return {p.stem for p in paths.agents.glob("*.md")}


def known_tickets(paths: Paths) -> set[str] | None:
    if not paths.backlog.is_file():
        return None
    backlog = json.loads(paths.backlog.read_text(encoding="utf-8"))
    return {issue["id"] for issue in backlog.get("issues", [])}


def record_name(event: str) -> str:
    """item.answered -> ItemAnswered: the record name an event schema must use."""
    return "".join(part.capitalize() for part in re.split(r"[._]", event))


def highest_privacy(expanded: dict) -> str:
    labels = [f.get("privacy", "none") for _, f, _ in iter_fields(expanded)]
    return max(labels, key=PRIVACY_ORDER.index) if labels else "none"


def sensitive_paths(expanded: dict) -> list[str]:
    return [path for path, f, _ in iter_fields(expanded) if f.get("privacy") == "sensitive"]


def check_catalogue(catalogue: Catalogue, sources: Sources, paths: Paths) -> list[str]:
    """Every schema has an entry and every entry a schema; entries are complete and consistent."""
    problems = []
    raw = catalogue.raw
    if raw["compatibility"] not in LEVELS:
        problems.append(f"compatibility '{raw['compatibility']}' is not one of {', '.join(sorted(LEVELS))}")
    privacy = raw["privacy"]
    classes = privacy.get("classes", {})
    if list(classes) != PRIVACY_ORDER:
        problems.append(f"privacy.classes must define exactly {', '.join(PRIVACY_ORDER)}, in that order")
    for record in privacy.get("sensitive_records", []):
        if record not in sources.common:
            problems.append(f"privacy.sensitive_records: {record} is not a type in common/")

    schema_names, entry_names = set(sources.events), set(catalogue.events)
    for name in sorted(schema_names - entry_names):
        problems.append(f"{name}.avsc has no entry in catalogue.yaml")
    for name in sorted(entry_names - schema_names):
        problems.append(f"catalogue.yaml entry '{name}' has no schema file {name}.avsc")

    roles, tickets = known_roles(paths), known_tickets(paths)
    prefix = raw["topic_prefix"]
    envelope = sources.common.get("kuizi.events.common.Envelope", {"fields": []})
    nullable_envelope = {f["name"] for f in envelope["fields"] if isinstance(f["type"], list) and "null" in f["type"]}

    def check_tickets(where: str, values: Any) -> None:
        if not isinstance(values, list) or not values:
            problems.append(f"{where}: tickets must be a non-empty list")
            return
        for t in values:
            if not isinstance(t, str) or not TICKET.fullmatch(t):
                problems.append(f"{where}: '{t}' is not a ticket ID like T023")
            elif tickets is not None and t not in tickets:
                problems.append(f"{where}: ticket {t} is not in the backlog")

    def check_parties(where: str, parties: Any, required: bool) -> None:
        if not isinstance(parties, list) or (required and not parties):
            problems.append(f"{where}: must be a non-empty list")
            return
        for i, party in enumerate(parties):
            here = f"{where}[{i}]"
            if not isinstance(party, dict) or set(party) != {"service", "tickets", "uses"}:
                problems.append(f"{here}: needs exactly service, tickets and uses")
                continue
            check_tickets(here, party["tickets"])

    check_parties("consumers_of_every_event", raw.get("consumers_of_every_event", []), required=False)

    for name in sorted(entry_names & schema_names):
        event = catalogue.events[name]
        where = f"events.{name}"
        expanded = sources.expanded(name)
        if event.schema != f"{name}.avsc":
            problems.append(f"{where}.schema: expected {name}.avsc, found {event.schema}")
        if not re.fullmatch(rf"{re.escape(prefix)}\.{re.escape(name)}\.v[1-9]\d*", event.topic):
            problems.append(f"{where}.topic: expected {prefix}.{name}.v<major>, found {event.topic}")
        expected_record = record_name(name)
        if expanded.get("name") != expected_record or expanded.get("namespace") != "kuizi.events":
            problems.append(f"{name}.avsc: record must be kuizi.events.{expected_record}")
        if roles is not None and event.owner not in roles:
            problems.append(f"{where}.owner: '{event.owner}' is not an agent role in .claude/agents/")
        producer = event.producer
        if not isinstance(producer, dict) or set(producer) != {"service", "tickets", "origin"}:
            problems.append(f"{where}.producer: needs exactly service, tickets and origin")
        else:
            check_tickets(f"{where}.producer", producer["tickets"])
            if producer["origin"] not in ORIGINS:
                problems.append(f"{where}.producer.origin: must be app or server")
        check_parties(f"{where}.consumers", event.consumers, required=True)
        sensitive = sensitive_paths(expanded)
        if sensitive and not event.sensitive_readers:
            problems.append(f"{where}: has sensitive fields ({', '.join(sensitive)}) but no sensitive_readers")
        if event.sensitive_readers and not sensitive:
            problems.append(f"{where}: lists sensitive_readers but the schema has no sensitive field")
        if event.sensitive_readers:
            check_parties(f"{where}.sensitive_readers", event.sensitive_readers, required=True)
        retention = event.retention
        if not isinstance(retention, dict) or set(retention) != {"kafka_days", "warehouse_raw_months"}:
            problems.append(f"{where}.retention: needs exactly kafka_days and warehouse_raw_months")
        else:
            if not isinstance(retention["kafka_days"], int) or not 1 <= retention["kafka_days"] <= MAX_KAFKA_DAYS:
                problems.append(f"{where}.retention.kafka_days: must be 1 to {MAX_KAFKA_DAYS} (erasure deadline, T018)")
            months = retention["warehouse_raw_months"]
            if not isinstance(months, int) or not 1 <= months <= MAX_WAREHOUSE_MONTHS:
                problems.append(f"{where}.retention.warehouse_raw_months: must be 1 to {MAX_WAREHOUSE_MONTHS} (T018)")
        unknown = set(event.required_envelope) - nullable_envelope
        if unknown:
            problems.append(f"{where}.required_envelope: {', '.join(sorted(unknown))} are not nullable envelope fields")
        if isinstance(producer, dict) and producer.get("origin") == "app":
            missing = APP_ENVELOPE - set(event.required_envelope)
            if missing:
                problems.append(f"{where}.required_envelope: an app event must require {', '.join(sorted(missing))}")
        if not (paths.events / event.examples).is_file():
            problems.append(f"{where}.examples: {event.examples} does not exist")

    review = raw.get("ml_review")
    if review is not None and not (paths.root / str(review)).is_file():
        problems.append(f"ml_review: {review} does not exist")
    for i, feature in enumerate(catalogue.ml_features):
        where = f"ml_features[{i}]"
        if not isinstance(feature, dict) or set(feature) != {"feature", "models", "fields", "known", "notes"}:
            problems.append(f"{where}: needs exactly feature, models, fields, known and notes")
            continue
        if feature["known"] not in KNOWN:
            problems.append(f"{where} ({feature['feature']}): known must be one of {', '.join(sorted(KNOWN))}")
        for ref in feature["fields"]:
            event_name, _, path = str(ref).partition(":")
            if event_name not in sources.events:
                problems.append(f"{where} ({feature['feature']}): unknown event '{event_name}' in {ref}")
                continue
            try:
                find_field(sources.expanded(event_name), path)
            except KeyError as error:
                problems.append(f"{where} ({feature['feature']}): {event_name} {error}")
    return problems
