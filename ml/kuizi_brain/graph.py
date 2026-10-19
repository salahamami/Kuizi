"""The concept graph: which concept must be known before which (T032, T035, T052).

An illustrative slice of the Tunisian Bac Physics programme. The full graph, for every
subject and track, is built in T035 (Physics) and T111 (the other subjects).
"""

from collections import deque

import matplotlib.pyplot as plt

# kc id -> (French name, Arabic name, prerequisite kc ids)
PHYSICS_KCS = {
    "vect": ("Vecteurs et repères", "الأشعة والمعالم", []),
    "deriv": ("Dérivées", "الاشتقاق", []),
    "eqdiff": ("Équations différentielles du 1er ordre", "المعادلات التفاضلية من الرتبة الأولى", ["deriv"]),
    "cinem": ("Cinématique du point", "حركية النقطة المادية", ["vect", "deriv"]),
    "newton": ("Lois de Newton", "قوانين نيوتن", ["cinem"]),
    "energie": ("Travail et énergie", "العمل والطاقة", ["newton"]),
    "osc_meca": ("Oscillations mécaniques libres", "الذبذبات الميكانيكية الحرة", ["newton", "energie", "eqdiff"]),
    "rc": ("Dipôle RC", "ثنائي القطب RC", ["eqdiff"]),
    "rl": ("Dipôle RL", "ثنائي القطب RL", ["eqdiff"]),
    "rlc": ("Oscillations électriques libres (RLC)", "الذبذبات الكهربائية الحرة RLC", ["rc", "rl"]),
    "forcees": ("Oscillations forcées", "الذبذبات القسرية", ["rlc", "osc_meca"]),
    "ondes": ("Ondes mécaniques progressives", "الموجات الميكانيكية المتنقلة", ["osc_meca"]),
}


def prerequisites(kc, graph=PHYSICS_KCS):
    """Direct prerequisites of a concept."""
    return list(graph[kc][2])


def topological_order(graph=PHYSICS_KCS):
    """Concepts in an order where every concept comes after its prerequisites (Kahn's algorithm).

    The graph is a DAG (directed acyclic graph): if a cycle existed, no order would be
    possible and this function raises. T034 runs the same check whenever an author edits
    the graph.
    """
    indegree = {kc: len(v[2]) for kc, v in graph.items()}
    children = {kc: [] for kc in graph}
    for kc, (_, _, pre) in graph.items():
        for p in pre:
            children[p].append(kc)
    queue = deque(sorted(kc for kc, d in indegree.items() if d == 0))
    order = []
    while queue:
        kc = queue.popleft()
        order.append(kc)
        for c in sorted(children[kc]):
            indegree[c] -= 1
            if indegree[c] == 0:
                queue.append(c)
    if len(order) != len(graph):
        raise ValueError("the concept graph has a cycle")
    return order


def depth(graph=PHYSICS_KCS):
    """Level of each concept: 0 for concepts without prerequisites, then 1 + deepest prerequisite."""
    d = {}
    for kc in topological_order(graph):
        pre = graph[kc][2]
        d[kc] = 0 if not pre else 1 + max(d[p] for p in pre)
    return d


def weakest_prerequisite(kc, mastery, threshold=0.6, graph=PHYSICS_KCS):
    """Routing back (T052, T053): the deepest unmastered prerequisite behind a struggling concept.

    Walks the prerequisites breadth first and returns the unmastered concept furthest down
    the chain, so a student who fails RLC because Dérivées are weak is sent to Dérivées,
    not to harder RLC exercises. Returns None when every prerequisite is mastered.
    """
    levels = depth(graph)
    seen, queue, weak = set(), deque(prerequisites(kc, graph)), []
    while queue:
        p = queue.popleft()
        if p in seen:
            continue
        seen.add(p)
        if mastery.get(p, 0.0) < threshold:
            weak.append(p)
        queue.extend(prerequisites(p, graph))
    if not weak:
        return None
    return min(weak, key=lambda p: (levels[p], mastery.get(p, 0.0)))


def draw(mastery=None, ax=None, graph=PHYSICS_KCS, threshold=0.6):
    """Draw the graph by level. With mastery values, each box shows its value as text and
    unmastered concepts get a dashed border, so nothing relies on colour alone."""
    levels = depth(graph)
    by_level = {}
    for kc in topological_order(graph):
        by_level.setdefault(levels[kc], []).append(kc)
    pos = {}
    for lvl, kcs in by_level.items():
        for i, kc in enumerate(kcs):
            pos[kc] = (lvl, -(i - (len(kcs) - 1) / 2))
    ax = ax or plt.subplots(figsize=(13, 6))[1]
    for kc, (_, _, pre) in graph.items():
        for p in pre:
            (x0, y0), (x1, y1) = pos[p], pos[kc]
            ax.annotate(
                "", xy=(x1 - 0.32, y1), xytext=(x0 + 0.32, y0), arrowprops=dict(arrowstyle="->", color="#555", lw=1)
            )
    for kc, (x, y) in pos.items():
        label = graph[kc][0]
        style = dict(boxstyle="round,pad=0.3", fc="#e8f0fb", ec="#1f4e8c", lw=1.2)
        if mastery is not None:
            m = mastery.get(kc, 0.0)
            label += f"\n{m:.0%}"
            if m < threshold:
                style.update(ec="#b3261e", ls="--", lw=1.6, fc="#fdeeee")
        ax.text(x, y, label, ha="center", va="center", fontsize=8, bbox=style, wrap=True)
    ax.set_xlim(-0.6, max(levels.values()) + 0.6)
    ax.set_ylim(min(p[1] for p in pos.values()) - 0.7, max(p[1] for p in pos.values()) + 0.7)
    ax.axis("off")
    return ax
