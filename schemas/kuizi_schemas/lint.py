"""House rules for the schemas, on top of what Avro itself checks.

Each rule keeps the contracts safe to evolve (defaults everywhere they will be needed) or safe for
learners (privacy labels, no field that invites personal data).
"""

from __future__ import annotations

import re
from typing import Any

from .avsc import (
    SchemaError,
    Sources,
    iter_fields,
    iter_named,
    named_types,
    parse_avro,
    parse_fastavro,
    record_of,
)
from .catalogue import PRIVACY_ORDER, Catalogue

FIELD_NAME = re.compile(r"[a-z][a-z0-9]*(_[a-z0-9]+)*")
SYMBOL = re.compile(r"[A-Z][A-Z0-9]*(_[A-Z0-9]+)*")
TYPE_NAME = re.compile(r"[A-Z][A-Za-z0-9]*")
ENVELOPE = "kuizi.events.common.Envelope"


def lint_definitions(label: str, schema: Any, catalogue: Catalogue) -> list[str]:
    """Rules for every named type and field defined in one source file."""
    problems = []
    for name, definition in iter_named(schema):
        short = name.rsplit(".", 1)[-1]
        if not TYPE_NAME.fullmatch(short):
            problems.append(f"{label}: type {name} must be PascalCase")
        if not str(definition.get("doc", "")).strip():
            problems.append(f"{label}: type {name} has no doc")
        if definition["type"] == "enum":
            symbols = definition.get("symbols", [])
            bad = [s for s in symbols if not SYMBOL.fullmatch(s)]
            if bad:
                problems.append(f"{label}: enum {name} symbols must be UPPER_SNAKE_CASE: {', '.join(bad)}")
            if not symbols or symbols[0] != "UNKNOWN" or definition.get("default") != "UNKNOWN":
                problems.append(
                    f'{label}: enum {name} must start with UNKNOWN and declare "default": "UNKNOWN"'
                    " so it can grow without breaking older readers"
                )
    for path, f, _owner in iter_fields(schema):
        where = f"{label}: field {path}"
        if not FIELD_NAME.fullmatch(f["name"]):
            problems.append(f"{where} must be snake_case")
        if f["name"] in catalogue.forbidden_names:
            problems.append(
                f"{where}: the name '{f['name']}' is forbidden (direct identifier, location, free text or"
                " keystrokes); adding it needs the product owner and the DPO"
            )
        if not str(f.get("doc", "")).strip():
            problems.append(f"{where} has no doc")
        if f.get("privacy") not in PRIVACY_ORDER:
            problems.append(f'{where} needs "privacy": one of {", ".join(PRIVACY_ORDER)}')
        field_type = f["type"]
        if isinstance(field_type, list):
            if "null" in field_type:
                if field_type[0] != "null" or f.get("default", "missing") is not None:
                    problems.append(f'{where}: an optional field is ["null", ...] with "default": null')
            elif "default" not in f:
                problems.append(f"{where}: a union field needs a default")
    return problems


def lint_event(name: str, source: dict, expanded: dict, catalogue: Catalogue) -> list[str]:
    """Rules that need the whole event schema."""
    problems = []
    fields = source.get("fields", [])
    if not fields or fields[0]["name"] != "envelope" or fields[0]["type"] != ENVELOPE:
        problems.append(f"{name}.avsc: the first field must be 'envelope' of type {ENVELOPE}")
    types = named_types(expanded)
    allowed = set(catalogue.sensitive_records)
    for path, f, owner in iter_fields(expanded):
        label = f.get("privacy")
        if label not in PRIVACY_ORDER:
            continue  # reported by lint_definitions
        owner_name = f"{owner.get('namespace', '')}.{owner['name']}".lstrip(".")
        inner = record_of(f["type"], types)
        holds_allowed = inner is not None and f"{inner.get('namespace', '')}.{inner['name']}" in allowed
        if label == "sensitive" and owner_name not in allowed and not holds_allowed:
            problems.append(
                f"{name}.avsc: field {path} is sensitive but sits outside the records allowed to hold"
                f" sensitive data ({', '.join(sorted(allowed))}); this needs the product owner and the DPO"
            )
        if inner is not None:
            nested = [g.get("privacy", "none") for g in inner["fields"] if g.get("privacy") in PRIVACY_ORDER]
            if nested:
                top = max(nested, key=PRIVACY_ORDER.index)
                if PRIVACY_ORDER.index(label) < PRIVACY_ORDER.index(top):
                    problems.append(f"{name}.avsc: field {path} is labelled {label} but holds {top} fields")
    return problems


def lint_all(sources: Sources, catalogue: Catalogue) -> list[str]:
    problems = []
    for name, schema in sources.common.items():
        problems += lint_definitions(f"common/{name}.avsc", schema, catalogue)
    for name, schema in sources.events.items():
        problems += lint_definitions(f"{name}.avsc", schema, catalogue)
        try:
            expanded = sources.expanded(name)
            parse_fastavro(expanded)
            parse_avro(expanded)
        except SchemaError as error:
            problems.append(f"{name}.avsc: {error}")
            continue
        problems += lint_event(name, schema, expanded, catalogue)
    return problems
