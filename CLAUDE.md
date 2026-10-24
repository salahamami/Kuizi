# CLAUDE.md — working rules for Kuizi

Kuizi is an adaptive tutor for Tunisian pupils of 6e année and 7e–9e année de base (about 11–15), all year and for the Sixième and Neuvième concours, in Arabic and French: maths, éveil scientifique, SVT, Arabic, French and English; the Bac follows in phase 2 ([ADR 0011](docs/architecture/decisions/0011-start-with-6e-9e.md)). Read `README.md` for the product and `docs/README.md` for the documentation map.

**Start every session with [`docs/STATUS.md`](docs/STATUS.md)**: the active sprint, what is waiting for the product owner, the next work and environment notes.

## Sources of truth

| What | Where | Rule |
| --- | --- | --- |
| Backlog (epics, tickets, points, sprints, dependencies) | `tools/backlog/additions.py` + `docs/backlog/source/` (v1) | Edit data, never the generated files |
| Generated backlog | `docs/backlog/APL_Full_Backlog.md`, `APL_jira_import_full.csv`, `apl_backlog.json` | Regenerate with `python3 tools/backlog/build_backlog.py` |
| Jira | Project key **`KK`** (team-managed Scrum, board 37) at https://kuizi.atlassian.net/jira/software/projects/KK/boards/37 | Must mirror the generated backlog |
| Jira key map | `docs/backlog/jira_keys.csv` (backlog ID → `KK-n`) | Add a row for every issue created in Jira |
| Requirements | `docs/requirements/` | Numbered IDs (FR-*, NFR-*) referenced by tickets |
| Architecture | `docs/architecture/overview.md`, decisions in `docs/architecture/decisions/` | Any structural change gets an ADR |
| Design | `docs/design/design-system.md` (Cyanotype) + design canvas (link inside) | UI follows the tokens and accessibility rules |
| Agent roles and working agreement | `.claude/agents/` (one brief per role), `docs/agents/README.md`, `docs/process/working-agreement.md` | Hand each ticket to the agent of its `agent-*` label; follow the Definition of Ready and Done |

## Always keep Jira updated

Whenever a session adds, removes or changes backlog items (scope, points, sprint, dependencies, acceptance criteria):

1. Change `tools/backlog/additions.py` (or the v1 change lists in it).
2. Run `python3 tools/backlog/build_backlog.py` and check the printed totals and sprint loads (no sprint above capacity, see `docs/backlog/README.md`).
3. Apply the same change in Jira project `KK` in the same session, following the sync procedure in `docs/backlog/README.md`. Every Jira issue carries the label `apl-<ticket id>` (for example `apl-t134`) so it can be found by backlog ID; `docs/backlog/jira_keys.csv` gives its key directly. New issues get a row in `jira_keys.csv`, then rerun the generator so the backlog shows the key.
4. Record the change in `CHANGELOG.md`.

Never leave the repo and Jira out of sync at the end of a session. If Jira cannot be reached, say so and list the pending Jira changes in `CHANGELOG.md` under "Pending Jira sync".

## Always keep the documentation updated

The product owner works across several chats, so the repository must always tell the whole story:

- Before a session ends, update `docs/STATUS.md` (sprint state, decisions waiting, next work), add a `CHANGELOG.md` entry, and update every `.md` file whose content changed (READMEs, guides, ADRs, the backlog README).
- Commit and push everything; never leave work only in a session.

## Conventions

- Ticket IDs `T###`, epic IDs `E##`, sprints `APL Sprint N` (two weeks; S1 started 2026-10-17 and ends 2026-10-30, then a new sprint every second Monday). The plan has 24 sprints: free pilot from S10 (2027-02-22), concours in S18, paid launch in S24 (September 2027); Bac phase 2 tickets have no sprint (label `phase-bac`).
- Story points are Fibonacci (1, 2, 3, 5, 8, 13); split anything at 13 before sprint entry.
- There is no human delivery team (ADR 0005). Every ticket has one owning agent role (label `agent-*`), done by the AI agent of that role with the product owner, who is the Jira assignee on every ticket and approves the work. User stories carry `persona-*` labels.
- Acceptance criteria are testable statements, three per ticket at minimum.
- Product copy is French and Arabic; documentation is English.
- Design gate: nothing pupils, parents or teachers see is coded before the product owner confirms its design and flow with the design-ux agent (`docs/process/working-agreement.md`).
- Accessibility is not optional: WCAG 2.2 AA, French and Arabic right to left, no information by colour alone, touch targets of at least 44 px (`docs/requirements/accessibility-focus-notifications.md`).
- Minors' data: every learner is a child; follow Law 2004-63 and the age-band rules (A: 11–12, B: 13–15) in `docs/requirements/minors-11-15.md` (rule IDs `MR-*`); accommodation data is sensitive.
- Local-first (ADR 0006): until the cloud move (T240, S9, after the data-residency decision T247) everything runs on the local stack (T237) with synthetic or public data; use the same environment variable names the cloud will use.

## Git

- Work on a branch, never commit straight to `main`. Conventional commit messages (`feat:`, `fix:`, `docs:`, `chore:`).
- Agents never merge, deploy or change repository or cloud settings; the product owner merges every pull request (template in `.github/pull_request_template.md`).
- Do not commit secrets, credentials or real student data.
