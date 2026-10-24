"""Build the full Kuizi backlog (v2) from the v1 source and additions.py.

Usage: python3 tools/backlog/build_backlog.py

Inputs:  docs/backlog/source/APL_jira_import_v1.csv
         docs/backlog/source/APL_Production_Backlog_v1.md
         tools/backlog/additions.py
         docs/backlog/jira_keys.csv              (backlog ID -> Jira key, kept up to date by the Jira sync)
Outputs: docs/backlog/APL_jira_import_full.csv   (Jira CSV importer)
         docs/backlog/apl_backlog.json           (API sync, see docs/backlog/README.md)
         docs/backlog/APL_Full_Backlog.md        (human-readable backlog)
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import additions as A  # noqa: E402

SRC_CSV = ROOT / "docs/backlog/source/APL_jira_import_v1.csv"
SRC_MD = ROOT / "docs/backlog/source/APL_Production_Backlog_v1.md"
OUT_CSV = ROOT / "docs/backlog/APL_jira_import_full.csv"
OUT_JSON = ROOT / "docs/backlog/apl_backlog.json"
OUT_MD = ROOT / "docs/backlog/APL_Full_Backlog.md"
JIRA_KEYS = ROOT / "docs/backlog/jira_keys.csv"

JIRA_PROJECT = "KK"
JIRA_BROWSE = "https://kuizi.atlassian.net/browse/"
SPRINT_START = "2026-10-19"  # S1 actually started on Saturday 2026-10-17
# Persona labels from the summary of a user story ("As a pupil, ..."). Pupils keep the label
# persona-student so the Jira labels stay stable (every learner is a pupil aged 11-15, ADR 0011).
_WORDS = r"(?:[\w/'’-]+ ){0,3}"
PERSONAS = [
    (rf"^As an? {_WORDS}(student|pupil) or parent", ["student", "parent"]),
    (rf"^As an? {_WORDS}(student|pupil)\b", ["student"]),
    (r"^As a screen-reader user", ["student"]),
    (r"^As a parent", ["parent"]),
    (r"^As a teacher-author", ["curriculum-author"]),
    (r"^As a teacher", ["teacher"]),
    (r"^As a curriculum lead", ["curriculum-author"]),
    (r"^As a school", ["school-admin"]),
    (r"^As a platform admin", ["platform-admin"]),
    (r"^As a visitor", ["visitor"]),
]


def personas_for(summary):
    for pattern, names in PERSONAS:
        if re.search(pattern, summary):
            return names
    return []


def sprint_num(value):
    m = re.search(r"(\d+)$", value or "")
    return int(m.group(1)) if m else None


def phase_of(sprint):
    """Phase name of a sprint (additions.PHASES); sprint 0 is the Bac phase 2 holding area."""
    if not sprint:
        return A.BAC_PHASE
    for name, first, last in A.PHASES:
        if first <= sprint <= last:
            return name
    raise ValueError(f"sprint {sprint} is outside the horizon (S1-S{A.HORIZON})")


def parse_sections(desc):
    """Split a v1 Jira-wiki description into its h3 sections."""
    parts = {}
    for block in re.split(r"\n?h3\. ", "\n" + desc)[1:]:
        title, _, body = block.partition("\n")
        parts[title.strip()] = body.strip()
    return parts


def bullets(text):
    return [line[2:].strip() for line in text.splitlines() if line.startswith("* ")]


def load_v1():
    rows = list(csv.reader(open(SRC_CSV, encoding="utf-8-sig")))
    header, data = rows[0], rows[1:]
    idx = defaultdict(list)
    for i, name in enumerate(header):
        idx[name].append(i)

    def one(r, name):
        return r[idx[name][0]]

    epics, tickets = [], []
    for r in data:
        sections = parse_sections(one(r, "Description"))
        labels = [r[i] for i in idx["Labels"] if r[i]]
        if one(r, "Issue Type") == "Epic":
            phase = one(r, "Fix Version")
            epics.append(dict(id=one(r, "Issue ID"), name=one(r, "Summary"), phase=phase,
                              priority=one(r, "Priority"), component=one(r, "Components"),
                              labels=labels, goal=sections.get("Goal", ""),
                              dod=sections.get("Definition of Done", ""), source="v1"))
        else:
            tickets.append(dict(id=one(r, "Issue ID"), type=one(r, "Issue Type"), epic=one(r, "Parent"),
                                summary=one(r, "Summary"), desc=sections.get("Description", ""),
                                ac=bullets(sections.get("Acceptance Criteria", "")),
                                points=int(one(r, "Story Points") or 0), priority=one(r, "Priority"),
                                sprint=sprint_num(one(r, "Sprint")), team=one(r, "Team"),
                                component=one(r, "Components"), fix_version=one(r, "Fix Version"),
                                blocked=[r[i] for i in idx["Blocked By"] if r[i]],
                                labels=labels, changes=[], source="v1"))
    return epics, tickets


def build():
    epics, tickets = load_v1()
    by_id = {t["id"]: t for t in tickets}

    for tid, lines in A.CHANGES.items():
        by_id[tid]["changes"] = list(lines)
    for tid, split in A.SPLITS.items():
        by_id[tid].update({k: v for k, v in split.items() if k != "change"})
        by_id[tid]["changes"].append(split["change"])
    for tid, sprint in A.SPRINT_OVERRIDES.items():
        by_id[tid]["sprint"] = sprint
    for tid, extra in A.EXTRA_BLOCKERS.items():
        by_id[tid]["blocked"] += [b for b in extra if b not in by_id[tid]["blocked"]]

    epic_by_id = {e["id"]: e for e in epics}
    for e in A.EPICS:
        e = dict(e, source="v2")
        epics.append(e)
        epic_by_id[e["id"]] = e
    for t in A.TICKETS:
        t = dict(t, component=A.TEAM_COMPONENT[t["team"]], fix_version=phase_of(t["sprint"]),
                 changes=[], source="v2")
        tickets.append(t)
        by_id[t["id"]] = t
    # Re-scoped epics and tickets (ADR 0011: 6e-9e first, Bac in phase 2).
    for eid, fields in A.EPIC_REWRITES.items():
        epic_by_id[eid].update(fields)
    for tid, rewrite in A.REWRITES.items():
        by_id[tid].update({k: v for k, v in rewrite.items() if k != "change"})
        if "team" in rewrite:
            by_id[tid]["component"] = A.TEAM_COMPONENT[rewrite["team"]]
        if rewrite.get("change"):
            by_id[tid]["changes"].append(rewrite["change"])
    # Age-band rules and other ADR 0011 criteria added to existing tickets (minors-11-15.md 5.2).
    for tid, lines in A.ADR11_CHANGES.items():
        by_id[tid]["changes"] = by_id[tid]["changes"] + [f"ADR 0011: {line}" for line in lines]

    # Local-first re-plan (ADR 0006): swapped dependencies, then the re-planned sprints.
    for tid, swaps in A.LOCAL_FIRST_SWAPS.items():
        t = by_id[tid]
        t["blocked"] = list(dict.fromkeys(swaps.get(b, b) for b in t["blocked"]))
        for new in sorted(set(swaps.values())):
            olds = ", ".join(o for o, n in swaps.items() if n == new)
            line = f"Local-first (ADR 0006): starts from {new} instead of waiting for {olds}"
            t["changes"].append(line + ("; moves to AWS with T240" if new == "T237" else ""))
    # ADR 0011 dependency changes: re-pointed from Bac phase 2 work, legal gates and the design gate.
    for tid, dep in A.DEPS.items():
        t = by_id[tid]
        drop = set(dep.get("drop", []))
        added = [b for b in dep.get("add", []) if b not in t["blocked"]]
        t["blocked"] = [b for b in t["blocked"] if b not in drop] + added
        if dep.get("why"):
            t["changes"] = t["changes"] + [dep["why"]]
        gates = [b for b in added if b in A.DESIGN_APPROVALS]
        if gates:
            what = ", ".join(f"{b} ({A.DESIGN_APPROVALS[b]})" for b in gates)
            t["changes"] = t["changes"] + [f"Design gate (ADR 0011): starts only once the product owner has "
                                           f"approved the design of its journey: {what}"]
    # Planning targets of ADR 0011 (priority order for replan.py), then the re-planned sprints.
    for tid, sprint in A.TARGET_SPRINTS.items():
        by_id[tid]["sprint"] = sprint
    for tid, sprint in A.REPLAN_SPRINTS.items():
        by_id[tid]["sprint"] = sprint
    # Bac phase 2: kept in the backlog without a sprint (sprint 0).
    for tid in A.BAC_PHASE2:
        by_id[tid]["sprint"] = 0
    # A ticket's phase follows its sprint (additions.PHASES).
    for t in tickets:
        t["fix_version"] = phase_of(t["sprint"])

    # Integrity checks.
    ids = [t["id"] for t in tickets]
    dupes = [i for i, n in Counter(ids).items() if n > 1]
    assert not dupes, f"duplicate ticket ids: {dupes}"
    for t in tickets:
        for b in t["blocked"]:
            assert b in by_id, f"{t['id']} blocked by unknown {b}"
        assert t["epic"] in epic_by_id, f"{t['id']} has unknown epic {t['epic']}"
        assert t["points"] in (1, 2, 3, 5, 8, 13), f"{t['id']} has non-Fibonacci points"
        if t["sprint"]:
            late = [x for x in t["blocked"] if not by_id[x]["sprint"]]
            assert not late, f"{t['id']} (S{t['sprint']}) is blocked by Bac phase 2 tickets {late}"
            assert t["sprint"] <= A.HORIZON, f"{t['id']} is planned after the horizon (S{t['sprint']})"

    blocks = defaultdict(list)
    for t in tickets:
        for b in t["blocked"]:
            blocks[b].append(t["id"])
    for t in tickets:
        t["blocks"] = sorted(blocks[t["id"]], key=lambda x: int(x[1:]))
        t["personas"] = personas_for(t["summary"])
        t["epic_name"] = epic_by_id[t["epic"]]["name"]

    tickets.sort(key=lambda t: int(t["id"][1:]))
    epics.sort(key=lambda e: int(e["id"][1:]))
    for e in epics:
        mine = [t for t in tickets if t["epic"] == e["id"]]
        sprints = [t["sprint"] for t in mine if t["sprint"]]
        e["tickets"], e["points"] = len(mine), sum(t["points"] for t in mine)
        e["sprint_range"] = f"S{min(sprints)}–S{max(sprints)}" if sprints else ""
        # An epic's phase is the phase that carries most of its points.
        pts = Counter()
        for t in mine:
            pts[t["fix_version"]] += t["points"]
        scheduled = Counter({k: v for k, v in pts.items() if k != A.BAC_PHASE})
        e["phase"] = (scheduled or pts).most_common(1)[0][0] if pts else e["phase"]
    return epics, tickets, by_id


def wiki_description(t, by_id):
    lines = ["h3. Description", t["desc"], "", "h3. Acceptance Criteria"]
    lines += [f"* {a}" for a in t["ac"]]
    if t["changes"]:
        lines += ["", "h3. Addendum changes (v2)"] + [f"* {c}" for c in t["changes"]]
    lines += ["", "h3. Context", f"* Epic: {t['epic_name']}", f"* Phase: {t['fix_version']}",
              f"* Target sprint: {sprint_name(t)}", f"* Agent role: {t['team']}"]
    if t["personas"]:
        lines.append(f"* Personas: {', '.join(t['personas'])}")
    if t["blocked"]:
        lines.append("* Blocked by: " + ", ".join(f"{b} ({by_id[b]['summary']})" for b in t["blocked"]))
    if t["blocks"]:
        lines.append("* Blocks: " + ", ".join(t["blocks"]))
    return "\n".join(lines)


def markdown_description(t, by_id):
    lines = [t["desc"], "", "**Acceptance criteria**", ""] + [f"- {a}" for a in t["ac"]]
    if t["changes"]:
        lines += ["", "**Addendum changes (v2)**", ""] + [f"- {c}" for c in t["changes"]]
    lines += ["", "**Context**", "", f"- Backlog ID: {t['id']}", f"- Epic: {t['epic']} {t['epic_name']}",
              f"- Phase: {t['fix_version']}", f"- Target sprint: {sprint_name(t)}",
              f"- Agent role: {t['team']}"]
    if t["personas"]:
        lines.append(f"- Personas: {', '.join(t['personas'])}")
    if t["blocked"]:
        lines.append("- Blocked by: " + ", ".join(f"{b} ({by_id[b]['summary']})" for b in t["blocked"]))
    if t["blocks"]:
        lines.append("- Blocks: " + ", ".join(t["blocks"]))
    return "\n".join(lines)


def epic_description(e, markdown=False):
    h = "## " if markdown else "h3. "
    bullet = "- " if markdown else "* "
    return "\n".join([f"{h}Goal", e["goal"], "", f"{h}Definition of Done", e["dod"], "", f"{h}Scope",
                      f"{bullet}{e['tickets']} tickets, {e['points']} story points",
                      f"{bullet}Sprints {e['sprint_range']} ({e['phase']})",
                      f"{bullet}Component: {e['component']}"])


def sprint_name(t):
    return f"APL Sprint {t['sprint']}" if t["sprint"] else "not scheduled (Bac phase 2, after the paid launch)"


def fill(text, by_id):
    """Replace S{Tnnn} in a planning text with the sprint of ticket Tnnn."""
    return re.sub(r"S\{(T\d+)\}", lambda m: f"S{by_id[m.group(1)]['sprint']}", text)


def short(text, words=7):
    parts = text.split()
    return " ".join(parts[:words]) + ("…" if len(parts) > words else "")


def critical_chain(tid, by_id):
    """Walk back from a ticket through its latest-planned blocker (ties: the longer chain)."""
    depth = {}

    def chain_len(x):
        if x not in depth:
            depth[x] = 1 + max((chain_len(b) for b in by_id[x]["blocked"]), default=0)
        return depth[x]

    chain = [tid]
    while by_id[chain[-1]]["blocked"]:
        chain.append(max(by_id[chain[-1]]["blocked"], key=lambda b: (by_id[b]["sprint"], chain_len(b))))
    return chain[::-1]


def sprint_key(t):
    return (t["sprint"] or 99, int(t["id"][1:]))


def agent_label(team):
    return "agent-" + re.sub(r"[^a-z0-9]+", "-", team.split("(")[0].lower()).strip("-")


def write_csv(epics, tickets, by_id):
    n_labels = max(len(t["labels"]) + len(t["personas"]) + 1 for t in tickets)
    n_blocked = max(len(t["blocked"]) for t in tickets)
    header = ["Issue ID", "Issue Type", "Summary", "Description", "Priority", "Story Points", "Epic Name",
              "Epic Link", "Parent", "Components", "Sprint", "Fix Version", "Agent role"]
    header += ["Labels"] * n_labels + ["Blocked By"] * n_blocked
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for e in epics:
            labels = e["labels"][:n_labels]
            w.writerow([e["id"], "Epic", e["name"], epic_description(e), e["priority"], "", e["name"], "", "",
                        e["component"], "", e["phase"], ""] + labels + [""] * (n_labels - len(labels))
                       + [""] * n_blocked)
        for t in tickets:
            labels = t["labels"] + [f"persona-{p}" for p in t["personas"]] + [agent_label(t["team"])]
            w.writerow([t["id"], t["type"], t["summary"], wiki_description(t, by_id), t["priority"], t["points"],
                        "", t["epic_name"], t["epic"], t["component"], f"APL Sprint {t['sprint']}" if t["sprint"] else "",
                        t["fix_version"], t["team"]] + labels + [""] * (n_labels - len(labels))
                       + t["blocked"] + [""] * (n_blocked - len(t["blocked"])))


def load_jira_keys():
    if not JIRA_KEYS.exists():
        return {}
    with JIRA_KEYS.open(newline="", encoding="utf-8") as f:
        return {r["backlog_id"]: r["jira_key"] for r in csv.DictReader(f)}


def write_json(epics, tickets, by_id, keys):
    data = {
        "project": {"key": "APL", "name": "Kuizi", "jira_project": JIRA_PROJECT, "sprint_length_days": 14,
                    "first_sprint_start": SPRINT_START, "sprints": A.HORIZON},
        "epics": [dict(id=e["id"], jira_key=keys.get(e["id"]), summary=e["name"], priority=e["priority"],
                       phase=e["phase"], component=e["component"], labels=e["labels"],
                       description=epic_description(e, True))
                  for e in epics],
        "issues": [dict(id=t["id"], jira_key=keys.get(t["id"]), type=t["type"], epic=t["epic"],
                        summary=t["summary"], priority=t["priority"],
                        points=t["points"], sprint=f"APL Sprint {t['sprint']}" if t["sprint"] else None, component=t["component"],
                        team=t["team"], phase=t["fix_version"],
                        labels=t["labels"] + [f"persona-{p}" for p in t["personas"]] + [agent_label(t["team"]),
                                                                                       f"apl-{t['id'].lower()}"],
                        blocked_by=t["blocked"], description=markdown_description(t, by_id))
                   for t in tickets],
    }
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def v1_sections():
    text = SRC_MD.read_text(encoding="utf-8")
    sections = {}
    for chunk in re.split(r"\n(?=## )", text):
        if chunk.startswith("## "):
            title, _, body = chunk.partition("\n")
            sections[title[3:].strip()] = body.strip()
    return sections


def sprint_dates(n):
    from datetime import date, timedelta
    start = date.fromisoformat(SPRINT_START) + timedelta(days=14 * (n - 1))
    return start.isoformat(), (start + timedelta(days=13)).isoformat()


def write_markdown(epics, tickets, by_id, keys):
    v1 = v1_sections()
    total_pts = sum(t["points"] for t in tickets)
    teams = Counter(t["team"] for t in tickets)

    def jira(item_id):
        key = keys.get(item_id)
        return f"[{key}]({JIRA_BROWSE}{key})" if key else "—"

    out = []
    out.append("# Kuizi (APL) — Full Product Backlog v2\n")
    pilot, launch = by_id[A.PILOT_TICKET], by_id[A.LAUNCH_TICKET]
    out.append(f"**Backlog code:** `APL` · **Jira project:** `{JIRA_PROJECT}` (keys in `jira_keys.csv`) · "
               f"**Audience:** pupils of 6e année and 7e–9e année de base (about 11–15), age bands A and B · "
               f"**Subjects:** maths, éveil scientifique (6e), SVT (7e–9e), Arabic, French, English; the Bac follows "
               f"in phase 2 · **Milestones:** free pilot from S{pilot['sprint']} ({sprint_dates(pilot['sprint'])[0]}), "
               f"Neuvième 17–19 June and Sixième 21–23 June 2027 (S18), paid launch for 2027–28 in "
               f"S{launch['sprint']} ({sprint_dates(launch['sprint'])[0]}) · "
               f"**Horizon:** {A.HORIZON} two-week sprints starting {SPRINT_START} · "
               f"**Scope:** {len(epics)} epics · {len(tickets)} tickets · {total_pts} story points\n")
    out.append("> Generated by `tools/backlog/build_backlog.py` from the v1 backlog (`docs/backlog/source/`) and "
               "`tools/backlog/additions.py`. Do not edit by hand: change the data, rerun the script, then sync Jira "
               "(see `docs/backlog/README.md`).\n")

    later = [t for t in tickets if not t["sprint"]]
    new_ids = [t for t in tickets if int(t["id"][1:]) >= A.FIRST_ADR11_TICKET]
    gated = [t for t in tickets if set(t["blocked"]) & set(A.DESIGN_APPROVALS)]
    out.append("## What changed with ADR 0011 (6e–9e first, the Bac in phase 2)\n")
    out.append("On 2026-10-24 the product owner decided to start with 6e and 7e–9e année de base and the two concours "
               "instead of the Bac ([ADR 0011](../architecture/decisions/0011-start-with-6e-9e.md)). The plan "
               "follows the three studies: `docs/curriculum/college-6-9-scope.md`, `docs/product/market-6-9.md` and "
               "`docs/requirements/minors-11-15.md`.\n")
    out.append(f"- **Horizon:** {A.HORIZON} sprints instead of 20: a free pilot with partner private schools from "
               f"S{pilot['sprint']} to the June 2027 concours, its exit review after the results, and the paid launch "
               f"for the 2027–28 school year in S{launch['sprint']} with 30-day hypercare.")
    out.append(f"- **Re-scoped:** {len(A.REWRITES) + len(A.ADR11_SPLITS)} tickets rewritten for 6e–9e or split before "
               f"sprint entry (a change line on each says why), {len(A.EPIC_REWRITES)} epics renamed or re-scoped; "
               f"{len(A.ADR11_CHANGES)} tickets gain age-band or concours criteria (marked \"ADR 0011\").")
    out.append(f"- **Bac phase 2:** {len(later)} tickets ({sum(t['points'] for t in later)} points) stay in the backlog "
               f"without a sprint (label `phase-bac`); nothing scheduled depends on them.")
    out.append(f"- **New:** {len(new_ids)} tickets ({sum(t['points'] for t in new_ids)} points), T{A.FIRST_ADR11_TICKET}"
               f"–T{max(int(t['id'][1:]) for t in new_ids)}: the legal and age-band work of `minors-11-15.md` "
               f"(NEW-1 to NEW-12), design first (epic E21), writing assessment, mock concours papers, English, the "
               f"pilot exit review and the launch go-to-market plan.")
    out.append(f"- **Design gate:** {len(gated)} tickets that build what pupils, parents or teachers see are blocked "
               f"by the approved design of their journey ({', '.join(A.DESIGN_APPROVALS)}).\n")

    v2_epics = [e for e in epics if e["source"] == "v2"]
    out.append("## What changed from v1\n")
    out.append(f"v2 keeps all 132 v1 tickets and adds {len(v2_epics)} epics, "
               f"{sum(e['tickets'] for e in v2_epics)} tickets and {sum(e['points'] for e in v2_epics)} points in them. "
               f"{len(A.CHANGES)} v1 tickets gain acceptance criteria (marked \"Addendum changes (v2)\").\n")
    out.append("| Epic | Why it was added | Tickets | Points |\n| --- | --- | --- | --- |")
    for e in v2_epics:
        out.append(f"| {e['id']} {e['name']} | {A.EPIC_WHY[e['id']]} | {e['tickets']} | {e['points']} |")
    out.append("")

    out.append("## 1. Architecture this backlog builds\n")
    out.append(A.ARCHITECTURE + "\n")
    out.append("**v2 additions to the architecture.** Four services join the platform: the Learner Comfort Profile "
               "(E14), the Speech service (E14), the Notification Orchestrator (E15) and the accessible content "
               "pipeline (E14). Native learner apps (E16) consume the same APIs and widget package. See "
               "`docs/architecture/overview.md`.\n")
    out.append("### Kuizi Neural Core → tickets\n")
    out.append("The Neural Core infographic (`docs/assets/kuizi-neural-core.jpg`) maps to these tickets:\n")
    out.append("| Neural Core element | Tickets |\n| --- | --- |")
    for element, refs in A.NEURAL_CORE:
        out.append(f"| {element} | {refs} |")
    out.append("")

    out.append("## 2. Delivery model and agent roles\n")
    out.append("Kuizi has no human delivery team. Each ticket is done by the AI agent of its owning role, working "
               "with the product owner, who is the Jira assignee on every ticket, briefs the agent, reviews its work "
               "and accepts it against the acceptance criteria (ADR 0005). Every ticket has one owning agent role "
               "(label `agent-*`) and, for user stories, the personas it serves.\n")
    v1_role_rows = [l for l in v1["2. Teams and capacity"].splitlines() if l.startswith("| ") and "---" not in l][1:]
    out.append("| Agent role | Label | Owns | Tickets | Points |\n| --- | --- | --- | --- | --- |")
    pts_by_role = Counter()
    for t in tickets:
        pts_by_role[t["team"]] += t["points"]
    roles = [(c[0], A.ROLE_SCOPE.get(c[0], c[2])) for c in ([x.strip() for x in row.strip("|").split("|")] for row in v1_role_rows)]
    for name, owns in roles + A.NEW_ROLES:
        out.append(f"| {name} | `{agent_label(name)}` | {owns} | {teams.get(name, 0)} | {pts_by_role.get(name, 0)} |")
    out.append("")
    out.append("**Sprint capacity.** The plan keeps a ceiling of 134 points per sprint. With agents doing the work, "
               "the real limit is how much the product owner can brief, review and accept in two weeks: velocity "
               "measured in S1 and S2 resets the ceiling and the plan is rebalanced then.\n")
    persona_counts = Counter(p for t in tickets for p in t["personas"])
    out.append("**Personas served by user stories.**\n")
    out.append("| Persona | Stories |\n| --- | --- |")
    for p, n in persona_counts.most_common():
        out.append(f"| {p} | {n} |")
    out.append("")

    out.append("## 3. Roadmap by phase\n")
    out.append("| Phase | Sprints | Dates | Focus |\n| --- | --- | --- | --- |")
    for name, first, last in A.PHASES:
        out.append(f"| {name} | S{first}–S{last} | {sprint_dates(first)[0]} → {sprint_dates(last)[1]} | "
                   f"{A.PHASE_FOCUS[name]} |")
    out.append(f"| {A.BAC_PHASE} | not scheduled | after the paid launch | {A.PHASE_FOCUS[A.BAC_PHASE]} |")
    out.append("")
    out.append("**Milestones**\n")
    out += [f"- {fill(m, by_id)}" for m in A.MILESTONES]
    out.append("")
    out.append("### Sprint calendar and load\n")
    out.append("| Sprint | Dates | Tickets | Points | Capacity | Epics active |\n| --- | --- | --- | --- | --- | --- |")
    for n in range(1, A.HORIZON + 1):
        mine = [t for t in tickets if t["sprint"] == n]
        start, end = sprint_dates(n)
        ep = ", ".join(sorted({t["epic"] for t in mine}, key=lambda x: int(x[1:])))
        out.append(f"| S{n} | {start} – {end} | {len(mine)} | {sum(t['points'] for t in mine)} | "
                   f"{A.CAPACITY.get(n, A.CEILING)} | {ep} |")
    if later:
        ep = ", ".join(sorted({t["epic"] for t in later}, key=lambda x: int(x[1:])))
        out.append(f"| Bac phase 2 | after the paid launch, not scheduled | {len(later)} | "
                   f"{sum(t['points'] for t in later)} | — | {ep} |")
    out.append("")
    over = [n for n in range(1, A.HORIZON + 1)
            if sum(t["points"] for t in tickets if t["sprint"] == n) > A.CAPACITY.get(n, A.CEILING)]
    note = (f" {', '.join(f'S{n}' for n in over)} carries more than its planned capacity only because finished work "
            "was pulled in (T040 into S1)." if over else "")
    out.append("Capacity ramps up over S1–S5, then the 134-point ceiling applies until the S1–S2 velocity resets it. "
               f"The Sprint 1 and Sprint 2 tickets are done or in review and keep their sprints.{note}\n")

    out.append("## 4. Epic summary\n")
    out.append("| ID | Epic | Phase | Priority | Tickets | Points | Sprints |\n| --- | --- | --- | --- | --- | --- | --- |")
    for e in epics:
        out.append(f"| {e['id']} | {e['name']} | {e['phase']} | {e['priority']} | {e['tickets']} | {e['points']} | "
                   f"{e['sprint_range']} |")
    out.append("")

    out.append("## 5. Critical path\n")
    out.append("Each chain walks back from a milestone through the blocker planned latest, so it shows what "
               "gates the milestone in the current plan. A slip anywhere on a chain moves the milestone.\n")
    for label, tid in (("Free pilot", A.PILOT_TICKET), ("Paid launch", A.LAUNCH_TICKET)):
        chain = critical_chain(tid, by_id)
        out.append(f"**{label} ({tid}, S{by_id[tid]['sprint']}):** "
                   + " → ".join(f"`{x}` {short(by_id[x]['summary'])} (S{by_id[x]['sprint']})" for x in chain) + "\n")
    out.append(fill(A.CRITICAL_NOTES, by_id) + "\n")

    out.append("## 6. Backlog detail\n")
    out.append("Conventions: story points are Fibonacci (13 = split before sprint entry); *Blocked by* references "
               "the IDs in this file and in the CSV; labels `agent-*` and `persona-*` carry the agent role and persona.\n")
    for e in epics:
        mine = [t for t in tickets if t["epic"] == e["id"]]
        out.append(f"### {e['id']} — {e['name']}\n")
        out.append(f"**Jira:** {jira(e['id'])} · **Phase:** {e['phase']} · **Priority:** {e['priority']} · "
                   f"**Component:** {e['component']} · **{e['tickets']} tickets / {e['points']} pts**\n")
        out.append(f"**Goal.** {e['goal']}\n")
        out.append(f"**Definition of done.** {e['dod']}\n")
        out.append("| ID | Jira | Type | Summary | Pts | Priority | Sprint | Agent role | Blocked by |\n"
                   "| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for t in sorted(mine, key=sprint_key):
            out.append(f"| {t['id']} | {jira(t['id'])} | {t['type']} | {t['summary']} | {t['points']} | "
                       f"{t['priority']} | {'S' + str(t['sprint']) if t['sprint'] else 'Bac phase 2'} | {t['team']} | "
                       f"{', '.join(t['blocked']) or '—'} |")
        out.append("")
        for t in sorted(mine, key=sprint_key):
            out.append(f"#### {t['id']} · {t['summary']}\n")
            meta = (f"*Jira {keys.get(t['id'], 'not synced')} · {t['type']} · {t['points']} pts · {t['priority']} · "
                    f"{sprint_name(t)} · {t['team']}")
            if t["personas"]:
                meta += f" · personas: {', '.join(t['personas'])}"
            out.append(meta + f" · labels: {', '.join(t['labels'])}*\n")
            out.append(t["desc"] + "\n")
            out.append("Acceptance criteria:\n")
            out += [f"- {a}" for a in t["ac"]]
            if t["changes"]:
                out.append("\nAddendum changes (v2):\n")
                out += [f"- {c}" for c in t["changes"]]
            if t["blocked"]:
                out.append("\nBlocked by: " + ", ".join(f"{b} ({by_id[b]['summary']})" for b in t["blocked"]))
            if t["blocks"]:
                out.append("\nBlocks: " + ", ".join(t["blocks"]))
            out.append("")
    OUT_MD.write_text("\n".join(out) + "\n", encoding="utf-8")


def main():
    epics, tickets, by_id = build()
    keys = load_jira_keys()
    write_csv(epics, tickets, by_id)
    write_json(epics, tickets, by_id, keys)
    write_markdown(epics, tickets, by_id, keys)
    pts = Counter()
    for t in tickets:
        pts[t["sprint"]] += t["points"]
    print(f"{len(epics)} epics, {len(tickets)} tickets, {sum(t['points'] for t in tickets)} points, "
          f"{sum(len(t['blocked']) for t in tickets)} dependency links")
    print("points per sprint:", dict(sorted(pts.items())))
    print("tickets per agent role:", dict(Counter(t["team"] for t in tickets)))
    missing = [i["id"] for i in epics + tickets if i["id"] not in keys]
    stale = sorted(set(keys) - {i["id"] for i in epics + tickets})
    print(f"Jira {JIRA_PROJECT}: {len(epics) + len(tickets) - len(missing)} items mapped in jira_keys.csv"
          + (f"; not yet in Jira: {', '.join(missing)}" if missing else "")
          + (f"; mapped but no longer in the backlog: {', '.join(stale)}" if stale else ""))


if __name__ == "__main__":
    main()
