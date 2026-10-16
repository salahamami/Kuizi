# Changelog

All notable changes to the Kuizi plan, backlog and documentation.

## 2026-10-16 — Backlog v2 and project foundation

### Added
- Repository structure: `CLAUDE.md`, `README.md`, `docs/` (product, requirements, architecture, design, backlog), decision records 0001–0004.
- Backlog v2: 20 epics, 210 tickets, 1,496 points, 351 dependency links, generated from `tools/backlog/additions.py`.
  - E14 Inclusive Learning & Accessibility (19 tickets, 134 pts)
  - E15 Focus Mode & Smart Notifications (11 tickets, 54 pts)
  - E16 Native Apps & Store Compliance (12 tickets, 78 pts)
  - E17 Learner Experience & Cyanotype Design System (11 tickets, 68 pts)
  - E18 Bac Simulation, Annales & Grade Prediction (7 tickets, 40 pts)
  - E19 Product Analytics, Growth & Go-to-Market (10 tickets, 45 pts)
  - E20 Support, Back-office & Legal (8 tickets, 36 pts)
- Six new team roles: Mobile, Accessibility, Design / UX, Growth & Marketing, Customer Success & Support, Legal / DPO; `team-*` and `persona-*` labels on every ticket.
- Neural Core traceability (`docs/architecture/neural-core.md`) and the infographic.
- Bilingual concepts brief (EN + AR) in `docs/deliverables/`.

### Changed
- 23 v1 tickets gain acceptance criteria for accessibility, Focus and notifications (listed in `additions.py`, `CHANGES`).
- T085 moves from S13 to S11 and becomes two verification audits (S11, S15).
- T110 go-live also requires T150 (accessibility gate), T207 (legal documents) and T169 (store compliance).
- T142 and T143 placed in S12 to keep S11 within the 134-point capacity.

### Jira sync
- The planned project `APL` was not visible to the connector, so the backlog is mirrored in the existing project `KK` (board 37) instead.
- Loaded into `KK`: 20 epics (KK-1 to KK-20), 210 tickets (KK-21 to KK-230) under their epics, and 351 "Blocks" links. Labels carry the backlog ID, team, persona, phase and sprint.
- The Neural Core infographic is attached to E05 (KK-5).
- `docs/backlog/jira_keys.csv` maps each backlog ID to its Jira key. The generator now prints Jira keys in `APL_Full_Backlog.md` and `apl_backlog.json`, and flags any item missing from Jira.

### Pending Jira sync
- Sprints `APL Sprint 1`–`20`, sprint assignment and story-point estimates. These wait for the Sprints feature on `KK` (Project settings → Features → Sprints). Until then, each ticket's description carries a "Story points" line and a `sprint-NN` label.
- Project rename from `Kuizi_KPI` to `Kuizi Adaptive Bac Platform` (manual, key stays `KK`).
