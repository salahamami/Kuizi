"""The data catalogue and the schemas agree both ways, and the generated page is current."""

from __future__ import annotations

import copy

import pytest
import yaml

from kuizi_schemas import Paths
from kuizi_schemas.catalogue import CatalogueError, check_catalogue, highest_privacy, load_catalogue, record_name
from kuizi_schemas.docs import doc_is_current, render


def test_catalogue_matches_the_schemas(catalogue, sources, paths):
    assert check_catalogue(catalogue, sources, paths) == []


def test_every_event_has_owner_producer_and_consumers(catalogue):
    for name, event in catalogue.events.items():
        assert event.owner, name
        assert event.producer["service"] and event.producer["tickets"], name
        assert event.consumers, name


def test_a_schema_without_entry_is_reported(catalogue, sources, paths):
    sources.events["item.skipped"] = copy.deepcopy(sources.events["session.end"])
    assert "item.skipped.avsc has no entry in catalogue.yaml" in check_catalogue(catalogue, sources, paths)


def test_an_entry_without_schema_is_reported(catalogue, sources, paths):
    del sources.events["tts.played"]
    assert "catalogue.yaml entry 'tts.played' has no schema file tts.played.avsc" in check_catalogue(
        catalogue, sources, paths
    )


def test_unknown_role_and_ticket_are_reported(catalogue, sources, paths):
    event = catalogue.events["session.start"]
    event.owner = "astronaut"
    event.consumers[0]["tickets"] = ["T999"]
    problems = check_catalogue(catalogue, sources, paths)
    assert any("'astronaut' is not an agent role" in p for p in problems)
    assert any("ticket T999 is not in the backlog" in p for p in problems)


def test_topic_must_follow_the_convention(catalogue, sources, paths):
    catalogue.events["session.start"].topic = "sessions"
    assert any("expected learner.session.start.v<major>" in p for p in check_catalogue(catalogue, sources, paths))


def test_sensitive_events_must_name_their_readers(catalogue, sources, paths):
    catalogue.events["item.answered"].sensitive_readers = []
    catalogue.events["session.end"].sensitive_readers = [{"service": "x", "tickets": ["T026"], "uses": "y"}]
    problems = check_catalogue(catalogue, sources, paths)
    assert any("item.answered: has sensitive fields" in p for p in problems)
    assert any("session.end: lists sensitive_readers" in p for p in problems)


def test_retention_is_bounded_by_the_erasure_rules(catalogue, sources, paths):
    catalogue.events["item.interaction"].retention = {"kafka_days": 90, "warehouse_raw_months": 36}
    problems = check_catalogue(catalogue, sources, paths)
    assert any("kafka_days: must be 1 to 30" in p for p in problems)
    assert any("warehouse_raw_months: must be 1 to 24" in p for p in problems)


def test_app_events_must_require_client_fields(catalogue, sources, paths):
    catalogue.events["session.start"].required_envelope = ["session_id"]
    assert any("an app event must require" in p for p in check_catalogue(catalogue, sources, paths))


def test_ml_feature_paths_are_verified(catalogue, sources, paths):
    catalogue.raw["ml_features"][0]["fields"].append("item.answered:envelope.student_name")
    catalogue.raw["ml_features"][1]["fields"].append("item.nope:item_id")
    problems = check_catalogue(catalogue, sources, paths)
    assert any("no field 'student_name'" in p for p in problems)
    assert any("unknown event 'item.nope'" in p for p in problems)


def test_ml_mapping_covers_what_knowledge_tracing_needs(catalogue):
    refs = {ref for feature in catalogue.ml_features for ref in feature["fields"]}
    for needed in (
        "item.answered:envelope.student_id",
        "item.answered:item.item_id",
        "item.answered:item.kc_ids",
        "item.answered:correct",
        "item.answered:latency_ms",
        "item.answered:presented_client_ts",
        "item.answered:hints_used",
        "item.answered:attempt",
        "item.answered:confidence_1_5",
        "item.answered:accommodation.time_multiplier",
        "item.answered:accommodation.assistive_modes",
    ):
        assert needed in refs


def test_malformed_catalogue_is_rejected(tmp_path):
    path = tmp_path / "catalogue.yaml"
    path.write_text(yaml.safe_dump({"version": 1}))
    with pytest.raises(CatalogueError, match="missing top-level key 'events'"):
        load_catalogue(path)
    good = yaml.safe_load(Paths().catalogue.read_text())
    good["events"]["session.end"]["colour"] = "blue"
    path.write_text(yaml.safe_dump(good))
    with pytest.raises(CatalogueError, match="unknown keys colour"):
        load_catalogue(path)


def test_record_names_follow_event_names():
    assert record_name("item.answered") == "ItemAnswered"
    assert record_name("tts.played") == "TtsPlayed"


def test_highest_privacy(sources):
    assert highest_privacy(sources.expanded("item.answered")) == "sensitive"
    assert highest_privacy(sources.expanded("notification.sent")) == "personal"


def test_generated_page_is_current(catalogue, sources, paths):
    assert doc_is_current(paths, catalogue, sources), "run make schemas-docs"


def test_generated_page_lists_every_event_and_the_ml_table(catalogue, sources):
    page = render(catalogue, sources)
    for name in catalogue.events:
        assert f"### {name}" in page
    assert "## Knowledge-tracing inputs (for the ML sign-off)" in page
