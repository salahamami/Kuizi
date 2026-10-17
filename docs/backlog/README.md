# Backlog: how it is maintained and synced to Jira

The repository is the source of truth for the backlog. Jira project **`KK`** (team-managed Scrum, [board 37](https://kuizi.atlassian.net/jira/software/projects/KK/boards/37)) mirrors it.

## Files

| File | Role | Edit? |
| --- | --- | --- |
| `source/APL_Production_Backlog_v1.md`, `.docx`, `source/APL_jira_import_v1.csv` | v1 backlog as received (13 epics, 132 tickets, 1,041 points) | Never |
| `../../tools/backlog/additions.py` | Everything added or changed after v1: epics E14–E20, tickets T133–T240, changes to v1 tickets, agent roles, Neural Core mapping | Yes, this is where changes go |
| `../../tools/backlog/build_backlog.py` | Generator | Only to change output formats |
| `jira_keys.csv` | Backlog ID → Jira key (`E05,KK-5`, `T103,KK-134`) | Yes, add a row whenever an issue is created in Jira |
| `APL_Full_Backlog.md` | Full readable backlog v2 (20 epics, 240 tickets, 1,636 points), with Jira keys | Generated |
| `APL_jira_import_full.csv` | Jira CSV import file, same columns as v1 plus agent-role and persona labels | Generated |
| `apl_backlog.json` | Input for the API sync (Markdown descriptions, labels, links, Jira keys) | Generated |

Regenerate after any change:

```bash
python3 tools/backlog/build_backlog.py
```

The script fails if a ticket ID is duplicated, a dependency points to an unknown ticket, an epic is missing or points are not Fibonacci. It prints points per sprint: keep every sprint at or below the 134-point planning ceiling. Work is done by role agents with the product owner (ADR 0005), so the ceiling is reset from the velocity measured in Sprints 1 and 2. It also lists backlog items that have no Jira key yet.

## Jira project state

Project name **Kuizi Adaptive Bac Platform** (renamed from `Kuizi_KPI` on 2026-10-17). Loaded on 2026-10-16 through the Atlassian connector:

- 20 epics, KK-1 to KK-20, in backlog order (E05 is KK-5).
- 240 tickets, KK-21 to KK-260, each a child of its epic. Keys follow `20 + ticket number`, except T104–T114 (KK-123 to KK-133) and T103 (KK-134). `jira_keys.csv` has every key.
- "Blocks" links reproduce every *Blocked by* in the backlog (440 links), plus 17 obsolete links still to be removed by hand (see `CHANGELOG.md`, "Pending Jira sync").
- The gap review of the same day added T211–T236 (KK-231 to KK-256): foundations, safeguarding, teacher and school-admin tools, mobile quality and content operations.
- The Neural Core infographic sits in a comment on KK-5.
- On 2026-10-17, after Backlog, Sprints and Estimation were turned on, the 20 sprints were created, every ticket was put in its sprint and given its story-point estimate (field `Story point estimate`, `customfield_10016`; the board estimates by it). Each sprint's goal names its phase and the three epics carrying the most points in it.
- The same day the delivery model changed to role agents with one product owner (ADR 0005): every ticket's `team-*` label became `agent-*`, its description says "Agent role", and the product owner is the assignee on all 236 tickets.
- Still on 2026-10-17, the plan became local-first (ADR 0006): T237–T240 were added (KK-257 to KK-260), 143 tickets moved sprint, their labels and descriptions were regenerated, 17 epic descriptions and 17 sprint goals were updated. The sprint plan comes from `tools/backlog/replan.py`.

| Sprint | Jira sprint ID | Start | End | Tickets | Points |
| --- | --- | --- | --- | --- | --- |
| APL Sprint 1 | 440 | 2026-10-17 | 2026-10-30 | 3 | 13 |
| APL Sprint 2 | 441 | 2026-11-02 | 2026-11-13 | 6 | 37 |
| APL Sprint 3 | 442 | 2026-11-16 | 2026-11-27 | 10 | 65 |
| APL Sprint 4 | 443 | 2026-11-30 | 2026-12-11 | 10 | 79 |
| APL Sprint 5 | 444 | 2026-12-14 | 2026-12-25 | 11 | 90 |
| APL Sprint 6 | 445 | 2026-12-28 | 2027-01-08 | 12 | 74 |
| APL Sprint 7 | 446 | 2027-01-11 | 2027-01-22 | 12 | 113 |
| APL Sprint 8 | 447 | 2027-01-25 | 2027-02-05 | 15 | 120 |
| APL Sprint 9 | 448 | 2027-02-08 | 2027-02-19 | 21 | 133 |
| APL Sprint 10 | 449 | 2027-02-22 | 2027-03-05 | 20 | 132 |
| APL Sprint 11 | 450 | 2027-03-08 | 2027-03-19 | 18 | 132 |
| APL Sprint 12 | 451 | 2027-03-22 | 2027-04-02 | 17 | 132 |
| APL Sprint 13 | 452 | 2027-04-05 | 2027-04-16 | 21 | 132 |
| APL Sprint 14 | 453 | 2027-04-19 | 2027-04-30 | 21 | 133 |
| APL Sprint 15 | 454 | 2027-05-03 | 2027-05-14 | 19 | 134 |
| APL Sprint 16 | 455 | 2027-05-17 | 2027-05-28 | 17 | 86 |
| APL Sprint 17 | 456 | 2027-05-31 | 2027-06-11 | 2 | 6 |
| APL Sprint 18 | 457 | 2027-06-14 | 2027-06-25 | 2 | 10 |
| APL Sprint 19 | 458 | 2027-06-28 | 2027-07-09 | 2 | 10 |
| APL Sprint 20 | 459 | 2027-07-12 | 2027-07-23 | 1 | 5 |

Jira sprint ID = 439 + sprint number. To move a ticket, change its sprint in `additions.py` (or rerun `python3 tools/backlog/replan.py` when capacity changes), regenerate, then in Jira move it to the new sprint and update its `sprint-NN` and `phase-N` labels and description.

Still to do in Jira (the connector cannot do these):

1. **Remove 17 obsolete "Blocks" links** left by the local-first re-plan; the list is in `CHANGELOG.md` under "Pending Jira sync". The connector can create issue links but not delete them.
2. Optional: add the Releases view to get one version per phase (the label `phase-N` already carries it). On this site Releases is not listed under Features; add it as a tab with **+** in the space navigation, as for Backlog. The `fixVersions` field only appears on tickets once that view exists.

Issue types on this site are French: `Epic`, `Story`, `Tâche` (Task). Jira has no Spike type, so spikes are `Tâche` with the label `spike`.

## Field mapping

| Backlog | Jira `KK` |
| --- | --- |
| Ticket ID `T###` | Label `apl-t###`, summary prefix `T### ·`, and the ID in the description's Context section |
| Epic `E##` | Epic `KK-1`…`KK-20` (summary `E## · name`, label `apl-e##`); tickets are its children (Parent) |
| Type | Story → `Story`; Task and Spike → `Tâche` (Spike adds label `spike`) |
| Summary, description, acceptance criteria | Summary, Description (Markdown) |
| Priority | Priority |
| Points | Field "Story point estimate" (`customfield_10016`) and the "Story points: N" line in the description |
| Sprint | Sprint `APL Sprint N` (Jira sprint ID 439 + N) and label `sprint-NN` |
| Phase | Label `phase-N` |
| Agent role | Label `agent-*` (team-managed projects have no components) and the "Agent role" line in the description |
| Owner | Assignee: the product owner on every ticket |
| Personas | Labels `persona-*` |
| Blocked by | Issue link "Blocks" (blocker blocks the ticket) |

## Two ways to load or resync

**A. API sync through Claude (used for the first load and for every later change).** Claude reads `apl_backlog.json` and creates or updates issues through the Atlassian connector. It finds existing issues through `jira_key` (from `jira_keys.csv`) or the `apl-t###` label. This is the path `CLAUDE.md` requires at the end of every session that changes the backlog.

**B. CSV import (only to rebuild a project from scratch).** Jira settings → System → External system import → CSV, file `APL_jira_import_full.csv`. Map `Issue ID` to the issue key placeholder, `Parent` to the epic link, `Blocked By` to the "Blocks" link type, `Sprint`, `Story Points` and every `Labels` column. Afterwards, rewrite `jira_keys.csv` with the new keys.

## Change procedure

1. Edit `tools/backlog/additions.py`.
2. Regenerate and check totals and sprint loads.
3. Sync Jira (path A) for the changed tickets only; add new keys to `jira_keys.csv` and regenerate.
4. Add a line to `CHANGELOG.md`.
