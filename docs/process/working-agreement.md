# Working agreement

How the product owner and the role agents work together (T234, [ADR 0005](../architecture/decisions/0005-role-agents-and-one-product-owner.md)). The role briefs are in [`.claude/agents/`](../../.claude/agents/) and listed in [`docs/agents/README.md`](../agents/README.md).

## Who does what

| | Product owner | Main session (Claude, orchestrator) | Role agent |
| --- | --- | --- | --- |
| Picks the next ticket | ✅ decides | proposes from the sprint | — |
| Writes code, tests, documents | — | small tasks | ✅ on a branch |
| Updates the backlog and Jira | approves | ✅ keeps them in sync (`CLAUDE.md`) | reports changes needed |
| Opens a pull request | — | ✅ | prepares the description |
| Approves and merges into `main` | ✅ only the product owner | never | never |
| Deploys, changes repository or cloud settings, spends money | ✅ only the product owner | never without explicit OK | never |

## Definition of Ready

A ticket can start when:

1. It has a clear summary, a description and at least three testable acceptance criteria.
2. Every ticket that blocks it is done, or the dependency is explicitly accepted (for example "starts from the local stack", ADR 0006).
3. Designs, data formats and documents it needs exist, or creating them is part of the ticket.
4. It has an owning agent role (label `agent-*`) and fits in the sprint (points ≤ 8 when possible, never 13 unsplit).
5. Anything touching personal, minors' or accommodation data names the rule it follows in `docs/requirements/`.
6. **Design gate.** A ticket that builds something pupils, parents or teachers see (a screen, a flow, a notification, an email) starts only when the product owner has confirmed its design and its flow, worked out together with the design-ux agent: the journey, the screens in Arabic and French at phone and desktop width, and the states. The ticket links the approved design (canvas artboard or prototype) and the date of the approval. No user-interface code is written before that.

If one point is missing, the agent stops and says what is needed instead of guessing.

## Definition of Done

A ticket is done when:

1. Every acceptance criterion is met, with evidence in the hand-back (commands, results, screenshots).
2. The change is on a branch, with a pull request that follows the template, and the product owner has merged it.
3. Tests cover the change and pass; `make smoke` still passes for anything touching the local stack.
4. Anything users see meets WCAG 2.2 AA and works in French and Arabic (right to left).
5. Documentation is updated: README or guide, an ADR for any structural decision, and a `CHANGELOG.md` entry.
6. The backlog and Jira match: status, scope, points, links (`CLAUDE.md`, "Always keep Jira updated").
7. No secret, credential or real student data is in the repository, logs or notebooks.

## Review gates (always the product owner)

- Every merge into `main`.
- Every release or deployment, and every store submission.
- Every design and user flow before it is built (the design gate in the Definition of Ready).
- Anything students, parents or teachers will read: product copy, notifications, tutor prompts.
- Anything touching personal data, minors' data, consent or accommodations.
- Any new vendor, paid service, dependency licence or cloud resource.
- Any model promotion (with the T047 gate numbers).
- Legal documents and the curriculum content also need an outside reviewer: counsel or the external DPO, a Tunisian subject teacher (ADR 0005).

## Branches, commits and pull requests

- Never commit to `main`. One branch per ticket: `feat/tNNN-short-name`, `fix/tNNN-…`, `docs/…`, `chore/…`.
- Conventional commit messages (`feat:`, `fix:`, `docs:`, `chore:`), with the ticket ID in the message or the branch.
- Pull requests use [`.github/pull_request_template.md`](../../.github/pull_request_template.md): what, why, ticket, how it was tested, Definition of Done checklist.
- `main` is protected on GitHub: changes arrive only through pull requests; force pushes and deletion are blocked. The product owner sets this once (agents cannot change repository settings): repository **Settings → Branches → Add branch ruleset** (or *Add classic branch protection rule*) for `main`: tick **Require a pull request before merging** (0 approvals for now), **Block force pushes**, **Restrict deletions**, and **Do not allow bypassing** so the rule applies to every account.
- All agents push with the product owner's GitHub account for now, and GitHub does not let an account approve its own pull request. Until the repository moves to the product owner's main account with the agents' account as a collaborator, the product owner's merge is the approval, and "agents never merge" is a rule in every brief. After the move, one approval from the code owner (`.github/CODEOWNERS`) becomes required.

## Architecture decisions

Any structural change (a new service, a data store, a vendor, a change to how data flows) gets an ADR in [`docs/architecture/decisions/`](../architecture/decisions/), numbered in order, with context, decision and consequences, before or with the change.

## Sprint rhythm

Two-week sprints (`APL Sprint N`, S1 2026-10-17 → 2026-10-30, then every second Monday).

| When | What |
| --- | --- |
| First day | Planning: the product owner picks the sprint scope from the plan; the main session checks Definition of Ready and moves the sprint in Jira. |
| Every working day | Agents work ticket by ticket; the main session moves tickets *À faire → En cours → Revue en cours*; the product owner reviews what is waiting. |
| Last day | Review: demo of what was merged (*Terminé*), unfinished tickets go back to the plan, velocity is recorded. |
| After Sprint 2 | The 134-point ceiling is replaced by the measured velocity, and `tools/backlog/replan.py` rebalances the plan (ADR 0005, ADR 0006). |

## How to start a task with an agent

In a Claude Code session on this repository:

> Use the **ml-engineering** agent on **T040**. Read the ticket and its blockers, check the Definition of Ready, work on branch `feat/t040-benchmark`, and hand back as the brief says.

The main session then reviews the hand-back, opens the pull request, updates Jira and the changelog, and asks you to review.
