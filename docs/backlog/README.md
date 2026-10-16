# Backlog: how it is maintained and synced to Jira

The repository is the source of truth for the backlog. Jira project **Kuizi Adaptive Bac Platform** (key `APL`, company-managed Scrum) mirrors it.

## Files

| File | Role | Edit? |
| --- | --- | --- |
| `source/APL_Production_Backlog_v1.md`, `.docx`, `source/APL_jira_import_v1.csv` | v1 backlog as received (13 epics, 132 tickets, 1,041 points) | Never |
| `../../tools/backlog/additions.py` | Everything added or changed after v1: epics E14–E20, tickets T133–T210, changes to v1 tickets, team list, Neural Core mapping | Yes, this is where changes go |
| `../../tools/backlog/build_backlog.py` | Generator | Only to change output formats |
| `APL_Full_Backlog.md` | Full readable backlog v2 (20 epics, 210 tickets, 1,496 points) | Generated |
| `APL_jira_import_full.csv` | Jira CSV import file, same columns as v1 plus team and persona labels | Generated |
| `apl_backlog.json` | Input for the API sync (Markdown descriptions, labels, links) | Generated |

Regenerate after any change:

```bash
python3 tools/backlog/build_backlog.py
```

The script fails if a ticket ID is duplicated, a dependency points to an unknown ticket, an epic is missing or points are not Fibonacci. It prints points per sprint: keep every sprint at or below capacity (134 points with the four added engineers, 110 without).

## Jira project setup (once)

1. Create the project: **Projects → Create project → Scrum → Company-managed**, name `Kuizi Adaptive Bac Platform`, key `APL`.
2. Components, one per owning team: Platform, Security, Data, Curriculum, ML, Backend, LLM, Frontend, QA, Mobile, Accessibility, Design, Growth, Support, Legal.
3. Versions, one per phase: `Phase 0 — Foundations` … `Phase 6 — Subject Expansion`.
4. Sprints `APL Sprint 1` … `APL Sprint 20` on the APL board, two weeks each, S1 starting 2026-11-02.
5. Issue types: Epic, Story, Task. Jira has no Spike type by default: spikes are Tasks with the label `spike`.

## Field mapping

| Backlog | Jira |
| --- | --- |
| Ticket ID `T###` | Label `apl-t###` (and the ID in the description's Context section) |
| Epic `E##` | Epic issue; tickets are its children (Parent) |
| Type | Issue type (Spike → Task + label `spike`) |
| Summary, description, acceptance criteria | Summary, Description |
| Priority | Priority |
| Points | Story Points |
| Sprint | Sprint `APL Sprint N` |
| Phase | Fix version |
| Team | Component + label `team-*` |
| Personas | Labels `persona-*` |
| Blocked by | Issue link "is blocked by" |

## Two ways to load or resync

**A. CSV import (fastest for the first load).** Jira settings → System → External system import → CSV, file `APL_jira_import_full.csv`. Map `Issue ID` to the issue key placeholder, `Parent` to the epic link, `Blocked By` to the "Blocks" link type, `Sprint`, `Story Points`, `Components`, `Fix Version` and every `Labels` column.

**B. API sync through Claude (used for every later change).** Claude reads `apl_backlog.json` and creates or updates issues through the Atlassian connector, finding existing issues by their `apl-t###` label. This is the path `CLAUDE.md` requires at the end of every session that changes the backlog.

## Change procedure

1. Edit `tools/backlog/additions.py`.
2. Regenerate and check totals and sprint loads.
3. Sync Jira (path B) for the changed tickets only.
4. Add a line to `CHANGELOG.md`.
