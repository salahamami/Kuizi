"""The schema-registry wire format used by Kafka clients (Confluent framing, also used by Redpanda).

Each message value is: magic byte 0, the 4-byte big-endian schema ID from the registry, then the
Avro binary encoding of the record. Consumers read the ID, fetch the writer schema from the
registry and decode with it, which is why every subject must stay readable (BACKWARD_TRANSITIVE).
"""

from __future__ import annotations

import struct
from collections.abc import Callable

from .examples import from_avro_binary, to_avro_binary

MAGIC = 0
HEADER = struct.Struct(">bI")


class WireFormatError(ValueError):
    """The bytes do not start with the registry framing."""


def encode(schema_id: int, parsed: dict, record: dict) -> bytes:
    return HEADER.pack(MAGIC, schema_id) + to_avro_binary(parsed, record)


def decode(data: bytes, parsed_for_id: Callable[[int], dict]) -> tuple[int, dict]:
    """Return (schema ID, record); `parsed_for_id` fetches and parses the writer schema."""
    if len(data) < HEADER.size:
        raise WireFormatError("message shorter than the 5-byte header")
    magic, schema_id = HEADER.unpack_from(data)
    if magic != MAGIC:
        raise WireFormatError(f"unknown magic byte {magic}")
    return schema_id, from_avro_binary(parsed_for_id(schema_id), data[HEADER.size :])
