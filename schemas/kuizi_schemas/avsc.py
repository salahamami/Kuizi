"""Load the Avro sources and expand each event into a self-contained schema.

Shared types live once in common/<fullname>.avsc and are referenced by full name. The registry and
every client need one complete schema per subject, so expand() inlines each shared type at its
first use and leaves later uses as name references, as the Avro specification requires.
"""

from __future__ import annotations

import copy
import json
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import avro.errors
import avro.schema
import fastavro
import fastavro.schema

PRIMITIVES = {"null", "boolean", "int", "long", "float", "double", "bytes", "string"}
NAMED = {"record", "enum", "fixed"}


class SchemaError(Exception):
    """A schema source is invalid; the message names the file and the problem."""


def fullname(name: str, namespace: str | None) -> str:
    if "." in name:
        return name
    return f"{namespace}.{name}" if namespace else name


def namespace_of(node: dict, enclosing: str | None) -> str | None:
    """Namespace that applies inside a named type, following the Avro rules."""
    name = node["name"]
    if "." in name:
        return name.rsplit(".", 1)[0]
    return node.get("namespace", enclosing)


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise SchemaError(f"{path.name}: invalid JSON ({error})") from None


@dataclass
class Sources:
    """The raw schema files of one schemas/events folder."""

    common: dict[str, dict]  # full name -> definition
    common_files: dict[str, Path]
    events: dict[str, dict]  # event name (file stem) -> record definition
    event_files: dict[str, Path]

    def expanded(self, event: str) -> dict:
        return expand(self.events[event], self.common)

    def all_expanded(self) -> dict[str, dict]:
        return {name: self.expanded(name) for name in self.events}


def load_sources(events_dir: Path) -> Sources:
    common, common_files = {}, {}
    for path in sorted((events_dir / "common").glob("*.avsc")):
        schema = read_json(path)
        if not isinstance(schema, dict) or schema.get("type") not in NAMED:
            raise SchemaError(f"common/{path.name}: must hold one named type (record, enum or fixed)")
        name = fullname(schema["name"], schema.get("namespace"))
        if path.stem != name:
            raise SchemaError(f"common/{path.name}: defines {name}; the file must be named {name}.avsc")
        common[name] = schema
        common_files[name] = path
    events, event_files = {}, {}
    for path in sorted(events_dir.glob("*.avsc")):
        schema = read_json(path)
        if not isinstance(schema, dict) or schema.get("type") != "record":
            raise SchemaError(f"{path.name}: an event schema must be one record")
        events[path.stem] = schema
        event_files[path.stem] = path
    if not events:
        raise SchemaError(f"no event schemas found in {events_dir}")
    return Sources(common, common_files, events, event_files)


def expand(schema: dict, common: dict[str, dict]) -> dict:
    """Return `schema` with every shared type inlined at its first use."""
    defined: set[str] = set()

    def walk(node: Any, namespace: str | None) -> Any:
        if isinstance(node, str):
            if node in PRIMITIVES:
                return node
            name = fullname(node, namespace)
            if name in defined:
                return name
            if name in common:
                return walk(copy.deepcopy(common[name]), namespace)
            raise SchemaError(f"unknown type {node!r}")
        if isinstance(node, list):
            return [walk(branch, namespace) for branch in node]
        if not isinstance(node, dict):
            raise SchemaError(f"unexpected schema node {node!r}")
        kind = node.get("type")
        if kind in NAMED:
            inner = namespace_of(node, namespace)
            name = fullname(node["name"], inner)
            if name in defined:
                raise SchemaError(f"type {name} is defined twice")
            defined.add(name)
            out = dict(node)
            if kind == "record":
                out["fields"] = [{**f, "type": walk(f["type"], inner)} for f in node.get("fields", [])]
            return out
        if kind == "array":
            return {**node, "items": walk(node["items"], namespace)}
        if kind == "map":
            return {**node, "values": walk(node["values"], namespace)}
        if isinstance(kind, (dict, list)):
            return {**node, "type": walk(kind, namespace)}
        return dict(node)  # a primitive, possibly with a logical type

    return walk(schema, None)


def parse_fastavro(expanded: dict) -> dict:
    """Parsed schema for fastavro reading and writing; raises SchemaError when invalid."""
    try:
        return fastavro.parse_schema(copy.deepcopy(expanded))
    except (
        fastavro.schema.SchemaParseException,
        fastavro.schema.UnknownType,
        ValueError,
        TypeError,
        KeyError,
    ) as error:
        raise SchemaError(f"fastavro rejects the schema: {error}") from None


def parse_avro(expanded: dict) -> avro.schema.Schema:
    """Parsed schema for the Apache Avro compatibility checker; raises SchemaError when invalid."""
    try:
        return avro.schema.parse(json.dumps(expanded))
    except (avro.errors.AvroException, ValueError, TypeError, KeyError) as error:
        raise SchemaError(f"Apache Avro rejects the schema: {error}") from None


def to_registry_string(expanded: dict) -> str:
    """The exact schema text registered: stable, so re-registering an unchanged schema is a no-op."""
    return json.dumps(expanded, ensure_ascii=False, separators=(",", ":"))


def canonical(expanded: dict) -> str:
    """Key used to tell two versions apart (docs and privacy labels included)."""
    return json.dumps(expanded, sort_keys=True, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Navigating schemas
# ---------------------------------------------------------------------------


def named_types(schema: Any, namespace: str | None = None, found: dict | None = None) -> dict[str, dict]:
    """Every named type defined inside `schema`, by full name."""
    found = {} if found is None else found
    if isinstance(schema, list):
        for branch in schema:
            named_types(branch, namespace, found)
    elif isinstance(schema, dict):
        kind = schema.get("type")
        if kind in NAMED:
            inner = namespace_of(schema, namespace)
            found[fullname(schema["name"], inner)] = schema
            for f in schema.get("fields", []):
                named_types(f["type"], inner, found)
        elif kind == "array":
            named_types(schema["items"], namespace, found)
        elif kind == "map":
            named_types(schema["values"], namespace, found)
        elif isinstance(kind, (dict, list)):
            named_types(kind, namespace, found)
    return found


def branches(field_type: Any) -> list:
    """The non-null branches of a field type (the type itself when it is not a union)."""
    if isinstance(field_type, list):
        return [b for b in field_type if b != "null"]
    return [field_type]


def resolve(node: Any, types: dict[str, dict]) -> Any:
    """Follow a name reference to its definition."""
    if isinstance(node, str) and node in types:
        return types[node]
    return node


def record_of(field_type: Any, types: dict[str, dict]) -> dict | None:
    """The record a field holds directly or through a nullable union, if any."""
    for branch in branches(field_type):
        branch = resolve(branch, types)
        if isinstance(branch, dict) and branch.get("type") == "record":
            return branch
    return None


def find_field(expanded: dict, path: str) -> dict:
    """The field at a dotted path such as 'envelope.student_id'; raises KeyError when absent."""
    types = named_types(expanded)
    record: dict | None = expanded
    field: dict | None = None
    for part in path.split("."):
        if record is None:
            raise KeyError(f"{path}: '{part}' is below a field that is not a record")
        field = next((f for f in record["fields"] if f["name"] == part), None)
        if field is None:
            raise KeyError(f"{path}: no field '{part}' in {record['name']}")
        record = record_of(field["type"], types)
    assert field is not None
    return field


def iter_fields(schema: Any, path: str = "", namespace: str | None = None) -> Iterator[tuple[str, dict, dict]]:
    """Yield (dotted path, field, owning record) for every field defined in `schema`.

    Only definitions are visited: a name reference is not followed, so each field is seen once.
    """
    if isinstance(schema, list):
        for branch in schema:
            yield from iter_fields(branch, path, namespace)
    elif isinstance(schema, dict):
        kind = schema.get("type")
        if kind == "record":
            inner = namespace_of(schema, namespace)
            for f in schema.get("fields", []):
                here = f"{path}.{f['name']}" if path else f["name"]
                yield here, f, schema
                yield from iter_fields(f["type"], here, inner)
        elif kind == "array":
            yield from iter_fields(schema["items"], path, namespace)
        elif kind == "map":
            yield from iter_fields(schema["values"], path, namespace)
        elif isinstance(kind, (dict, list)):
            yield from iter_fields(kind, path, namespace)


def iter_named(schema: Any, namespace: str | None = None) -> Iterator[tuple[str, dict]]:
    """Yield (full name, definition) for every named type defined in `schema`."""
    yield from named_types(schema, namespace).items()


def logical_type(field_type: Any) -> str | None:
    for branch in branches(field_type):
        if isinstance(branch, dict) and "logicalType" in branch:
            return branch["logicalType"]
    return None
