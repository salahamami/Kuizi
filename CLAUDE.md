# CLAUDE.md — working rules for Kuizi

Kuizi is an adaptive tutor for Tunisian Baccalauréat students (Physics, Maths, Sciences, Sciences techniques, Économie & Gestion), in French and Arabic. Read `README.md` for the product and `docs/README.md` for the documentation map.

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

## Always keep Jira updated

Whenever a session adds, removes or changes backlog items (scope, points, sprint, dependencies, acceptance criteria):

1. Change `tools/backlog/additions.py` (or the v1 change lists in it).
2. Run `python3 tools/backlog/build_backlog.py` and check the printed totals and sprint loads (no sprint above capacity, see `docs/backlog/README.md`).
3. Apply the same change in Jira project `KK` in the same session, following the sync procedure in `docs/backlog/README.md`. Every Jira issue carries the label `apl-<ticket id>` (for example `apl-t134`) so it can be found by backlog ID; `docs/backlog/jira_keys.csv` gives its key directly. New issues get a row in `jira_keys.csv`, then rerun the generator so the backlog shows the key.
4. Record the change in `CHANGELOG.md`.

Never leave the repo and Jira out of sync at the end of a session. If Jira cannot be reached, say so and list the pending Jira changes in `CHANGELOG.md` under "Pending Jira sync".

## Conventions

- Ticket IDs `T###`, epic IDs `E##`, sprints `APL Sprint N` (two weeks, S1 starts 2026-11-02).
- Story points are Fibonacci (1, 2, 3, 5, 8, 13); split anything at 13 before sprint entry.
- There is no human delivery team (ADR 0005). Every ticket has one owning agent role (label `agent-*`), done by the AI agent of that role with the product owner, who is the Jira assignee on every ticket and approves the work. User stories carry `persona-*` labels.
- Acceptance criteria are testable statements, three per ticket at minimum.
- Product copy is French and Arabic; documentation is English.
- Accessibility is not optional: WCAG 2.2 AA, French and Arabic right to left, no information by colour alone, touch targets of at least 44 px (`docs/requirements/accessibility-focus-notifications.md`).
- Minors' data: follow Law 2004-63 rules in the requirements; accommodation data is sensitive.

## Git

- Work on a branch, never commit straight to `main`. Conventional commit messages (`feat:`, `fix:`, `docs:`, `chore:`).
- Do not commit secrets, credentials or real student data.
