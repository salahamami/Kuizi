#!/usr/bin/env python3
"""Re-plan sprints (local-first ADR 0006, re-planned for 6e-9e by ADR 0011).

Schedules every ticket into a sprint of the 24-sprint horizon, keeping the planned order as priority:
- tickets done or in review (Sprints 1 and 2), the free pilot (T108, S10), the pilot exit review
  (T272, S20) and the paid launch (T110, S24) stay where they are;
- cloud tickets (additions.CLOUD_TICKETS) start in S6 at the earliest, so the cloud move (T240) is
  ready one sprint before the pilot;
- Bac phase 2 tickets (additions.BAC_PHASE2, ADR 0011) are left out: they have no sprint;
- a ticket never comes before a ticket that blocks it (same sprint only where the plan already allowed it,
  and never in the sprint of the design approval that gates it: the design gate, ADR 0011);
- a ticket moves at most MAX_PULL sprints earlier than planned, unless a pinned ticket needs it sooner;
  tickets planned after the concours (from NO_PULL_FROM) are not pulled earlier;
- no sprint goes over its capacity (additions.CAPACITY ramp for S1-S5, then additions.CEILING).

The planned sprint of a ticket is its sprint in the data before this script runs: the v1 sprint, the
sprint of a ticket in additions.TICKETS or REWRITES, or its additions.TARGET_SPRINTS entry.
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

A.REPLAN_SPRINTS = {}  # plan from the planned sprints
import build_backlog as B  # noqa: E402

HORIZON = A.HORIZON
LAST_FLEXIBLE_SPRINT = HORIZON - 1
# Done or in review: they keep their sprints (Sprint 1 and the Sprint 2 tickets worked ahead).
DONE_OR_IN_REVIEW = {"T237": 1, "T238": 1, "T234": 1, "T040": 1,
                     "T006": 2, "T012": 2, "T023": 2, "T032": 2, "T231": 2}
PINNED = dict(DONE_OR_IN_REVIEW, **{A.PILOT_TICKET: A.PILOT_SPRINT, "T272": 20, A.LAUNCH_TICKET: A.LAUNCH_SPRINT})
CLOUD_FROM = 6
# The brain track goes first (the product owner learns and prototypes the brain on public data).
PRIORITY = {"T041": 3, "T042": 4, "T043": 4}
# A ticket moves at most this many sprints earlier than planned (the brain track and deadlines excepted).
MAX_PULL = int(sys.argv[1]) if len(sys.argv) > 1 else 1
# Tickets planned from this sprint on (after the June 2027 concours) are placed after the pilot on purpose.
NO_PULL_FROM = 19


def main():
    _, tickets, by_id = B.build()
    # Bac phase 2 (ADR 0011) stays in the backlog without a sprint.
    later = set(A.BAC_PHASE2)
    tickets = [t for t in tickets if t["id"] not in later]
    original = {t["id"]: t["sprint"] for t in tickets}
    pinned = dict(PINNED)
    pinned.update({t["id"]: t["sprint"] for t in tickets if t["sprint"] > LAST_FLEXIBLE_SPRINT})
    cloud = set(A.CLOUD_TICKETS)

    def same_ok(b, tid):
        """May a ticket share a sprint with its blocker b? Never with the design approval that gates it."""
        return b not in A.DESIGN_APPROVALS and original[b] >= original[tid]

    # Latest sprint a ticket may take so that every pinned ticket after it keeps its sprint.
    deadline = {t["id"]: LAST_FLEXIBLE_SPRINT for t in tickets}
    deadline.update(pinned)
    changed = True
    while changed:
        changed = False
        for t in tickets:
            for b in t["blocked"]:
                limit = deadline[t["id"]] - (0 if same_ok(b, t["id"]) else 1)
                if b not in pinned and limit < deadline[b]:
                    deadline[b] = limit
                    changed = True

    load = {s: 0 for s in range(1, HORIZON + 1)}
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
        pull = 0 if original[tid] >= NO_PULL_FROM else MAX_PULL
        earliest = max(1, PRIORITY.get(tid, original[tid] - pull))
        earliest = min(earliest, deadline[tid])  # pulled sooner when a pinned ticket needs it
        if tid in cloud:
            earliest = max(earliest, CLOUD_FROM)
        for b in t["blocked"]:
            earliest = max(earliest, sprint[b] + (0 if same_ok(b, tid) else 1))
        s = earliest
        while s <= LAST_FLEXIBLE_SPRINT and load[s] + t["points"] > A.CAPACITY.get(s, A.CEILING):
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
            if sprint[b] > sprint[t["id"]] or (b in A.DESIGN_APPROVALS and sprint[b] >= sprint[t["id"]]):
                problems.append(f"{t['id']} (S{sprint[t['id']]}) not after its blocker {b} (S{sprint[b]})")
    for s in range(1, HORIZON + 1):
        unpinned = load[s] - sum(by_id[tid]["points"] for tid, p in DONE_OR_IN_REVIEW.items() if p == s)
        if load[s] > A.CAPACITY.get(s, A.CEILING) and unpinned > 0:
            problems.append(f"S{s} is over capacity ({load[s]} points)")

    moved = {tid: s for tid, s in sorted(sprint.items(), key=lambda x: int(x[0][1:])) if s != original[tid]}
    print("points per sprint:", {s: load[s] for s in range(1, HORIZON + 1)})
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
