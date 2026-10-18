# Changelog

All notable changes to the Kuizi plan, backlog and documentation.

## 2026-10-18 — T076 split before Sprint 3 (new ticket T241)

T076 was 13 points, and the conventions split anything at 13 before sprint entry.

### Changed
- **T076 (KK-96)** is now "Next.js 15 app foundation: apps/web with the App Router, i18n (ar/fr) with RTL and Keycloak sign-in", 8 points, still Sprint 3. Its description follows ADR 0008 (pnpm workspace instead of Turborepo), and its third acceptance criterion is now Keycloak sign-in (PKCE) with roles and tenant read from the token.
- **New T241 (KK-261)** "Shared UI package and Storybook: packages/ui, stories in French and Arabic, accessibility checks, Storybook for every pull request", 5 points, Sprint 3, frontend agent, blocked by T076. It blocks T174, which now also lists it as a blocker.
- Sprint 3 keeps 65 points (now 11 tickets). Totals: 241 tickets, 1,636 points, 442 dependency links.
- `tools/backlog/build_backlog.py` reads a new `SPLITS` table in `additions.py`: the fields it gives replace the v1 ticket's, and a change line records the split.

### Jira sync
- KK-96: summary, description and story points (13 → 8) updated.
- KK-261 created: Tâche, child of KK-9 (E09), APL Sprint 3, 5 points, labels `agent-frontend`, `apl-t241`, `sprint-03`, `phase-0`, `storybook`, `design-system`, `frontend`; assigned to the product owner. Links: KK-96 blocks KK-261, KK-261 blocks KK-194.
- Descriptions refreshed for the 13 tickets blocked by T076 (KK-97, KK-103, KK-104, KK-106, KK-122, KK-153, KK-155, KK-157, KK-182, KK-194, KK-240, KK-244, KK-252) and the scope line of KK-9.
- `docs/backlog/jira_keys.csv`: new row `T241,KK-261`.

## 2026-10-18 — Sprint 2 started early: CI, identity, learner events, concept graph, brand

While Sprint 1 waits for the product owner's review, the five Sprint 2 tickets were started early ("work ahead"); they stay in APL Sprint 2 in Jira. Each was handed to the agent of its role, worked in its own git worktree and branch, reviewed by the main session and merged into `feat/sprint-2`. The backlog itself (scope, points, sprints, links) did not change.

### Added
- **ADR 0008 (proposed): monorepo layout and toolchains.** Folders `apps/`, `services/`, `packages/`, `schemas/`, `curriculum/`, `brand/`; Node 22 with pnpm workspaces, strict TypeScript, ESLint, Prettier, Vitest; Python 3.12 with uv, Ruff, pytest. Root tooling: `package.json`, `pnpm-workspace.yaml`, `tsconfig.base.json`, `eslint.config.js`, `.prettierrc.json`.
- **T006 CI (KK-26, platform-devops agent).** GitHub Actions with project discovery (`scripts/ci/discover.py`): reusable Python, TypeScript and container workflows; coverage gates (services 80 %, frontends 70 %, `ml/` 75 %); Pact convention (`test:contract`); Syft SBOM, Trivy gate on CRITICAL, cosign keyless signing and SBOM attestation on `main` only (GHCR until T240); actions pinned to commit SHAs (new check in `make check`); `make lint` and `make test`; root `ruff.toml`; 50 pytest tests for `ml/kuizi_brain`. Guide: `docs/dev/ci.md`. Median run 59 s on GitHub.
- **T012 identity (KK-32, backend agent).** One Keycloak realm `kuizi` (single issuer) with roles, `tenant_id` and `roles` claims, 15-minute access tokens, rotating refresh tokens, brute-force protection, French and Arabic; a Kuizi Keycloak image with a Have I Been Pwned password policy (k-anonymity) and a login theme with 44 px controls; `@kuizi/auth` verifies tokens in services (55 tests). ADR 0009 (proposed). Guide and screenshots: `docs/dev/identity.md`.
- **T023 learner events (KK-43, data-engineering agent; ML sign-off by the ml-engineering agent).** 15 Avro events with a shared envelope, one topic per event, BACKWARD_TRANSITIVE compatibility enforced by the registry and by an offline check against git history; privacy class on every field, sensitive accommodation fields only in `AccommodationContext`, no free text in `tutor.message`; machine-readable catalogue and generated page `docs/data/event-catalogue.md`; 125 tests. ADR 0010 (proposed). ML review `docs/data/event-schema-ml-review.md`: signed off with conditions R1–R4, all applied.
- **T032 concept graph (KK-52, product-curriculum agent; tests run by the main session).** PostgreSQL schema `curriculum` with ltree paths, KCs shared across tracks with per-track chapter and exam weight, typed edges and a cycle-rejecting trigger that holds under concurrent writes; starter Physics seed (70 KCs, 132 edges, 4e Mathématiques, Sciences expérimentales, Sciences techniques, all `to_review`); loader and JSON export with its JSON Schema; 50 tests. Doc: `docs/curriculum/kc-graph.md`.
- **T231 brand (KK-251, design-ux agent; rendered and checked by the main session).** Eight-point star mark with a rhombus counter, logotypes «kuizi» and «كويزي» drawn as shapes (geometric Kufi), lockups, iOS, Android and web icons, social images; `brand/export.json` and 67 rendered PNGs plus `favicon.ico`; brand guide (draft) and review briefs for an Arabic type designer and a trademark search: `docs/design/brand-guide.md`, `docs/design/brand-reviews.md`.
- `docs/product-owner-decisions.md`: every decision waiting for the product owner, grouped by urgency and ticket, with the acceptance-criteria wording the agents proposed (not applied).

### Changed
- `infra/local/compose.yaml`: Keycloak is built from `services/keycloak` (`pull_policy: never`). `.env.example` gains `KEYCLOAK_API_AUDIENCE` and the Google sign-in variables (empty).
- `ml/`: six files reformatted by Ruff and small lint fixes; the T040 benchmark records a new `code_sha256` from now on.
- `Makefile`: `lint`, `test`, `graph-*` and `schemas-*` targets.
- `docs/STATUS.md`, `README.md`, `docs/README.md`, `docs/dev/local-setup.md`: links to the new guides.

### Jira sync
- KK-26, KK-32, KK-43, KK-52 and KK-251 moved À faire → En cours → Revue en cours, each with a comment on what was built, how each acceptance criterion was verified and what waits for the product owner. They stay in APL Sprint 2. No scope, point, sprint or link change, so `additions.py` and the generated backlog are unchanged.

## 2026-10-18 — Session hand-off: status page and documentation rule

### Added
- `docs/STATUS.md`: the page every session starts from — Sprint 1 state, decisions waiting for the product owner, next work, how a new session continues (Jira IDs, transitions, story-point field), environment notes for Claude sessions.

### Changed
- `CLAUDE.md`: sessions start with `docs/STATUS.md`; new rule "Always keep the documentation updated" (update STATUS, CHANGELOG and every changed `.md` file, commit and push, before a session ends).
- `README.md` and `docs/README.md` link the status page. The sprint table in `docs/backlog/README.md` shows Sprint 1 with 4 tickets (21 points) and Sprint 2 with 5 (29) after T040 moved forward.
- `docs/architecture/overview.md` and `neural-core.md` no longer present SAINT+ as decided: the model is chosen in ADR 0007 (proposed AKT, DKT fallback). Same fix in `README.md` and `docs/product/overview.md`.
- `ml/README.md`: EdNet is no longer listed as an allowed dataset (CC BY-NC licence).

## 2026-10-18 — T040 knowledge-tracing benchmark (Sprint 1, in review)

Done by the `ml-engineering` agent; reviewed by the main session (self-checks rerun, results files and ADR checked).

### Added
- `ml/benchmarks/`: `kt_benchmark.py` (5-fold split by student, quick and full modes, Platt calibration, T047 gate, CPU latency, MLflow logging), `check_kt_benchmark.py` (self-checks), `t040_benchmark.ipynb` (tables and charts from the saved results), `results/` and a README.
- ADR 0007 (Proposed): AKT with Platt calibration and 100-answer windows as the production knowledge-tracing model, DKT as the fallback. The product owner decides.

### Findings (ASSISTments 2009, 3 folds of 726 unseen students, windows of 100)
- AUC: AKT 0.768 ± 0.003, DKT 0.756 ± 0.002, SAKT 0.719, SAINT 0.699, SAINT+ 0.699. CPU latency at batch 1: AKT 3.8 ms, DKT 0.4 ms.
- AKT beats DKT by +0.012 AUC with no slice worse, but fails the T047 gate on raw calibration (ECE 0.040 vs 0.005); it passes after Platt calibration.
- SAINT+'s time features add +0.0008 AUC; windows longer than 50 answers do not help.
- On simulated students AKT also leads (0.680 vs 0.656); no model shows an extra-time gap larger than its spread, which rules out a large unfairness but does not prove fairness.
- ASSISTments 2017 needs a sign-up and acceptance of terms by the product owner; not used. GPU latency waits for the cloud (S8+).

### Jira sync
- KK-60 moved to *Revue en cours* with a comment.

### Pending decision (product owner)
- Accept ADR 0007 or keep DKT as champion until T239. If accepted, the backlog and Jira change for E05's goal, T041, T042 (AKT instead of SAINT+), T046 (serve AKT and DKT, GPU latency moved from T040), T049, and the architecture overview.

## 2026-10-18 — T234 agent operating model (Sprint 1, in review)

### Added
- `.claude/agents/`: 14 role briefs, one per `agent-*` label, written as Claude Code agent definitions: mission, what the role owns, tools and stack, role-specific done checks, what it must never do, when to ask the product owner, shared ground rules and the hand-back format. Each role gets only the tools it needs (document roles cannot run shell commands; no agent has Jira or repository-settings tools).
- `docs/process/working-agreement.md`: who does what, Definition of Ready and Done, review gates, branch and pull-request rules, ADR process, sprint rhythm, how to start a task with an agent. `docs/agents/README.md` lists the roles.
- `.github/pull_request_template.md` (Definition of Done checklist) and `.github/CODEOWNERS`.
- `make check` (`scripts/check_repo.py`): checks the compose file, the briefs' front matter, that every `agent-*` label has a brief, and that the generated backlog is up to date, without changing any file. Written by the `qa-sdet` agent from its brief alone, as the test of the operating model.

### Changed
- T234 acceptance criteria: "staging" becomes "tested on the local stack" (ADR 0006), and branch protection is described as it can work while every agent pushes with the product owner's GitHub account (the product owner's merge is the approval; a required code-owner approval comes once agents use their own account).
- `CLAUDE.md` points to the briefs and the working agreement and states that agents never merge, deploy or change settings.

### Jira sync
- KK-254: description updated, links to the briefs and the working agreement added, moved to *Revue en cours* with a comment.

### Pending (product owner, on GitHub)
- Protect `main`: Settings → Branches → rule for `main` with "Require a pull request before merging", "Block force pushes", "Restrict deletions" and no bypass. The connector cannot change repository settings.

## 2026-10-18 — T238 brain walkthrough (Sprint 1, in review)

### Added
- `ml/notebooks/`: ten notebooks, each in English and Arabic, from the concept graph to SAINT+ and fairness. Every code cell names its concept and the production ticket that will build it. All ten run end to end on CPU; the longest (07, SAINT+) takes about 5 minutes on 4 cores.
- `ml/kuizi_brain/`: small teaching library: Bac Physics concept slice with French and Arabic names, ASSISTments 2009 loader (fingerprint-checked download), Bac Physics student simulator with known true mastery and accommodations, IRT with Bayesian cold start and adaptive placement, BKT, DKT, SAINT+, mastery probes with attention, AUC and calibration.
- `docs/brain/README.md` (index, data and licences) and `docs/brain/glossary.md` (57 terms in English, Arabic and French).

### Findings worth carrying into T040
- On ASSISTments 2009 (students never seen in training): BKT AUC 0.726, DKT 0.756, SAINT+ 0.710. On the simulator: DKT 0.662, SAINT+ 0.624, ceiling 0.742. This matches published benchmarks: SAINT-type models need very large datasets. T040 and T239 should decide the production model on data, and DKT must stay in the benchmark.
- Time features did not help SAINT+ on the simulator (0.624 with, 0.645 without); T040 should test them on real data.
- A speed-only mastery signal underestimates students with extra time (bias −0.022 against +0.005 for the others); dividing time by the multiplier reduces it to −0.006 (T148).
- Splitting by answer instead of by student inflates IRT's AUC from 0.630 to 0.746 (leakage): T040 must split by student.

### Jira sync
- KK-258 moved to *Revue en cours* with a comment; the review session with the product owner closes it.

## 2026-10-17 — Sprint 1 starts now

The product owner decided not to wait for November: Sprint 1 started on 2026-10-17 and ends on 2026-10-30. Every sprint moves two weeks earlier, so S2 starts 2026-11-02, the pilot (S12) runs 2027-03-22 to 2027-04-02, go-live (S18) 2027-06-14 to 2027-06-25, and S20 ends 2027-07-23. Scope, points and sprint contents are unchanged.

### Changed
- Generator: `SPRINT_START` is 2026-10-19 (the Monday of the first sprint week); `CLAUDE.md`, `README.md` and the sprint table in `docs/backlog/README.md` show the new dates.

### Jira sync
- Updated the dates of `APL Sprint 1` to `APL Sprint 20` (goals unchanged) and started `APL Sprint 1`: it is the active sprint, with KK-254, KK-257 and KK-258.

## 2026-10-17 — T237 local stack (Sprint 1, in review)

### Added
- `infra/local/compose.yaml`: PostgreSQL 16 with pgvector, Redpanda (Kafka API and schema registry), Redis, SeaweedFS (S3 API), Keycloak with the development realm `kuizi`, MLflow, and LiteLLM as an optional profile. Every service has a health check.
- `Makefile` (`make up`, `smoke`, `status`, `down`, `reset`, `up-llm`, `ml-setup`, `ml-lab`), `.env.example` with the variable names the cloud will use, `scripts/smoke-test.sh` (10 functional checks).
- `ml/`: the brain's Python environment (uv, Python 3.12, PyTorch on CPU, pyKT, JupyterLab, MLflow client) with its lock file.
- `docs/dev/local-setup.md`: setup guide for Windows 11 with WSL2, macOS and Ubuntu.

### Changed
- T237 text: SeaweedFS replaces MinIO, which stopped publishing community images in 2025; LiteLLM is an optional profile (its image is about 1.7 GB). ADR 0006 updated to match.
- Local S3 keys are `S3_ACCESS_KEY_ID` and `S3_SECRET_ACCESS_KEY`, not `AWS_*`, so AWS keys already in a developer's shell never leak into the local stack; in the cloud, services use IAM roles.

### Jira sync
- KK-257 moved to *Revue en cours*, its description updated, and a comment lists what was built and tested.

## 2026-10-17 — Local-first plan: build on the PC, learn the brain early, cloud before the pilot

The product owner works on their own PC, so the five sprints of AWS foundations at the start no longer made sense ([ADR 0006](docs/architecture/decisions/0006-local-first-development.md)). Totals: 240 tickets, 1,636 points, 440 links. The pilot stays in S12 and go-live in S18; S17 is left almost empty as a buffer.

### Added
- T237 (S1) local development stack on the PC: PostgreSQL with pgvector, Kafka (Redpanda), Redis, MinIO, Keycloak, MLflow, LiteLLM and the Python ML environment.
- T238 (S1) brain walkthrough: each Neural Core concept explained simply, with notebooks on public data and an English–Arabic glossary.
- T239 (S14) re-run of the knowledge-tracing benchmark on Kuizi pilot data.
- T240 (S11) move to the cloud: every locally built service goes to AWS staging and production; the pilot (T108) now waits for it.
- `tools/backlog/replan.py`: recomputes the sprint plan (original order as priority, dependencies, capacity ramp, cloud from S8, pilot fixed in S12). Rerun it after the S1–S2 velocity reset.

### Changed
- Sprint 1 is now T237, T234 and T238 (13 points). Cloud tickets (Terraform, VPC, EKS, ArgoCD, Kong, Datadog, Aurora, MSK, Snowflake, MWAA, KMS, Secrets Manager, WAF, CDN, vLLM) move to S8–S11.
- The brain comes earlier: public-data benchmark (T040) in S2, pyKT (T041) in S3, SAINT+ (T042) and the IRT cold start (T043) in S4. The app shell (T076) moves to S3.
- 12 tickets start from the local stack instead of waiting for cloud infrastructure (T006, T012, T023, T025, T026, T027, T032, T041, T059, T061, T092, T134); T040 starts from T238 on public data, and the judge (T062) starts with hosted models through LiteLLM (T059) instead of the self-hosted model (T060). Each carries a "Local-first (ADR 0006)" change line.
- 144 tickets change sprint; phase labels follow the sprint.
- The generator applies `LOCAL_FIRST_SWAPS` and `REPLAN_SPRINTS` from `additions.py`.

### Jira sync
- Created KK-257 to KK-260 (T237–T240) with labels, assignee, estimate and sprint, and added 31 "Blocks" links.
- Moved 143 tickets to their new sprints; regenerated labels and descriptions for 147 tickets and the descriptions of 17 epics; updated 17 sprint goals. Checked: 240 tickets, and every ticket's sprint matches its `sprint-NN` label.

### Pending Jira sync
- Remove 17 obsolete "Blocks" links by hand (the connector cannot delete links). In each ticket, open *Linked work items* and remove the link: KK-21 blocks KK-26 · KK-23 blocks KK-32 · KK-23 blocks KK-79 · KK-25 blocks KK-45 · KK-35 blocks KK-154 · KK-36 blocks KK-79 · KK-41 blocks KK-43 · KK-41 blocks KK-46 · KK-41 blocks KK-47 · KK-48 blocks KK-60 · KK-80 blocks KK-82 · KK-231 blocks KK-32 · KK-231 blocks KK-52 · KK-231 blocks KK-81 · KK-231 blocks KK-112 · KK-237 blocks KK-47 · KK-238 blocks KK-61. Each ticket's description already lists the correct blockers.

## 2026-10-17 — Delivery by role agents, no human team

Kuizi is built by one product owner working with a role-specific AI agent on every ticket ([ADR 0005](docs/architecture/decisions/0005-role-agents-and-one-product-owner.md)). The backlog now speaks of agent roles instead of teams. Totals: 236 tickets, 1,613 points, 426 links; Sprint 1 carries 13 points.

### Changed
- The 14 teams become agent roles. Label `team-*` becomes `agent-*`, the "Team" line in descriptions becomes "Agent role", and the generated backlog's team and headcount table becomes the agent roster with each role's scope.
- No hiring: the staffing lines in ADR 0002, ADR 0004 and the open decisions in the accessibility requirements are superseded. Decisions owned by a CTO, ML lead or engineering manager now belong to the product owner.
- Sprint capacity: the 134-point ceiling stays as the planning limit and is reset from the velocity measured in Sprints 1 and 2.
- T234 becomes the agent operating model (role briefs, Definition of Ready and Done, review gates, least-privilege access, no real student data), 2 → 3 points.
- Sign-offs that named people who do not exist: T215 is reviewed by the product owner and the DPO; T017 and T051 gain a change line naming the product owner, the external DPO and a Tunisian Physics teacher.
- ADR 0005 lists where people outside the project are still needed: legal and DPO sign-off, accessibility testing with students, teacher review of content, pilot schools.

### Jira sync
- Project renamed to **Kuizi Adaptive Bac Platform** (key `KK`).
- All 236 tickets: labels `agent-*` instead of `team-*`, assignee set to the product owner, descriptions regenerated with the "Agent role" line. KK-254 (T234) also gets its new summary and 3 points.

## 2026-10-17 — Sprints and estimates in Jira

No backlog change; Jira catches up with the plan.

### Jira sync
- Backlog and Sprints were turned on in `KK`. Created `APL Sprint 1` to `APL Sprint 20` (Jira sprint IDs 440–459), two weeks each from 2026-11-02 to 2027-08-06, with a goal naming the phase and the main epics.
- Put all 236 tickets in their sprints, matching the `sprint-NN` labels and the generated backlog. No ticket is left outside a sprint.
- Estimation turned on: all 236 tickets carry their story-point estimate (1,612 points in total) and board 37 now estimates by story points.
- Sprint table added to `docs/backlog/README.md`.

### Pending Jira sync
- Project rename from `Kuizi_KPI` to `Kuizi Adaptive Bac Platform` (manual, key stays `KK`). *Done the same day.*

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
- Sprints `APL Sprint 1`–`20`, sprint assignment and story-point estimates. These wait for the Sprints feature on `KK` (Project settings → Features → Sprints). Until then, each ticket's description carries a "Story points" line and a `sprint-NN` label. *Sprints and assignment done on 2026-10-17; estimates still pending, see that entry.*
- Project rename from `Kuizi_KPI` to `Kuizi Adaptive Bac Platform` (manual, key stays `KK`).
