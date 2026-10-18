"""The concept graph (kuizi_brain/graph.py): order, levels, routing back, drawing."""

import pytest

from kuizi_brain import graph as G

ALL_MASTERED = dict.fromkeys(G.PHYSICS_KCS, 0.9)


def test_every_concept_has_french_and_arabic_names_and_known_prerequisites():
    for kc, (french, arabic, prerequisites) in G.PHYSICS_KCS.items():
        assert french.strip() and arabic.strip(), kc
        assert set(prerequisites) <= set(G.PHYSICS_KCS), kc


def test_topological_order_puts_every_prerequisite_first():
    order = G.topological_order()
    assert sorted(order) == sorted(G.PHYSICS_KCS)
    position = {kc: i for i, kc in enumerate(order)}
    for kc, (_, _, prerequisites) in G.PHYSICS_KCS.items():
        for p in prerequisites:
            assert position[p] < position[kc], f"{p} must come before {kc}"


def test_topological_order_is_deterministic():
    assert G.topological_order() == G.topological_order()
    assert G.topological_order()[:2] == ["deriv", "vect"]  # roots in alphabetical order


def test_a_cycle_is_rejected():
    graph = {"a": ("A", "أ", ["b"]), "b": ("B", "ب", ["a"]), "c": ("C", "ج", [])}
    with pytest.raises(ValueError, match="cycle"):
        G.topological_order(graph)


def test_depth_counts_the_longest_prerequisite_chain():
    assert G.depth() == {
        "deriv": 0,
        "vect": 0,
        "eqdiff": 1,
        "cinem": 1,
        "newton": 2,
        "rc": 2,
        "rl": 2,
        "energie": 3,
        "rlc": 3,
        "osc_meca": 4,
        "forcees": 5,
        "ondes": 5,
    }


def test_prerequisites_returns_a_copy():
    prerequisites = G.prerequisites("rlc")
    prerequisites.append("vect")
    assert G.prerequisites("rlc") == ["rc", "rl"]


def test_routing_back_goes_to_the_deepest_unmastered_prerequisite():
    # RLC fails because Dérivées are weak (level 0) and RC is shaky (level 2): go back to Dérivées.
    mastery = {**ALL_MASTERED, "deriv": 0.2, "rc": 0.4}
    assert G.weakest_prerequisite("rlc", mastery) == "deriv"


def test_routing_back_breaks_ties_by_lowest_mastery():
    mastery = {**ALL_MASTERED, "vect": 0.5, "deriv": 0.3}
    assert G.weakest_prerequisite("cinem", mastery) == "deriv"


def test_routing_back_follows_the_threshold():
    mastery = {**ALL_MASTERED, "deriv": 0.65}
    assert G.weakest_prerequisite("eqdiff", mastery) is None
    assert G.weakest_prerequisite("eqdiff", mastery, threshold=0.7) == "deriv"


def test_no_routing_back_when_everything_is_mastered_or_there_is_no_prerequisite():
    assert G.weakest_prerequisite("forcees", ALL_MASTERED) is None
    assert G.weakest_prerequisite("vect", {}) is None


def test_a_concept_never_seen_counts_as_unmastered():
    assert G.weakest_prerequisite("eqdiff", {}) == "deriv"


def test_drawing_shows_mastery_as_text_and_dashes_unmastered_concepts():
    """Accessibility: the value is written in the box and weak concepts get a dashed border, so
    the figure does not rely on colour alone."""
    ax = G.draw({**ALL_MASTERED, "deriv": 0.2})
    boxes = {t.get_text().split("\n")[0]: t for t in ax.texts if t.get_text()}
    assert set(boxes) == {french for french, _, _ in G.PHYSICS_KCS.values()}
    assert boxes["Dérivées"].get_text().endswith("20%")
    assert boxes["Dérivées"].get_bbox_patch().get_linestyle() == "--"
    assert boxes["Lois de Newton"].get_text().endswith("90%")
    assert boxes["Lois de Newton"].get_bbox_patch().get_linestyle() == "solid"


def test_drawing_without_mastery_shows_names_only():
    ax = G.draw()
    assert all("%" not in t.get_text() for t in ax.texts)
