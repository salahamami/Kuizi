# Backlog: how it is maintained and synced to Jira

The repository is the source of truth for the backlog. Jira project **`KK`** (team-managed Scrum, [board 37](https://kuizi.atlassian.net/jira/software/projects/KK/boards/37)) mirrors it.

## Files

| File | Role | Edit? |
| --- | --- | --- |
| `source/APL_Production_Backlog_v1.md`, `.docx`, `source/APL_jira_import_v1.csv` | v1 backlog as received (13 epics, 132 tickets, 1,041 points) | Never |
| `../../tools/backlog/additions.py` | Everything added or changed after v1: epics E14–E21, tickets T133–T275, v1 tickets split before sprint entry (`SPLITS`), changes to v1 tickets, the ADR 0011 re-scope (`REWRITES`, `EPIC_REWRITES`, `ADR11_CHANGES`, `DEPS`, `BAC_PHASE2`, `TARGET_SPRINTS`), the horizon, phases and milestones (`HORIZON`, `PHASES`, `MILESTONES`), agent roles, Neural Core mapping | Yes, this is where changes go |
| `../../tools/backlog/build_backlog.py` | Generator | Only to change output formats |
| `../../tools/backlog/replan.py` | Sprint scheduler: writes `REPLAN_SPRINTS` in `additions.py` from the planned sprints, dependencies, pins and capacity | Only to change the planning rules |
| `jira_keys.csv` | Backlog ID → Jira key (`E05,KK-5`, `T103,KK-134`) | Yes, add a row whenever an issue is created in Jira |
| `APL_Full_Backlog.md` | Full readable backlog (21 epics, 275 tickets, 1,721 points; 8 of them, 94 points, in Bac phase 2), with Jira keys | Generated |
| `APL_jira_import_full.csv` | Jira CSV import file, same columns as v1 plus agent-role and persona labels | Generated |
| `apl_backlog.json` | Input for the API sync (Markdown descriptions, labels, links, Jira keys) | Generated |

Regenerate after any change:

```bash
python3 tools/backlog/build_backlog.py
```

The script fails if a ticket ID is duplicated, a dependency points to an unknown ticket, an epic is missing, points are not Fibonacci, a scheduled ticket depends on a Bac phase 2 ticket, or a ticket lands after the horizon. It prints points per sprint: keep every sprint at or below its capacity (a ramp of 13, 40, 65, 80 and 95 points for S1–S5, then the 134-point planning ceiling). Work is done by role agents with the product owner (ADR 0005), so the ceiling is reset from the velocity measured in Sprints 1 and 2. It also lists backlog items that have no Jira key yet.

To re-plan sprints (after a scope change or a capacity change), run the scheduler, then the generator:

```bash
python3 tools/backlog/replan.py && python3 tools/backlog/build_backlog.py
```

`replan.py` keeps the tickets done or in review (Sprints 1 and 2), the free pilot (T108, S10), the pilot exit review (T272, S20) and the paid launch (T110, S24) where they are; starts cloud work in S6 at the earliest; never puts a ticket in the same sprint as the design approval that gates it (design gate); and reports any ticket that misses a pinned date or any sprint over capacity.

## Plan after ADR 0011 (6e–9e first)

On 2026-10-24 the product owner decided to start with 6e and 7e–9e année de base and the two concours, and to move the Bac to phase 2 ([ADR 0011](../architecture/decisions/0011-start-with-6e-9e.md)). The re-plan in the repository:

- **24 sprints** instead of 20: free pilot with 3–5 partner private schools from S10 (2027-02-22) to the June 2027 concours (S18), pilot exit review in S20, paid launch for the 2027–28 school year in S24 (from 2027-09-06) with 30-day hypercare. S17 and S18 are left free for the concours change freeze and as a buffer.
- **Phases** follow the sprint for every ticket (`PHASES` in `additions.py`): Phase 0 Foundations (S1–S3), 1 Data Plane & Design Research (S4–S6), 2 Intelligence & Pilot Build (S7–S9), 3 Free Pilot & Product Surfaces (S10–S14), 4 Concours Season & Hardening (S15–S18), 5 Pilot Exit & Content Completion (S19–S20), 6 Launch Readiness (S21–S22), 7 Paid Launch 2027–28 (S23–S24), and Phase 8 — Bac (phase 2, not scheduled).
- **Bac phase 2:** T035, T038, T079, T080, T081, T125, T126 and the placeholder T274 stay in the backlog without a sprint (Jira label `phase-bac`, no sprint). Nothing scheduled may depend on them.
- **Design gate:** every ticket that builds what pupils, parents or teachers see is blocked by the approved design of its journey (T258 core pupil journey, T260 parent, T261 teacher and school, T262 concours mode, T259 Cyanotype v2, T244 consent and assent screens).
- **New:** E21 (Design First) and T242–T275: NEW-1 to NEW-12 of `docs/requirements/minors-11-15.md` (T242–T253), design (T254–T262), splits of T037, T042, T092 and T084 (T263–T266), maths 7e–8e and English content (T267, T268), writing assessment (T269–T271), the pilot exit review (T272), the launch go-to-market plan (T273), the Bac phase 2 placeholder (T274) and the mock concours papers (T275).
- **Jira:** not yet synced. The pending changes are listed in `CHANGELOG.md` ("Pending Jira sync", 2026-10-24).

## Jira project state

Project name **Kuizi Adaptive Bac Platform** (renamed from `Kuizi_KPI` on 2026-10-17). Loaded on 2026-10-16 through the Atlassian connector:

- 20 epics, KK-1 to KK-20, in backlog order (E05 is KK-5).
- 241 tickets, KK-21 to KK-261, each a child of its epic. Keys follow `20 + ticket number`, except T104–T114 (KK-123 to KK-133), T103 (KK-134) and T241 (KK-261). `jira_keys.csv` has every key.
- "Blocks" links reproduce every *Blocked by* in the backlog (442 links), plus 17 obsolete links still to be removed by hand (see `CHANGELOG.md`, "Pending Jira sync").
- The gap review of the same day added T211–T236 (KK-231 to KK-256): foundations, safeguarding, teacher and school-admin tools, mobile quality and content operations.
- The Neural Core infographic sits in a comment on KK-5.
- On 2026-10-17, after Backlog, Sprints and Estimation were turned on, the 20 sprints were created, every ticket was put in its sprint and given its story-point estimate (field `Story point estimate`, `customfield_10016`; the board estimates by it). Each sprint's goal names its phase and the three epics carrying the most points in it.
- The same day the delivery model changed to role agents with one product owner (ADR 0005): every ticket's `team-*` label became `agent-*`, its description says "Agent role", and the product owner is the assignee on all 236 tickets.
- Still on 2026-10-17, the plan became local-first (ADR 0006): T237–T240 were added (KK-257 to KK-260), 143 tickets moved sprint, their labels and descriptions were regenerated, 17 epic descriptions and 17 sprint goals were updated. The sprint plan comes from `tools/backlog/replan.py`.
- On 2026-10-18 Sprint 1 was started (it began 2026-10-17); its four tickets are in *Revue en cours*. The five Sprint 2 tickets (KK-26, KK-32, KK-43, KK-52, KK-251) were worked ahead the same day and are also in *Revue en cours*, still in APL Sprint 2. Each reviewed ticket has a comment saying how its acceptance criteria were verified and what waits for the product owner.
- Also on 2026-10-18, T076 (13 points, Sprint 3) was split before sprint entry: T076 became the 8-point app foundation and T241 (KK-261, 5 points, Sprint 3) took the shared UI package and Storybook; T241 blocks T174. The 13 tickets blocked by T076 got their descriptions refreshed (new T076 title), and E09's scope line says 13 tickets.
- **On 2026-10-24 the backlog was re-planned in the repository for ADR 0011 (6e–9e first, 24 sprints); Jira is not synced yet.** The sync creates E21, T242–T275 and APL Sprint 21–24, rewrites 64 tickets, adds criteria to 85 more, moves 153 tickets to a new sprint and 7 to Bac phase 2, adds 222 links and removes 50 (list in `CHANGELOG.md`, "Pending Jira sync", 2026-10-24). The project name still says "Bac"; renaming it is the product owner's call.

The sprint plan in the repository after ADR 0011 (Jira still shows the plan before it until the sync):

| Sprint | Jira sprint ID | Start | End | Tickets | Points |
| --- | --- | --- | --- | --- | --- |
| APL Sprint 1 | 440 | 2026-10-17 | 2026-10-30 | 4 | 21 |
| APL Sprint 2 | 441 | 2026-11-02 | 2026-11-13 | 7 | 39 |
| APL Sprint 3 | 442 | 2026-11-16 | 2026-11-27 | 12 | 65 |
| APL Sprint 4 | 443 | 2026-11-30 | 2026-12-11 | 14 | 78 |
| APL Sprint 5 | 444 | 2026-12-14 | 2026-12-25 | 16 | 95 |
| APL Sprint 6 | 445 | 2026-12-28 | 2027-01-08 | 18 | 101 |
| APL Sprint 7 | 446 | 2027-01-11 | 2027-01-22 | 19 | 127 |
| APL Sprint 8 | 447 | 2027-01-25 | 2027-02-05 | 22 | 134 |
| APL Sprint 9 | 448 | 2027-02-08 | 2027-02-19 | 19 | 132 |
| APL Sprint 10 | 449 | 2027-02-22 | 2027-03-05 | 21 | 132 |
| APL Sprint 11 | 450 | 2027-03-08 | 2027-03-19 | 16 | 134 |
| APL Sprint 12 | 451 | 2027-03-22 | 2027-04-02 | 23 | 133 |
| APL Sprint 13 | 452 | 2027-04-05 | 2027-04-16 | 22 | 134 |
| APL Sprint 14 | 453 | 2027-04-19 | 2027-04-30 | 21 | 106 |
| APL Sprint 15 | 454 | 2027-05-03 | 2027-05-14 | 7 | 34 |
| APL Sprint 16 | 455 | 2027-05-17 | 2027-05-28 | 2 | 11 |
| APL Sprint 17 | 456 | 2027-05-31 | 2027-06-11 | 0 | 0 |
| APL Sprint 18 | 457 | 2027-06-14 | 2027-06-25 | 0 | 0 |
| APL Sprint 19 | 458 | 2027-06-28 | 2027-07-09 | 5 | 37 |
| APL Sprint 20 | 459 | 2027-07-12 | 2027-07-23 | 8 | 47 |
| APL Sprint 21 | to create | 2027-07-26 | 2027-08-06 | 7 | 52 |
| APL Sprint 22 | to create | 2027-08-09 | 2027-08-20 | 2 | 5 |
| APL Sprint 23 | to create | 2027-08-23 | 2027-09-03 | 1 | 5 |
| APL Sprint 24 | to create | 2027-09-06 | 2027-09-17 | 1 | 5 |
| Bac phase 2 | — | not scheduled | — | 8 | 94 |

Jira sprint ID = 439 + sprint number for APL Sprint 1–20; Sprints 21–24 get their IDs when they are created (record them here). To move a ticket, change its sprint in `additions.py` (or rerun `python3 tools/backlog/replan.py` when capacity changes), regenerate, then in Jira move it to the new sprint and update its `sprint-NN` and `phase-N` labels and description.

Still to do in Jira (the connector cannot do these):

1. **Remove the obsolete "Blocks" links**: 17 left by the local-first re-plan and 50 by the ADR 0011 re-plan; the lists are in `CHANGELOG.md` under "Pending Jira sync". The connector can create issue links but not delete them.
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
| Phase | Label `phase-N` (`phase-bac` for Bac phase 2, which has no sprint and no `sprint-NN` label) |
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
