"""Graph algorithms on plain ids and (from, to) edges, shared by validation and export.

The same rules as the database trigger, so a seed file can be checked without PostgreSQL.
Every function is deterministic: ties are broken by id, so exports and messages are stable.
"""

from __future__ import annotations

import heapq
from collections.abc import Iterable


def successors(nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> dict[str, set[str]]:
    """Adjacency sets restricted to `nodes`; edges touching other nodes are ignored."""
    succ: dict[str, set[str]] = {node: set() for node in nodes}
    for source, target in edges:
        if source in succ and target in succ:
            succ[source].add(target)
    return succ


def predecessors(nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> dict[str, set[str]]:
    """Reverse adjacency sets restricted to `nodes`."""
    pred: dict[str, set[str]] = {node: set() for node in nodes}
    for source, target in edges:
        if source in pred and target in pred:
            pred[target].add(source)
    return pred


def find_cycle(nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> list[str] | None:
    """One directed cycle as [a, b, ..., a], or None when the graph is acyclic."""
    succ = successors(nodes, edges)
    white, grey, black = 0, 1, 2
    colour = dict.fromkeys(succ, white)
    for root in sorted(succ):
        if colour[root] != white:
            continue
        colour[root] = grey
        trail = [root]
        stack = [iter(sorted(succ[root]))]
        while stack:
            for child in stack[-1]:
                if colour[child] == grey:
                    return trail[trail.index(child):] + [child]
                if colour[child] == white:
                    colour[child] = grey
                    trail.append(child)
                    stack.append(iter(sorted(succ[child])))
                    break
            else:
                colour[trail.pop()] = black
                stack.pop()
    return None


def topological_order(nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> list[str]:
    """Nodes ordered so every edge goes forward (Kahn's algorithm, smallest id first).

    Raises ValueError naming one cycle if there is no such order.
    """
    nodes = list(nodes)
    edges = list(edges)
    succ = successors(nodes, edges)
    indegree = dict.fromkeys(succ, 0)
    for targets in succ.values():
        for target in targets:
            indegree[target] += 1
    ready = [node for node, degree in indegree.items() if degree == 0]
    heapq.heapify(ready)
    order: list[str] = []
    while ready:
        node = heapq.heappop(ready)
        order.append(node)
        for target in succ[node]:
            indegree[target] -= 1
            if indegree[target] == 0:
                heapq.heappush(ready, target)
    if len(order) != len(succ):
        cycle = find_cycle(nodes, edges) or []
        raise ValueError("the graph has a cycle: " + " -> ".join(cycle))
    return order


def depths(nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> dict[str, int]:
    """0 for a node without incoming edges, otherwise 1 + the deepest predecessor."""
    nodes = list(nodes)
    edges = list(edges)
    pred = predecessors(nodes, edges)
    depth: dict[str, int] = {}
    for node in topological_order(nodes, edges):
        depth[node] = 1 + max((depth[p] for p in pred[node]), default=-1)
    return depth


def ancestors(node: str, pred: dict[str, set[str]]) -> set[str]:
    """Every node with a path to `node` (its transitive predecessors)."""
    seen: set[str] = set()
    todo = list(pred.get(node, ()))
    while todo:
        current = todo.pop()
        if current not in seen:
            seen.add(current)
            todo.extend(pred.get(current, ()))
    return seen
