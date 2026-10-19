"""The schemas parse, expand correctly and follow the house rules; the rules catch violations."""

from __future__ import annotations

import json

import pytest

from kuizi_schemas import cli
from kuizi_schemas.avsc import (
    SchemaError,
    expand,
    find_field,
    load_sources,
    named_types,
    parse_avro,
    parse_fastavro,
    to_registry_string,
)
from kuizi_schemas.lint import lint_all

TICKET_EVENTS = {
    "item.presented",
    "item.interaction",
    "item.hesitation",
    "item.answered",
    "hint.requested",
    "hint.shown",
    "tutor.message",
    "session.start",
    "session.end",
}
V2_EVENTS = {
    "focus.start",
    "focus.end",
    "notification.decided",
    "notification.sent",
    "notification.opened",
    "tts.played",
}
TICKET_ENVELOPE = ["student_id", "tenant_id", "client_ts", "server_ts", "session_id", "device", "app_version"]
V2_ENVELOPE = ["focus_session_id", "input_modality"]


def test_whole_repository_passes_the_check(capsys):
    assert cli.main(["check"]) == 0, capsys.readouterr().out


def test_every_event_the_ticket_names_has_a_schema(sources):
    assert set(sources.events) >= TICKET_EVENTS | V2_EVENTS


def test_every_event_carries_the_ticket_fields(sources):
    for name in sources.events:
        expanded = sources.expanded(name)
        for field in TICKET_ENVELOPE + V2_ENVELOPE:
            find_field(expanded, f"envelope.{field}")


def test_item_events_carry_item_and_concepts(sources):
    for name in ("item.presented", "item.interaction", "item.hesitation", "item.answered", "hint.requested"):
        expanded = sources.expanded(name)
        find_field(expanded, "item.item_id")
        find_field(expanded, "item.kc_ids")


def test_learning_events_carry_accommodation(sources):
    for name in ("item.presented", "item.answered"):
        expanded = sources.expanded(name)
        for field in ("time_multiplier", "untimed", "assistive_modes"):
            assert find_field(expanded, f"accommodation.{field}")["privacy"] == "sensitive"


def test_item_answered_has_the_ticket_fields(sources):
    expanded = sources.expanded("item.answered")
    for field in ("response", "correct", "latency_ms", "confidence_1_5", "attempt"):
        find_field(expanded, field)


@pytest.mark.parametrize("event", sorted(TICKET_EVENTS | V2_EVENTS))
def test_schema_parses_in_both_libraries(sources, event):
    expanded = sources.expanded(event)
    parse_fastavro(expanded)
    parse_avro(expanded)
    assert json.loads(to_registry_string(expanded)) == expanded


def test_expansion_defines_each_shared_type_once(sources):
    text = to_registry_string(sources.expanded("tutor.message"))
    # Language is used by the envelope, the item context and the message itself: defined once.
    assert text.count('"name":"Language"') == 1
    assert "kuizi.events.common.Language" in text


def test_expand_rejects_unknown_types(sources):
    schema = {"type": "record", "name": "X", "namespace": "kuizi.events", "fields": [{"name": "a", "type": "Nope"}]}
    with pytest.raises(SchemaError, match="unknown type"):
        expand(schema, sources.common)


def test_shared_file_must_be_named_after_its_type(tmp_path):
    (tmp_path / "common").mkdir()
    (tmp_path / "common" / "wrong.avsc").write_text(
        json.dumps({"type": "enum", "name": "E", "namespace": "kuizi.events.common", "symbols": ["UNKNOWN"]})
    )
    with pytest.raises(SchemaError, match="must be named"):
        load_sources(tmp_path)


def test_named_types_finds_inline_records(sources):
    types = named_types(sources.expanded("item.answered"))
    assert "kuizi.events.Response" in types
    assert "kuizi.events.common.AccommodationContext" in types


def test_house_rules_hold(sources, catalogue):
    assert lint_all(sources, catalogue) == []


def first_field(sources, event, name):
    return next(f for f in sources.events[event]["fields"] if f["name"] == name)


def test_lint_rejects_a_field_without_privacy_label(sources, catalogue):
    del first_field(sources, "item.answered", "latency_ms")["privacy"]
    assert any('latency_ms needs "privacy"' in p for p in lint_all(sources, catalogue))


def test_lint_rejects_a_field_without_doc(sources, catalogue):
    first_field(sources, "session.end", "duration_ms")["doc"] = " "
    assert any("duration_ms has no doc" in p for p in lint_all(sources, catalogue))


@pytest.mark.parametrize("name", ["email", "phone", "national_id", "ip_address", "key_code", "text", "name"])
def test_lint_rejects_field_names_that_invite_personal_data(sources, catalogue, name):
    sources.events["session.start"]["fields"].append(
        {"name": name, "type": ["null", "string"], "default": None, "privacy": "personal", "doc": "x"}
    )
    assert any(f"the name '{name}' is forbidden" in p for p in lint_all(sources, catalogue))


def test_lint_rejects_a_sensitive_field_outside_the_accommodation_record(sources, catalogue):
    sources.events["session.start"]["fields"].append(
        {"name": "dyslexia", "type": "boolean", "default": False, "privacy": "sensitive", "doc": "x"}
    )
    assert any("dyslexia is sensitive but sits outside" in p for p in lint_all(sources, catalogue))


def test_lint_rejects_a_label_lower_than_the_record_it_holds(sources, catalogue):
    first_field(sources, "item.answered", "accommodation")["privacy"] = "personal"
    assert any("labelled personal but holds sensitive" in p for p in lint_all(sources, catalogue))


def test_lint_rejects_an_enum_that_cannot_grow(sources, catalogue):
    enum = first_field(sources, "session.end", "reason")["type"]
    del enum["default"]
    assert any("must start with UNKNOWN" in p for p in lint_all(sources, catalogue))


def test_lint_rejects_an_optional_field_without_null_default(sources, catalogue):
    first_field(sources, "item.answered", "active_ms")["default"] = 0
    assert any("active_ms: an optional field" in p for p in lint_all(sources, catalogue))


def test_lint_rejects_an_event_without_envelope_first(sources, catalogue):
    fields = sources.events["session.end"]["fields"]
    fields.append(fields.pop(0))
    assert any("first field must be 'envelope'" in p for p in lint_all(sources, catalogue))


def test_lint_rejects_bad_names(sources, catalogue):
    first_field(sources, "session.end", "items_answered")["name"] = "itemsAnswered"
    first_field(sources, "session.end", "reason")["type"]["symbols"].append("lower")
    problems = lint_all(sources, catalogue)
    assert any("itemsAnswered must be snake_case" in p for p in problems)
    assert any("UPPER_SNAKE_CASE" in p for p in problems)


def test_lint_reports_a_schema_avro_rejects(sources, catalogue):
    first_field(sources, "session.end", "items_answered")["default"] = "zero"
    assert any("session.end.avsc" in p and "rejects" in p for p in lint_all(sources, catalogue))
