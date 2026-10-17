#!/usr/bin/env python3
"""Re-plan sprints for the local-first delivery model (ADR 0006).

Schedules every ticket into a sprint, keeping the original order as priority:
- the Sprint 1 tickets, the pilot (T108, S12) and everything from S18 on stay where they are;
- cloud tickets (additions.CLOUD_TICKETS) start in S8 at the earliest;
- a ticket never comes before a ticket that blocks it (same sprint only where the plan already allowed it);
- no sprint goes over its capacity (a ramp for S1-S5, then the 134-point ceiling).

Writes the result into additions.REPLAN_SPRINTS. Run it, then build_backlog.py, then sync Jira.
Rerun it when capacity changes (for example after the S1-S2 velocity reset).
"""
import heapq
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import additions as A  # noqa: E402

A.REPLAN_SPRINTS = {}  # plan from the original sprints
import build_backlog as B  # noqa: E402

CAPACITY = {1: 13, 2: 40, 3: 65, 4: 80, 5: 95}
CEILING = 134
LAST_FLEXIBLE_SPRINT = 17
PINNED = {"T237": 1, "T234": 1, "T238": 1, "T108": 12}
CLOUD_FROM = 8
# The brain track goes first (the product owner learns and prototypes the brain on public data).
PRIORITY = {"T040": 2, "T041": 3, "T042": 4, "T043": 4}
# A ticket moves at most this many sprints earlier than planned (the brain track excepted).
MAX_PULL = int(sys.argv[1]) if len(sys.argv) > 1 else 1


def main():
    _, tickets, by_id = B.build()
    original = {t["id"]: t["sprint"] for t in tickets}
    pinned = dict(PINNED)
    pinned.update({t["id"]: t["sprint"] for t in tickets if t["sprint"] > LAST_FLEXIBLE_SPRINT})
    cloud = set(A.CLOUD_TICKETS)

    # Latest sprint a ticket may take so that every pinned ticket after it keeps its sprint.
    deadline = {t["id"]: LAST_FLEXIBLE_SPRINT for t in tickets}
    deadline.update(pinned)
    changed = True
    while changed:
        changed = False
        for t in tickets:
            for b in t["blocked"]:
                same_ok = original[b] >= original[t["id"]]
                limit = deadline[t["id"]] - (0 if same_ok else 1)
                if b not in pinned and limit < deadline[b]:
                    deadline[b] = limit
                    changed = True

    load = {s: 0 for s in range(1, 21)}
    sprint = {}
    for tid, s in pinned.items():
        sprint[tid] = s
        load[s] += by_id[tid]["points"]

    waiting = {t["id"]: {b for b in t["blocked"]} for t in tickets if t["id"] not in pinned}
    dependents = {t["id"]: [] for t in tickets}
    for t in tickets:
        for b in t["blocked"]:
            dependents[b].append(t["id"])

    def key(tid):
        return (min(PRIORITY.get(tid, original[tid]), deadline[tid]), deadline[tid], int(tid[1:]))

    ready = [key(tid) + (tid,) for tid, w in waiting.items() if not (w - set(sprint))]
    heapq.heapify(ready)
    queued = {r[-1] for r in ready}
    problems = []
    while ready:
        tid = heapq.heappop(ready)[-1]
        t = by_id[tid]
        earliest = CLOUD_FROM if tid in cloud else max(1, PRIORITY.get(tid, original[tid] - MAX_PULL))
        for b in t["blocked"]:
            same_ok = original[b] >= original[tid]
            earliest = max(earliest, sprint[b] + (0 if same_ok else 1))
        s = earliest
        while s <= LAST_FLEXIBLE_SPRINT and load[s] + t["points"] > CAPACITY.get(s, CEILING):
            s += 1
        if s > LAST_FLEXIBLE_SPRINT:
            s = max(earliest, LAST_FLEXIBLE_SPRINT)
            problems.append(f"{tid} over capacity in S{s}")
        if s > deadline[tid]:
            problems.append(f"{tid} in S{s} misses its deadline S{deadline[tid]}")
        sprint[tid] = s
        load[s] += t["points"]
        for d in dependents[tid]:
            if d in waiting and d not in queued and not (waiting[d] - set(sprint)):
                heapq.heappush(ready, key(d) + (d,))
                queued.add(d)

    missing = [tid for tid in waiting if tid not in sprint]
    assert not missing, f"unscheduled (dependency cycle?): {missing}"
    for t in tickets:
        for b in t["blocked"]:
            if sprint[b] > sprint[t["id"]]:
                problems.append(f"{t['id']} (S{sprint[t['id']]}) before its blocker {b} (S{sprint[b]})")

    moved = {tid: s for tid, s in sorted(sprint.items(), key=lambda x: int(x[0][1:])) if s != original[tid]}
    print("points per sprint:", {s: load[s] for s in range(1, 21)})
    print(f"{len(moved)} tickets change sprint")
    for p in problems:
        print("PROBLEM:", p)

    path = HERE / "additions.py"
    text = path.read_text(encoding="utf-8")
    body = ", ".join(f'"{tid}": {s}' for tid, s in moved.items())
    lines, line = [], "    "
    for item in body.split(", "):
        if len(line) + len(item) + 2 > 110:
            lines.append(line.rstrip())
            line = "    "
        line += item + ", "
    lines.append(line.rstrip())
    new = "REPLAN_SPRINTS = {\n" + "\n".join(lines) + "\n}"
    text, n = re.subn(r"REPLAN_SPRINTS = \{.*?\n?\}", new, text, count=1, flags=re.S)
    assert n == 1
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
