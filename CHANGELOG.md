# Changelog

All notable changes to the Kuizi plan, backlog and documentation.

## 2026-10-16 — Gap review: what the final version still needed

The backlog was checked against what a production app for minors needs end to end. 26 tickets were added (T211–T236, 116 points), bringing it to 236 tickets, 1,612 points and 426 dependency links. Every sprint stays at or below 134 points.

### Added
- Foundations nobody had ticketed: Aurora PostgreSQL with pgvector (T211), domains, certificates and email sending (T212), CDN and media store (T213), backend service template and API versioning (T214), Snowflake provisioning with PII masking (T217), Airflow and MLflow (T218), synthetic test data (T219).
- Core learning loop: one item player for every item type (T220) and a server-side answer evaluation service (T221) that feeds knowledge tracing.
- Child safety: a safeguarding policy with a designated lead (T222) and a tutor safety layer that detects distress, abuse and off-topic requests (T223).
- Security and legal: threat model, static analysis and dependency updates (T215), data breach response plan (T216), DPAs with LLM providers and other sub-processors (T236).
- Teachers and schools: classes and join codes (T224), assignments (T225), student profile page (T226), class announcements (T227), school admin management of teachers, classes and seats (T228).
- Mobile: native push and deep links (T229), crash reporting, performance monitoring and device-farm UI tests (T230).
- Brand identity (T231), UI string localisation workflow (T232), ways of working (T234), content production operations (T235), and the yearly Bac session update after go-live (T233).

### Changed
- T185 mock Bac: tutor, hints and the concept map are switched off during a graded paper.
- T108 pilot now waits for T223 and T236; T110 go-live also needs T216.
- Generator: new tickets in the original epics take their phase from their sprint, with the full phase name.

### Jira sync
- Created KK-231 to KK-256, added 75 "Blocks" links, and updated the descriptions of 49 tickets and 13 epics (dependency lines, criteria, scope counts). Jira shows 236 tickets.

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
