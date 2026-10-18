"""Synthetic examples are valid, cover the edge cases and round-trip through Avro binary."""

from __future__ import annotations

import copy

import pytest

from kuizi_schemas.avsc import parse_fastavro
from kuizi_schemas.examples import (
    check_all_examples,
    check_record,
    contains,
    from_avro_binary,
    load_examples,
    normalise,
    to_avro_binary,
)


def examples_of(paths, catalogue, event):
    return load_examples(paths, catalogue.events[event])


def test_all_examples_are_valid(catalogue, sources, paths):
    assert check_all_examples(catalogue, sources, paths) == []


@pytest.mark.parametrize(
    "event",
    [
        "focus.end",
        "focus.start",
        "hint.requested",
        "hint.shown",
        "item.answered",
        "item.hesitation",
        "item.interaction",
        "item.presented",
        "notification.decided",
        "notification.opened",
        "notification.sent",
        "session.end",
        "session.start",
        "tts.played",
        "tutor.message",
    ],
)
def test_examples_round_trip_through_avro_binary(catalogue, sources, paths, event):
    parsed = parse_fastavro(sources.expanded(event))
    records = examples_of(paths, catalogue, event)
    assert records
    for record in records:
        data = to_avro_binary(parsed, record)
        decoded = normalise(from_avro_binary(parsed, data))
        assert contains(record, decoded)
        assert to_avro_binary(parsed, decoded) == data  # decoding then encoding gives the same bytes


def test_examples_cover_the_edge_cases(catalogue, paths):
    answered = examples_of(paths, catalogue, "item.answered")
    with_accommodation = [r for r in answered if r.get("accommodation")]
    assert with_accommodation and any(r.get("accommodation") is None for r in answered)
    assert any(
        r["accommodation"]["time_multiplier"] > 1 and "SCREEN_READER" in r["accommodation"]["assistive_modes"]
        for r in with_accommodation
    )
    assert any(0 < r["score"] < 1 for r in answered), "partial credit"
    assert any(r["attempt"] > 1 and r["hints_used"] > 0 for r in answered), "second attempt after a hint"
    assert {r["response"]["kind"] for r in answered} >= {"CHOICE", "NUMERIC", "EXPRESSION"}
    assert any(r["item"]["item_language"] == "AR" for r in answered)
    for event in ("notification.decided", "notification.sent"):
        for record in examples_of(paths, catalogue, event):
            assert record["envelope"]["client_ts"] is None, "server events leave client fields empty"
    assert {r["role"] for r in examples_of(paths, catalogue, "tutor.message")} == {"STUDENT", "TUTOR"}
    kinds = {r["kind"] for r in examples_of(paths, catalogue, "item.interaction")}
    assert {"SLIDER_MOVE", "KEYSTROKE_BURST"} <= kinds


def broken(record, path, value):
    record = copy.deepcopy(record)
    target = record
    *parents, last = path.split(".")
    for part in parents:
        target = target[part]
    if value is KeyError:
        del target[last]
    else:
        target[last] = value
    return record


@pytest.mark.parametrize(
    ("path", "value", "message"),
    [
        ("envelope.student_id", "firstname.lastname", "is not a UUID"),
        ("envelope.tenant_id", "parent: someone@example.com", "looks like an email address"),
        ("envelope.tenant_id", "school 12345678", "8-digit national ID"),
        ("envelope.tenant_id", "call +216 98 123 456", "Tunisian phone number"),
        ("envelope.client_ts", 1793718000, "not a plausible UTC timestamp in milliseconds"),
        ("envelope.session_id", None, "envelope.session_id: required"),
        ("item.kc_ids", [], "at least one knowledge component"),
        ("confidence_1_5", 6, "outside 1 to 5"),
        ("score", 0.5, "a correct answer earns full credit"),
        ("max_hint_level", 7, "outside 1 to 4"),
        ("latency_ms", -5, "must not be negative"),
        ("correct", "yes", "does not match the schema"),
        ("raw_keys", ["a", "b"], "more fields than the schema specifies"),
        ("attempt", KeyError, "ItemAnswered.attempt) is None expected int"),
    ],
)
def test_rules_reject_bad_events(catalogue, sources, paths, path, value, message):
    event = catalogue.events["item.answered"]
    expanded = sources.expanded("item.answered")
    good = next(r for r in examples_of(paths, catalogue, "item.answered") if r["correct"])
    problems = check_record(broken(good, path, value), expanded, parse_fastavro(expanded), event)
    assert any(message in p for p in problems), problems


def test_rules_for_other_events(catalogue, sources, paths):
    for event_name, path, value, message in [
        ("item.hesitation", "idle_ms", 2_000, "a hesitation is longer than 3000 ms"),
        ("focus.start", "planned_minutes", 30, "is not one of [15, 25, 45]"),
        ("item.presented", "accommodation", {"time_multiplier": 5.0}, "outside 1.0 to 3.0"),
        ("item.answered", "response", {"kind": "EXPRESSION", "expression": "x" * 501}, "longer than 500 characters"),
    ]:
        event = catalogue.events[event_name]
        expanded = sources.expanded(event_name)
        record = examples_of(paths, catalogue, event_name)[0]
        problems = check_record(broken(record, path, value), expanded, parse_fastavro(expanded), event)
        assert any(message in p for p in problems), (event_name, problems)


def test_contains_compares_numbers_loosely_and_lists_strictly():
    assert contains({"a": 1.0, "b": [1, 2]}, {"a": 1.0000000000001, "b": [1, 2], "c": 3})
    assert not contains({"b": [1, 2]}, {"b": [1, 2, 3]})
    assert not contains({"a": 1}, {})
