# Backlog: how it is maintained and synced to Jira

The repository is the source of truth for the backlog. Jira project **`KK`** (team-managed Scrum, [board 37](https://kuizi.atlassian.net/jira/software/projects/KK/boards/37)) mirrors it.

## Files

| File | Role | Edit? |
| --- | --- | --- |
| `source/APL_Production_Backlog_v1.md`, `.docx`, `source/APL_jira_import_v1.csv` | v1 backlog as received (13 epics, 132 tickets, 1,041 points) | Never |
| `../../tools/backlog/additions.py` | Everything added or changed after v1: epics E14–E20, tickets T133–T236, changes to v1 tickets, team list, Neural Core mapping | Yes, this is where changes go |
| `../../tools/backlog/build_backlog.py` | Generator | Only to change output formats |
| `jira_keys.csv` | Backlog ID → Jira key (`E05,KK-5`, `T103,KK-134`) | Yes, add a row whenever an issue is created in Jira |
| `APL_Full_Backlog.md` | Full readable backlog v2 (20 epics, 236 tickets, 1,612 points), with Jira keys | Generated |
| `APL_jira_import_full.csv` | Jira CSV import file, same columns as v1 plus team and persona labels | Generated |
| `apl_backlog.json` | Input for the API sync (Markdown descriptions, labels, links, Jira keys) | Generated |

Regenerate after any change:

```bash
python3 tools/backlog/build_backlog.py
```

The script fails if a ticket ID is duplicated, a dependency points to an unknown ticket, an epic is missing or points are not Fibonacci. It prints points per sprint: keep every sprint at or below capacity (134 points with the four added engineers, 110 without). It also lists backlog items that have no Jira key yet.

## Jira project state

Loaded on 2026-10-16 through the Atlassian connector:

- 20 epics, KK-1 to KK-20, in backlog order (E05 is KK-5).
- 236 tickets, KK-21 to KK-256, each a child of its epic. Keys follow `20 + ticket number`, except T104–T114 (KK-123 to KK-133) and T103 (KK-134). `jira_keys.csv` has every key.
- 426 "Blocks" links reproduce every *Blocked by* in the backlog.
- The gap review of the same day added T211–T236 (KK-231 to KK-256): foundations, safeguarding, teacher and school-admin tools, mobile quality and content operations.
- The Neural Core infographic sits in a comment on KK-5.
- On 2026-10-17, after Backlog, Sprints and Estimation were turned on, the 20 sprints were created, every ticket was put in its sprint and given its story-point estimate (field `Story point estimate`, `customfield_10016`; the board estimates by it). Each sprint's goal names its phase and the three epics carrying the most points in it.

| Sprint | Jira sprint ID | Start | End | Tickets | Points |
| --- | --- | --- | --- | --- | --- |
| APL Sprint 1 | 440 | 2026-11-02 | 2026-11-13 | 3 | 12 |
| APL Sprint 2 | 441 | 2026-11-16 | 2026-11-27 | 6 | 37 |
| APL Sprint 3 | 442 | 2026-11-30 | 2026-12-11 | 11 | 63 |
| APL Sprint 4 | 443 | 2026-12-14 | 2026-12-25 | 11 | 76 |
| APL Sprint 5 | 444 | 2026-12-28 | 2027-01-08 | 12 | 73 |
| APL Sprint 6 | 445 | 2027-01-11 | 2027-01-22 | 17 | 123 |
| APL Sprint 7 | 446 | 2027-01-25 | 2027-02-05 | 16 | 116 |
| APL Sprint 8 | 447 | 2027-02-08 | 2027-02-19 | 14 | 131 |
| APL Sprint 9 | 448 | 2027-02-22 | 2027-03-05 | 17 | 134 |
| APL Sprint 10 | 449 | 2027-03-08 | 2027-03-19 | 20 | 133 |
| APL Sprint 11 | 450 | 2027-03-22 | 2027-04-02 | 16 | 132 |
| APL Sprint 12 | 451 | 2027-04-05 | 2027-04-16 | 21 | 131 |
| APL Sprint 13 | 452 | 2027-04-19 | 2027-04-30 | 16 | 112 |
| APL Sprint 14 | 453 | 2027-05-03 | 2027-05-14 | 19 | 131 |
| APL Sprint 15 | 454 | 2027-05-17 | 2027-05-28 | 16 | 102 |
| APL Sprint 16 | 455 | 2027-05-31 | 2027-06-11 | 12 | 65 |
| APL Sprint 17 | 456 | 2027-06-14 | 2027-06-25 | 4 | 16 |
| APL Sprint 18 | 457 | 2027-06-28 | 2027-07-09 | 2 | 10 |
| APL Sprint 19 | 458 | 2027-07-12 | 2027-07-23 | 2 | 10 |
| APL Sprint 20 | 459 | 2027-07-26 | 2027-08-06 | 1 | 5 |

Jira sprint ID = 439 + sprint number. To move a ticket, change its sprint in `additions.py`, regenerate, then in Jira move it to the new sprint and update its `sprint-NN` label.

Still to do in Jira (the connector cannot do these):

1. **Rename the project.** Project settings → Details → Name `Kuizi Adaptive Bac Platform`, keep key `KK`. It is currently named `Kuizi_KPI`.
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
| Team | Label `team-*` (team-managed projects have no components) |
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
