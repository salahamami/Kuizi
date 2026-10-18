"""The JSON export and its schema (no database: built straight from the starter seed)."""

from __future__ import annotations

import copy
import dataclasses
from datetime import UTC, datetime

import pytest
from jsonschema import Draft202012Validator

from kuizi_kc_graph.export import (
    ExportError,
    build_export,
    check_export,
    content_hash,
    load_export_schema,
)

MONDAY = datetime(2026, 11, 2, 8, 0, tzinfo=UTC)


def kc_entry(doc: dict, kc_id: str) -> dict:
    return next(k for k in doc["kcs"] if k["id"] == kc_id)


def test_schema_is_a_valid_json_schema():
    Draft202012Validator.check_schema(load_export_schema())


def test_export_of_every_track_validates(starter):
    doc = build_export(starter, generated_at=MONDAY)
    assert check_export(doc) == []
    assert doc["generated_at"] == "2026-11-02T08:00:00Z"
    assert [t["id"] for t in doc["tracks"]] == ["math-4", "sexp-4", "tech-4"]
    assert len(doc["kcs"]) == len(starter.kcs)


@pytest.mark.parametrize("track", ["math-4", "sexp-4", "tech-4"])
def test_export_of_one_track_validates_and_holds_only_that_track(starter, track):
    doc = build_export(starter, tracks=[track])
    assert check_export(doc) == []
    assert doc["filter"] == {"tracks": [track], "reviewed_only": False}
    members = {m.kc_id for m in starter.memberships if m.track_id == track}
    assert {k["id"] for k in doc["kcs"]} == members
    assert all(m["track"] == track for k in doc["kcs"] for m in k["memberships"])


def test_track_exports_differ_where_the_programmes_differ(starter):
    tech = {k["id"] for k in build_export(starter, tracks=["tech-4"])["kcs"]}
    sexp = {k["id"] for k in build_export(starter, tracks=["sexp-4"])["kcs"]}
    assert "physics.elec.filters.active" in tech - sexp
    assert "physics.nuclear.reactions.decay_law" in sexp - tech
    assert "physics.elec.rc.time_constant" in tech & sexp


def test_topological_order_puts_prerequisites_first(starter):
    doc = build_export(starter, tracks=["sexp-4"])
    order = doc["tracks"][0]["topological_order"]
    position = {kc_id: i for i, kc_id in enumerate(order)}
    for kc in doc["kcs"]:
        for prerequisite in kc["prerequisites"]:
            assert position[prerequisite] < position[kc["id"]], (prerequisite, kc["id"])
    assert order.index("maths.analysis.ode1") < order.index("physics.elec.rc.ode")


def test_export_carries_what_routing_and_rag_need(starter):
    doc = build_export(starter, tracks=["sexp-4"])
    kc = kc_entry(doc, "physics.elec.rlc.forced.resonance")
    # Routing: prerequisites, depth, sub-concept parent, track membership.
    assert kc["prerequisites"] == ["physics.elec.rlc.forced.impedance", "physics.elec.rlc.free.lc"]
    assert kc["parents"] == ["physics.elec.rlc.forced"]
    assert kc["depth"] > kc_entry(doc, "physics.elec.rlc.forced.impedance")["depth"]
    assert kc["memberships"] == [
        {
            "track": "sexp-4",
            "scope": "core",
            "chapter": 4,
            "exam_weight": None,
            "exam_weight_source": None,
            "source_ref": None,
        }
    ]
    assert kc["related"] == ["physics.mech.oscillations.forced.resonance"]
    # RAG: names in both languages, ltree path, chapter title for citations.
    assert kc["name"]["fr"].startswith("Résonance d'intensité")
    assert kc["name"]["ar"].startswith("رنين الشدة")
    assert kc["path"].startswith("physics.elec.rlc.")
    chapters = doc["tracks"][0]["programmes"][0]["chapters"]
    chapter = next(c for c in chapters if c["number"] == kc["memberships"][0]["chapter"])
    assert chapter["title"]["fr"] == "Oscillations électriques forcées en régime sinusoïdal"
    # A prerequisite-scope KC says where it is taught.
    newton = kc_entry(doc, "physics.mech.newton2")["memberships"][0]
    assert newton["scope"] == "prerequisite" and newton["chapter"] is None
    assert newton["source_ref"]


def test_graph_hash_ignores_the_timestamp_but_not_the_content(starter):
    first = build_export(starter, generated_at=MONDAY)
    second = build_export(starter, generated_at=datetime(2027, 6, 1, tzinfo=UTC))
    assert first["graph_hash"] == second["graph_hash"]
    renamed = copy.deepcopy(starter)
    renamed.kcs[0] = dataclasses.replace(renamed.kcs[0], name_fr="Vecteurs")
    assert build_export(renamed)["graph_hash"] != first["graph_hash"]
    assert content_hash(first) == first["graph_hash"]


def test_reviewed_only_export_of_the_starter_is_empty_but_valid(starter):
    doc = build_export(starter, reviewed_only=True)
    assert check_export(doc) == []
    assert doc["kcs"] == [] and doc["edges"] == []
    assert all(t["topological_order"] == [] for t in doc["tracks"])


def test_reviewed_only_keeps_reviewed_kcs_and_edges(starter):
    graph = copy.deepcopy(starter)
    reviewed = {"physics.elec.circuit_laws", "physics.elec.rc.capacitor"}
    graph.kcs = [dataclasses.replace(k, status="reviewed") if k.id in reviewed else k for k in graph.kcs]
    graph.edges = [
        dataclasses.replace(e, status="reviewed")
        if (e.from_kc, e.to_kc) == ("physics.elec.circuit_laws", "physics.elec.rc.capacitor")
        else e
        for e in graph.edges
    ]
    doc = build_export(graph, tracks=["tech-4"], reviewed_only=True)
    assert check_export(doc) == []
    assert {k["id"] for k in doc["kcs"]} == reviewed
    assert doc["edges"] == [
        {
            "from": "physics.elec.circuit_laws",
            "to": "physics.elec.rc.capacitor",
            "type": "prerequisite",
            "review_status": "reviewed",
        }
    ]


def test_retired_kcs_are_not_exported(starter):
    graph = copy.deepcopy(starter)
    graph.kcs = [
        dataclasses.replace(k, status="retired") if k.id == "physics.elec.filters.active" else k for k in graph.kcs
    ]
    doc = build_export(graph, tracks=["tech-4"])
    assert check_export(doc) == []
    assert "physics.elec.filters.active" not in {k["id"] for k in doc["kcs"]}


def test_unknown_track_is_refused(starter):
    with pytest.raises(ExportError, match="unknown track"):
        build_export(starter, tracks=["lettres-4"])


def test_check_export_catches_a_broken_document(starter):
    doc = build_export(starter, tracks=["sexp-4"])
    broken = copy.deepcopy(doc)
    broken["tracks"][0]["topological_order"].reverse()
    assert any("must come before" in p for p in check_export(broken))
    broken = copy.deepcopy(doc)
    broken["kcs"][0]["name"]["ar"] = ""
    assert any("name/ar" in p for p in check_export(broken))
    broken = copy.deepcopy(doc)
    broken["kcs"][0]["review_status"] = "reviewed"
    assert check_export(broken) == ["graph_hash does not match the content"]
