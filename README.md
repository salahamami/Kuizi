# Kuizi — Adaptive Bac Platform

Kuizi helps Tunisian Baccalauréat students reach the grade they aim for. It traces what each student knows, concept by concept, with a deep knowledge-tracing model (proposed: AKT, with DKT as fallback; [ADR 0007](docs/architecture/decisions/0007-knowledge-tracing-model.md) is waiting for the product owner's decision), routes them through a prerequisite graph to the next best step, and teaches through a Socratic tutor, hands-on simulations and 1-minute micro-remediations. It works in French and Arabic, on web, iOS and Android, and is built to be fully accessible.

**Subjects:** Physics, Mathématiques, Sciences (SVT / Chimie), Sciences techniques, Économie & Gestion.
**Users:** students (17–19), parents, teachers, school admins, curriculum authors, platform admins.
**Built by:** one product owner working with a role-specific AI agent on every ticket ([ADR 0005](docs/architecture/decisions/0005-role-agents-and-one-product-owner.md)).

## Where things are

| Need | Go to |
| --- | --- |
| **Current status: sprint, decisions waiting, next work** | [`docs/STATUS.md`](docs/STATUS.md) |
| Rules for every contributor and AI session | [`CLAUDE.md`](CLAUDE.md) |
| Agent roles and working agreement (Ready, Done, review gates) | [`docs/agents/README.md`](docs/agents/README.md), [`docs/process/working-agreement.md`](docs/process/working-agreement.md) |
| Documentation map | [`docs/README.md`](docs/README.md) |
| Run Kuizi on your PC (local stack, brain environment) | [`docs/dev/local-setup.md`](docs/dev/local-setup.md) |
| Product overview, personas, screens, advanced concepts | [`docs/product/overview.md`](docs/product/overview.md) |
| Full backlog (20 epics, 240 tickets, 1,636 points) | [`docs/backlog/APL_Full_Backlog.md`](docs/backlog/APL_Full_Backlog.md) |
| Jira import file and sync procedure | [`docs/backlog/README.md`](docs/backlog/README.md) |
| Architecture and decisions | [`docs/architecture/`](docs/architecture/overview.md) |
| Neural Core (knowledge-tracing engine) | [`docs/architecture/neural-core.md`](docs/architecture/neural-core.md) |
| Learner event catalogue and Avro schemas (telemetry contracts) | [`docs/data/event-catalogue.md`](docs/data/event-catalogue.md), [`schemas/`](schemas/README.md) |
| Brain walkthrough: 10 notebooks, EN + AR, and glossary | [`docs/brain/README.md`](docs/brain/README.md) |
| Accessibility, Focus and notifications requirements | [`docs/requirements/accessibility-focus-notifications.md`](docs/requirements/accessibility-focus-notifications.md) |
| Cyanotype design system and screens | [`docs/design/design-system.md`](docs/design/design-system.md) |
| Bilingual concepts brief (EN + AR, PDF) | [`docs/deliverables/Kuizi-Concepts-EN-AR.pdf`](docs/deliverables/Kuizi-Concepts-EN-AR.pdf) |
| History of changes | [`CHANGELOG.md`](CHANGELOG.md) |

## Project tracking

Jira project `KK` ([board](https://kuizi.atlassian.net/jira/software/projects/KK/boards/37)) mirrors the backlog in this repository: 20 epics (KK-1 to KK-20), 240 tickets (KK-21 to KK-260) estimated and placed in `APL Sprint 1` to `APL Sprint 20`, and 440 "blocks" links. The repository is the source of truth. [`docs/backlog/jira_keys.csv`](docs/backlog/jira_keys.csv) maps each backlog ID to its Jira key, and [`docs/backlog/README.md`](docs/backlog/README.md) describes the sync.

## Status

Sprint 1 is active (see [`docs/STATUS.md`](docs/STATUS.md)). Development is local-first ([ADR 0006](docs/architecture/decisions/0006-local-first-development.md)): Sprint 1 (started 2026-10-17) sets up the local stack on the product owner's PC and starts the brain walkthrough; the cloud comes in S8–S11, before the pilot in S12. Physics and Maths go live in S18 (June 2027), the other subjects in S19–S20.
