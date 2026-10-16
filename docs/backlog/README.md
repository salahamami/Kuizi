# Backlog: how it is maintained and synced to Jira

The repository is the source of truth for the backlog. Jira project **`KK`** (team-managed Scrum, [board 37](https://kuizi.atlassian.net/jira/software/projects/KK/boards/37)) mirrors it.

## Files

| File | Role | Edit? |
| --- | --- | --- |
| `source/APL_Production_Backlog_v1.md`, `.docx`, `source/APL_jira_import_v1.csv` | v1 backlog as received (13 epics, 132 tickets, 1,041 points) | Never |
| `../../tools/backlog/additions.py` | Everything added or changed after v1: epics E14–E20, tickets T133–T210, changes to v1 tickets, team list, Neural Core mapping | Yes, this is where changes go |
| `../../tools/backlog/build_backlog.py` | Generator | Only to change output formats |
| `jira_keys.csv` | Backlog ID → Jira key (`E05,KK-5`, `T103,KK-134`) | Yes, add a row whenever an issue is created in Jira |
| `APL_Full_Backlog.md` | Full readable backlog v2 (20 epics, 210 tickets, 1,496 points), with Jira keys | Generated |
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
- 210 tickets, KK-21 to KK-230, each a child of its epic. Keys follow `20 + ticket number`, except T104–T114 (KK-123 to KK-133) and T103 (KK-134). `jira_keys.csv` has every key.
- 351 "Blocks" links reproduce every *Blocked by* in the backlog.
- The Neural Core infographic sits in a comment on KK-5.

Still to do in Jira (the connector cannot do these):

1. **Rename the project.** Project settings → Details → Name `Kuizi Adaptive Bac Platform`, keep key `KK`. It is currently named `Kuizi_KPI`.
2. **Turn on Sprints.** Project settings → Features → Sprints (this also turns on story-point estimation). Then the next session creates `APL Sprint 1` … `APL Sprint 20` (two weeks each, S1 from 2026-11-02), puts every ticket in its sprint (label `sprint-NN`) and sets the estimate from the "Story points" line.
3. Optional: turn on Releases to get one version per phase (the label `phase-N` already carries it).

Issue types on this site are French: `Epic`, `Story`, `Tâche` (Task). Jira has no Spike type, so spikes are `Tâche` with the label `spike`.

## Field mapping

| Backlog | Jira `KK` |
| --- | --- |
| Ticket ID `T###` | Label `apl-t###`, summary prefix `T### ·`, and the ID in the description's Context section |
| Epic `E##` | Epic `KK-1`…`KK-20` (summary `E## · name`, label `apl-e##`); tickets are its children (Parent) |
| Type | Story → `Story`; Task and Spike → `Tâche` (Spike adds label `spike`) |
| Summary, description, acceptance criteria | Summary, Description (Markdown) |
| Priority | Priority |
| Points | "Story points: N" line in the description; the estimate field once Sprints is on |
| Sprint | Label `sprint-NN`; the sprint `APL Sprint N` once Sprints is on |
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
