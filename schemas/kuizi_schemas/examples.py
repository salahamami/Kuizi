"""Synthetic example events: validation against the schemas and the rules Avro cannot express.

The rules here are the reference for ingestion (T025), which applies the same ones before an event
reaches Kafka, and for the synthetic data generator (T219).
"""

from __future__ import annotations

import datetime as dt
import io
import json
import math
import re
import uuid
from typing import Any

import fastavro
from fastavro.validation import ValidationError, validate

from . import Paths
from .avsc import (
    SchemaError,
    Sources,
    logical_type,
    named_types,
    parse_fastavro,
    resolve,
)
from .catalogue import Catalogue, Event

# Inclusive ranges for fields, by field name, wherever they appear.
RANGES: dict[str, tuple[float, float]] = {
    "confidence_1_5": (1, 5),
    "level": (1, 4),
    "max_hint_level": (1, 4),
    "hint_level": (1, 4),
    "score": (0.0, 1.0),
    "attempt": (1, 1_000),
    "session_seq": (1, 10_000_000),
    "time_multiplier": (1.0, 3.0),
    "rate": (0.25, 4.0),
}
ALLOWED_VALUES: dict[str, set] = {"planned_minutes": {15, 25, 45}}
NON_NEGATIVE = {
    "position",
    "items_answered",
    "hints_used",
    "attempts_before",
    "key_count",
    "sample_count",
    "length_chars",
    "template_version",
    "item_version",
    "decision_ms",
    "first_token_ms",
}
MAX_LENGTH = {"expression": 500}  # typed answers stay short; longer input is rejected at ingestion (T025)
HESITATION_MIN_MS = 3_000
EARLIEST_TS = int(dt.datetime(2026, 1, 1, tzinfo=dt.UTC).timestamp() * 1000)
LATEST_TS = int(dt.datetime(2100, 1, 1, tzinfo=dt.UTC).timestamp() * 1000)

# Values that look like real personal data must never appear in fixtures (T219 rule).
LOOKS_REAL = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "an email address"),
    (re.compile(r"(?<!\w)(\+|00)216[\s.-]?\d{2}[\s.-]?\d{3}[\s.-]?\d{3}(?!\w)"), "a Tunisian phone number"),
    (re.compile(r"(?<![\w-])\d{8}(?![\w-])"), "an 8-digit national ID (CIN) or phone number"),
]


def load_examples(paths: Paths, event: Event) -> list[dict]:
    data = json.loads((paths.events / event.examples).read_text(encoding="utf-8"))
    return data if isinstance(data, list) else [data]


def semantic_problems(record: dict, expanded: dict, event: Event) -> list[str]:
    """Problems Avro cannot see: identifiers, ranges, required envelope fields, realistic-looking data."""
    problems: list[str] = []
    types = named_types(expanded)

    def walk(value: Any, schema: Any, path: str) -> None:
        schema = resolve(schema, types)
        if isinstance(schema, list):  # every union here is ["null", T]: follow T
            if value is None:
                return
            for branch in schema:
                if branch == "null":
                    continue
                walk(value, branch, path)
                return
            return
        if isinstance(schema, dict) and schema.get("type") == "record":
            for f in schema["fields"]:
                if isinstance(value, dict) and f["name"] in value:
                    walk(value[f["name"]], f["type"], f"{path}.{f['name']}".lstrip("."))
            return
        if isinstance(schema, dict) and schema.get("type") == "array":
            for i, item in enumerate(value or []):
                walk(item, schema["items"], f"{path}[{i}]")
            return
        if isinstance(schema, dict) and schema.get("type") == "map":
            for k, item in (value or {}).items():
                walk(item, schema["values"], f"{path}[{k}]")
            return
        name = path.rsplit(".", 1)[-1]
        logical = logical_type(schema)
        if logical == "uuid":
            try:
                uuid.UUID(str(value))
            except ValueError:
                problems.append(f"{path}: '{value}' is not a UUID")
            return
        if logical == "timestamp-millis" and isinstance(value, int) and not EARLIEST_TS <= value < LATEST_TS:
            problems.append(f"{path}: {value} is not a plausible UTC timestamp in milliseconds")
        if isinstance(value, str):
            if name in MAX_LENGTH and len(value) > MAX_LENGTH[name]:
                problems.append(f"{path}: longer than {MAX_LENGTH[name]} characters")
            for pattern, what in LOOKS_REAL:
                if pattern.search(value):
                    problems.append(f"{path}: '{value}' looks like {what}; fixtures must be synthetic")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return
        if name in RANGES:
            low, high = RANGES[name]
            if not low <= value <= high:
                problems.append(f"{path}: {value} is outside {low} to {high}")
        if name in ALLOWED_VALUES and value not in ALLOWED_VALUES[name]:
            problems.append(f"{path}: {value} is not one of {sorted(ALLOWED_VALUES[name])}")
        if (name.endswith("_ms") or name in NON_NEGATIVE) and value < 0:
            problems.append(f"{path}: must not be negative")

    walk(record, expanded, "")
    envelope = record.get("envelope", {})
    for name in event.required_envelope:
        if envelope.get(name) is None:
            problems.append(f"envelope.{name}: required for {event.name} (catalogue required_envelope)")
    item = record.get("item")
    if isinstance(item, dict) and not item.get("kc_ids"):
        problems.append("item.kc_ids: at least one knowledge component is required")
    if event.name == "item.hesitation" and record.get("idle_ms", HESITATION_MIN_MS + 1) <= HESITATION_MIN_MS:
        problems.append(f"idle_ms: a hesitation is longer than {HESITATION_MIN_MS} ms")
    if event.name == "item.answered" and "correct" in record and "score" in record:
        if record["correct"] and record["score"] != 1.0:
            problems.append("score: a correct answer earns full credit (1.0)")
        if not record["correct"] and record["score"] >= 1.0:
            problems.append("score: an incorrect answer cannot earn full credit")
    return problems


def check_record(record: dict, expanded: dict, parsed: dict, event: Event) -> list[str]:
    """All problems of one event record: Avro types, unknown or missing fields, then semantic rules."""
    if not isinstance(record, dict):
        return ["an event must be a JSON object"]
    try:
        validate(record, parsed, raise_errors=True)
    except ValidationError as error:
        return [f"does not match the schema: {' '.join(str(error).split())}"]
    try:
        fastavro.schemaless_writer(io.BytesIO(), parsed, record, strict_allow_default=True)
    except (ValueError, TypeError) as error:
        return [f"cannot be serialised: {error}"]
    return semantic_problems(record, expanded, event)


def check_all_examples(catalogue: Catalogue, sources: Sources, paths: Paths) -> list[str]:
    problems = []
    for name, event in sorted(catalogue.events.items()):
        if name not in sources.events or not (paths.events / event.examples).is_file():
            continue  # reported by the catalogue check
        try:
            expanded = sources.expanded(name)
            parsed = parse_fastavro(expanded)
        except SchemaError:
            continue  # reported by the lint
        try:
            records = load_examples(paths, event)
        except json.JSONDecodeError as error:
            problems.append(f"{event.examples}: invalid JSON ({error})")
            continue
        if not records:
            problems.append(f"{event.examples}: holds no example")
        for i, record in enumerate(records):
            problems += [f"{event.examples}[{i}]: {p}" for p in check_record(record, expanded, parsed, event)]
    return problems


# ---------------------------------------------------------------------------
# Serialisation helpers shared by the tests and the registry round trip
# ---------------------------------------------------------------------------


def to_avro_binary(parsed: dict, record: dict) -> bytes:
    out = io.BytesIO()
    fastavro.schemaless_writer(out, parsed, record)
    return out.getvalue()


def from_avro_binary(parsed: dict, data: bytes) -> dict:
    return fastavro.schemaless_reader(io.BytesIO(data), parsed, None)


def normalise(value: Any) -> Any:
    """fastavro returns datetimes and UUID objects; turn them back into JSON values."""
    if isinstance(value, dict):
        return {k: normalise(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normalise(v) for v in value]
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, dt.datetime):
        return round(value.timestamp() * 1000)
    return value


def contains(expected: Any, actual: Any) -> bool:
    """True when every value in `expected` is in `actual` (defaults may add fields to `actual`)."""
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(k in actual and contains(v, actual[k]) for k, v in expected.items())
    if isinstance(expected, list):
        return (
            isinstance(actual, list)
            and len(expected) == len(actual)
            and all(contains(e, a) for e, a in zip(expected, actual, strict=True))
        )
    if isinstance(expected, float) or isinstance(actual, float):
        return isinstance(actual, (int, float)) and math.isclose(expected, actual, rel_tol=1e-9)
    return expected == actual
