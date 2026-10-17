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
SPRINT_START = "2026-11-02"
PHASE_ORDER = ["Phase 0", "Phase 1", "Phase 2", "Phase 3", "Phase 4", "Phase 5", "Phase 6"]
PERSONAS = [
    (r"^As a (maths |sciences |sciences-techniques |éco/gestion |new |dyslexic |screen-reader |blind or low-vision |iPad )?student or parent", ["student", "parent"]),
    (r"^As an? (maths |sciences |sciences-techniques |éco/gestion |new |dyslexic |anxious |iPad )?student", ["student"]),
    (r"^As a screen-reader user", ["student"]),
    (r"^As a blind", ["student"]),
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
    for tid, sprint in A.SPRINT_OVERRIDES.items():
        by_id[tid]["sprint"] = sprint
    for tid, extra in A.EXTRA_BLOCKERS.items():
        by_id[tid]["blocked"] += [b for b in extra if b not in by_id[tid]["blocked"]]

    epic_by_id = {e["id"]: e for e in epics}
    # In v1 epics a ticket's phase follows its sprint; new tickets in those epics do the same.
    # v2 epics keep one phase for all their tickets.
    sprint_phase = {s: Counter(t["fix_version"] for t in tickets if t["sprint"] == s).most_common(1)[0][0]
                    for s in {t["sprint"] for t in tickets}}
    v1_epics = {e["id"] for e in epics}
    for e in A.EPICS:
        e = dict(e, source="v2")
        epics.append(e)
        epic_by_id[e["id"]] = e
    for t in A.TICKETS:
        phase = sprint_phase[t["sprint"]] if t["epic"] in v1_epics else epic_by_id[t["epic"]]["phase"]
        t = dict(t, component=A.TEAM_COMPONENT[t["team"]], fix_version=phase,
                 changes=[], source="v2")
        tickets.append(t)
        by_id[t["id"]] = t

    # Integrity checks.
    ids = [t["id"] for t in tickets]
    dupes = [i for i, n in Counter(ids).items() if n > 1]
    assert not dupes, f"duplicate ticket ids: {dupes}"
    for t in tickets:
        for b in t["blocked"]:
            assert b in by_id, f"{t['id']} blocked by unknown {b}"
        assert t["epic"] in epic_by_id, f"{t['id']} has unknown epic {t['epic']}"
        assert t["points"] in (1, 2, 3, 5, 8, 13), f"{t['id']} has non-Fibonacci points"

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
    return epics, tickets, by_id


def wiki_description(t, by_id):
    lines = ["h3. Description", t["desc"], "", "h3. Acceptance Criteria"]
    lines += [f"* {a}" for a in t["ac"]]
    if t["changes"]:
        lines += ["", "h3. Addendum changes (v2)"] + [f"* {c}" for c in t["changes"]]
    lines += ["", "h3. Context", f"* Epic: {t['epic_name']}", f"* Phase: {t['fix_version']}",
              f"* Target sprint: APL Sprint {t['sprint']}", f"* Agent role: {t['team']}"]
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
              f"- Phase: {t['fix_version']}", f"- Target sprint: APL Sprint {t['sprint']}",
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
                        "", t["epic_name"], t["epic"], t["component"], f"APL Sprint {t['sprint']}",
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
                    "first_sprint_start": SPRINT_START, "sprints": 20},
        "epics": [dict(id=e["id"], jira_key=keys.get(e["id"]), summary=e["name"], priority=e["priority"],
                       phase=e["phase"], component=e["component"], labels=e["labels"],
                       description=epic_description(e, True))
                  for e in epics],
        "issues": [dict(id=t["id"], jira_key=keys.get(t["id"]), type=t["type"], epic=t["epic"],
                        summary=t["summary"], priority=t["priority"],
                        points=t["points"], sprint=f"APL Sprint {t['sprint']}", component=t["component"],
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
    out.append(f"**Backlog code:** `APL` · **Jira project:** `{JIRA_PROJECT}` (keys in `jira_keys.csv`) · "
               f"**Subjects:** Physics, Mathématiques, Sciences (SVT / Chimie), Sciences "
               f"techniques, Économie & Gestion · **Horizon:** 20 two-week sprints starting {SPRINT_START} · "
               f"**Scope:** {len(epics)} epics · {len(tickets)} tickets · {total_pts} story points\n")
    out.append("> Generated by `tools/backlog/build_backlog.py` from the v1 backlog (`docs/backlog/source/`) and "
               "`tools/backlog/additions.py`. Do not edit by hand: change the data, rerun the script, then sync Jira "
               "(see `docs/backlog/README.md`).\n")
    v2_epics = [e for e in epics if e["source"] == "v2"]
    out.append("## What changed from v1\n")
    out.append(f"v2 keeps all 132 v1 tickets and adds {len(v2_epics)} epics, "
               f"{sum(e['tickets'] for e in v2_epics)} tickets and {sum(e['points'] for e in v2_epics)} points. "
               f"{len(A.CHANGES)} v1 tickets gain acceptance criteria (marked \"Addendum changes (v2)\").\n")
    out.append("| Epic | Why it was added | Tickets | Points |\n| --- | --- | --- | --- |")
    why = {"E14": "Full accessibility for students with different needs (WCAG 2.2 AA, accommodations, fairness)",
           "E15": "Focus sessions and notifications that respect quiet hours, class hours and exams",
           "E16": "Native iOS and Android apps and App Store / Google Play rules",
           "E17": "The learner screens of the design canvas and the Cyanotype design system in code",
           "E18": "Mock Bac, annales library and the estimated Bac grade shown in the design",
           "E19": "KPIs, marketing site, B2C checkout, store listings, evidence for public claims",
           "E20": "Admin console, feature flags, moderation, help center, support desk, legal documents"}
    for e in v2_epics:
        out.append(f"| {e['id']} {e['name']} | {why[e['id']]} | {e['tickets']} | {e['points']} |")
    out.append("")

    out.append("## 1. Architecture this backlog builds\n")
    out.append(v1["1. Architecture this backlog builds"] + "\n")
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
    roadmap = v1["3. Roadmap by phase"].split("### Sprint calendar and load")[0].strip()
    out.append(roadmap + "\n")
    out.append("### Sprint calendar and load\n")
    out.append("| Sprint | Dates | Tickets | Points | Epics active |\n| --- | --- | --- | --- | --- |")
    for n in range(1, 21):
        mine = [t for t in tickets if t["sprint"] == n]
        start, end = sprint_dates(n)
        ep = ", ".join(sorted({t["epic"] for t in mine}, key=lambda x: int(x[1:])))
        out.append(f"| S{n} | {start} – {end} | {len(mine)} | {sum(t['points'] for t in mine)} | {ep} |")
    out.append("")

    out.append("## 4. Epic summary\n")
    out.append("| ID | Epic | Phase | Priority | Tickets | Points | Sprints |\n| --- | --- | --- | --- | --- | --- | --- |")
    for e in epics:
        out.append(f"| {e['id']} | {e['name']} | {e['phase']} | {e['priority']} | {e['tickets']} | {e['points']} | "
                   f"{e['sprint_range']} |")
    out.append("")

    out.append("## 5. Critical path\n")
    out.append(v1["5. Critical path"] + "\n")
    out.append("v2 adds no ticket to the critical path. Three v2 tickets gate it: T148 must land before the first "
               "champion/challenger gate (T047, S9), and go-live (T110) now also needs T150 (accessibility gate), "
               "T207 (legal documents) and T169 (store compliance).\n")

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
        for t in sorted(mine, key=lambda t: (t["sprint"], int(t["id"][1:]))):
            out.append(f"| {t['id']} | {jira(t['id'])} | {t['type']} | {t['summary']} | {t['points']} | "
                       f"{t['priority']} | S{t['sprint']} | {t['team']} | {', '.join(t['blocked']) or '—'} |")
        out.append("")
        for t in sorted(mine, key=lambda t: (t["sprint"], int(t["id"][1:]))):
            out.append(f"#### {t['id']} · {t['summary']}\n")
            meta = (f"*Jira {keys.get(t['id'], 'not synced')} · {t['type']} · {t['points']} pts · {t['priority']} · "
                    f"APL Sprint {t['sprint']} · {t['team']}")
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
