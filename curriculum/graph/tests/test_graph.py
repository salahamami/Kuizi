"""Graph algorithms (no database)."""

import pytest
from kuizi_kc_graph import graph as g

NODES = ["a", "b", "c", "d"]
EDGES = [("a", "b"), ("b", "c"), ("a", "c"), ("d", "c")]


def test_topological_order_puts_every_edge_forward_and_is_stable():
    order = g.topological_order(NODES, EDGES)
    assert order == ["a", "b", "d", "c"]
    position = {node: i for i, node in enumerate(order)}
    assert all(position[s] < position[t] for s, t in EDGES)
    assert g.topological_order(reversed(NODES), list(reversed(EDGES))) == order


def test_topological_order_raises_on_a_cycle():
    with pytest.raises(ValueError, match="cycle: a -> b -> c -> a"):
        g.topological_order(NODES, [("a", "b"), ("b", "c"), ("c", "a")])


def test_find_cycle():
    assert g.find_cycle(NODES, EDGES) is None
    assert g.find_cycle(NODES, [*EDGES, ("c", "a")]) == ["a", "b", "c", "a"]
    assert g.find_cycle(["x"], [("x", "x")]) == ["x", "x"]


def test_edges_outside_the_node_set_are_ignored():
    assert g.topological_order(["a", "b"], [("a", "b"), ("b", "zz"), ("zz", "a")]) == ["a", "b"]


def test_depths_and_ancestors():
    assert g.depths(NODES, EDGES) == {"a": 0, "b": 1, "d": 0, "c": 2}
    pred = g.predecessors(NODES, EDGES)
    assert g.ancestors("c", pred) == {"a", "b", "d"}
    assert g.ancestors("a", pred) == set()
