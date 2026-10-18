"""The starter seed and the validation rules (no database)."""

from __future__ import annotations

import copy
import dataclasses

import pytest
import yaml
from kuizi_kc_graph import STARTER_SEED
from kuizi_kc_graph import graph as g
from kuizi_kc_graph.cli import main
from kuizi_kc_graph.model import ARABIC_LETTER, Edge, Graph, Membership, validate_graph
from kuizi_kc_graph.seed import SeedError, load_seed, parse_seed

# The 12 concepts of the brain walkthrough (ml/kuizi_brain/graph.py) and where they live now.
BRAIN_TO_SEED = {
    "vect": "maths.geometry.vectors",
    "deriv": "maths.analysis.derivative",
    "eqdiff": "maths.analysis.ode1",
    "cinem": "physics.mech.kinematics",
    "newton": "physics.mech.newton2",
    "energie": "physics.mech.energy",
    "osc_meca": "physics.mech.oscillations.free",
    "rc": "physics.elec.rc",
    "rl": "physics.elec.rl",
    "rlc": "physics.elec.rlc.free",
    "forcees": "physics.elec.rlc.forced",
    "ondes": "physics.waves.mechanical",
}


def chapter_of(graph: Graph, kc_id: str) -> dict[str, int | None]:
    return {m.track_id: m.chapter_no for m in graph.memberships if m.kc_id == kc_id}


def test_starter_seed_is_valid(starter):
    assert validate_graph(starter) == []
    assert {t.id for t in starter.tracks} == {"math-4", "sexp-4", "tech-4"}


def test_starter_seed_has_no_cycles(starter):
    kc_ids = [k.id for k in starter.kcs]
    for edge_type in ("prerequisite", "sub_concept"):
        assert g.find_cycle(kc_ids, starter.edge_pairs(edge_type)) is None
    order = g.topological_order(kc_ids, starter.edge_pairs("prerequisite"))
    assert len(order) == len(kc_ids)


def test_every_programme_chapter_has_core_kcs(starter):
    covered = {(m.track_id, m.subject_id, m.chapter_no) for m in starter.memberships}
    missing = [
        (c.track_id, c.number, c.title_fr)
        for c in starter.chapters
        if (c.track_id, c.subject_id, c.number) not in covered
    ]
    assert missing == []


def test_names_are_bilingual(starter):
    for kc in starter.kcs:
        assert kc.name_fr.strip(), kc.id
        assert ARABIC_LETTER.search(kc.name_ar), kc.id


def test_starter_marks_everything_to_review_and_invents_no_numbers(starter):
    assert {k.status for k in starter.kcs} == {"to_review"}
    assert {e.status for e in starter.edges} == {"to_review"}
    assert all(m.exam_weight is None for m in starter.memberships)
    assert all(k.difficulty_prior is None for k in starter.kcs)


def test_tracks_share_kcs_with_their_own_chapters(starter):
    assert chapter_of(starter, "physics.elec.rc") == {"math-4": 1, "sexp-4": 1, "tech-4": 1}
    assert chapter_of(starter, "physics.waves.mechanical") == {
        "math-4": 7,
        "sexp-4": 7,
        "tech-4": 9,
    }
    assert chapter_of(starter, "physics.elec.filters") == {"tech-4": 7}
    assert chapter_of(starter, "physics.elec.filters.passive") == {"tech-4": 8}
    assert chapter_of(starter, "physics.waves.reflection_refraction") == {"math-4": 8}
    assert "tech-4" not in chapter_of(starter, "physics.nuclear.reactions")
    assert chapter_of(starter, "physics.mech.newton2") == {
        "math-4": None,
        "sexp-4": None,
        "tech-4": None,
    }


def test_brain_walkthrough_concepts_are_kept(starter):
    kc_ids = {k.id for k in starter.kcs}
    assert set(BRAIN_TO_SEED.values()) <= kc_ids


def test_cli_validate(capsys):
    assert main(["validate", str(STARTER_SEED)]) == 0
    out = capsys.readouterr().out
    assert out.startswith("ok: ")
    assert "sexp-4:" in out


# --- validation catches mistakes -------------------------------------------------------


def problems_after(graph: Graph, change) -> list[str]:
    changed = copy.deepcopy(graph)
    change(changed)
    return validate_graph(changed)


def test_a_prerequisite_cycle_is_reported(starter):
    problems = problems_after(
        starter,
        lambda gr: gr.edges.append(Edge("physics.elec.rc.time_constant", "physics.elec.rc.capacitor", "prerequisite")),
    )
    assert any("prerequisite edges form a cycle" in p for p in problems)


def test_a_self_loop_is_reported(starter):
    problems = problems_after(
        starter, lambda gr: gr.edges.append(Edge("physics.elec.rc", "physics.elec.rc", "related"))
    )
    assert any("cannot join a KC to itself" in p for p in problems)


def test_a_missing_prerequisite_in_a_track_is_reported(starter):
    def drop(gr: Graph) -> None:
        gr.memberships = [
            m for m in gr.memberships if not (m.track_id == "tech-4" and m.kc_id == "physics.elec.circuit_laws")
        ]

    problems = problems_after(starter, drop)
    assert any(p.startswith("track tech-4:") and "needs physics.elec.circuit_laws" in p for p in problems)


def test_french_in_the_arabic_field_is_reported(starter):
    def frenchify(gr: Graph) -> None:
        gr.kcs[0] = dataclasses.replace(gr.kcs[0], name_ar=gr.kcs[0].name_fr)

    assert any("has no Arabic letters" in p for p in problems_after(starter, frenchify))


def test_unknown_chapter_and_unsourced_weight_are_reported(starter):
    def bad_memberships(gr: Graph) -> None:
        gr.memberships.append(Membership("sexp-4", "physics.elec.filters", "physics", "core", 12))
        first = next(i for i, m in enumerate(gr.memberships) if m.scope == "core")
        gr.memberships[first] = dataclasses.replace(gr.memberships[first], exam_weight=0.2)

    problems = problems_after(starter, bad_memberships)
    assert any("chapter 12 is not in the physics programme of sexp-4" in p for p in problems)
    assert any("needs exam_weight_source" in p for p in problems)


def test_shape_problems_are_reported():
    _, problems = parse_seed({"format": "something else", "kcs": "not a list"})
    assert "format must be 'kuizi.kc-graph.seed'" in problems
    assert any("kcs must be a list" in p for p in problems)


def test_a_typo_in_a_kc_key_is_reported(tmp_path):
    data = yaml.safe_load(STARTER_SEED.read_text(encoding="utf-8"))
    data["kcs"][0]["prerequisite"] = ["maths.analysis.derivative"]  # typo for "requires"
    seed = tmp_path / "typo.yaml"
    seed.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    with pytest.raises(SeedError) as caught:
        load_seed(seed)
    assert any("unknown key 'prerequisite'" in p for p in caught.value.problems)
