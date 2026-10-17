# Kuizi — Adaptive Bac Platform

Kuizi helps Tunisian Baccalauréat students reach the grade they aim for. It traces what each student knows, concept by concept, with a transformer knowledge-tracing model (SAINT+), routes them through a prerequisite graph to the next best step, and teaches through a Socratic tutor, hands-on simulations and 1-minute micro-remediations. It works in French and Arabic, on web, iOS and Android, and is built to be fully accessible.

**Subjects:** Physics, Mathématiques, Sciences (SVT / Chimie), Sciences techniques, Économie & Gestion.
**Users:** students (17–19), parents, teachers, school admins, curriculum authors, platform admins.

## Where things are

| Need | Go to |
| --- | --- |
| Rules for every contributor and AI session | [`CLAUDE.md`](CLAUDE.md) |
| Documentation map | [`docs/README.md`](docs/README.md) |
| Product overview, personas, screens, advanced concepts | [`docs/product/overview.md`](docs/product/overview.md) |
| Full backlog (20 epics, 236 tickets, 1,612 points) | [`docs/backlog/APL_Full_Backlog.md`](docs/backlog/APL_Full_Backlog.md) |
| Jira import file and sync procedure | [`docs/backlog/README.md`](docs/backlog/README.md) |
| Architecture and decisions | [`docs/architecture/`](docs/architecture/overview.md) |
| Neural Core (knowledge-tracing engine) | [`docs/architecture/neural-core.md`](docs/architecture/neural-core.md) |
| Accessibility, Focus and notifications requirements | [`docs/requirements/accessibility-focus-notifications.md`](docs/requirements/accessibility-focus-notifications.md) |
| Cyanotype design system and screens | [`docs/design/design-system.md`](docs/design/design-system.md) |
| Bilingual concepts brief (EN + AR, PDF) | [`docs/deliverables/Kuizi-Concepts-EN-AR.pdf`](docs/deliverables/Kuizi-Concepts-EN-AR.pdf) |
| History of changes | [`CHANGELOG.md`](CHANGELOG.md) |

## Project tracking

Jira project `KK` ([board](https://kuizi.atlassian.net/jira/software/projects/KK/boards/37)) mirrors the backlog in this repository: 20 epics (KK-1 to KK-20), 236 tickets (KK-21 to KK-256) placed in `APL Sprint 1` to `APL Sprint 20`, and 426 "blocks" links. The repository is the source of truth. [`docs/backlog/jira_keys.csv`](docs/backlog/jira_keys.csv) maps each backlog ID to its Jira key, and [`docs/backlog/README.md`](docs/backlog/README.md) describes the sync.

## Status

Planning and design. Sprint 1 starts 2026-11-02; Physics and Maths go live in S18 (July 2027), the other subjects in S19–S20.
