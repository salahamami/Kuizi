# Project status — start here

**Last updated:** 2026-10-18, end of the second working session. Every session updates this page before it ends (`CLAUDE.md`).

Kuizi is planned (241 tickets in 20 two-week sprints, mirrored in Jira `KK`), runs on the product owner's PC (local-first, ADR 0006), and is built by the product owner with one AI agent per role (ADR 0005). Sprint 1 is active and in review. The five Sprint 2 tickets were worked ahead and are in review too. **All the work is on the branch `feat/sprint-2`; `main` is still empty until the product owner merges it.**

## Sprint 1 — active, 2026-10-17 → 2026-10-30

| Jira | Ticket | What it is | Status | What closes it |
| --- | --- | --- | --- | --- |
| [KK-257](https://kuizi.atlassian.net/browse/KK-257) | T237 | Local stack on the PC: `make up`, `make smoke` | Revue en cours | The product owner runs `make up` and `make smoke` on their PC |
| [KK-258](https://kuizi.atlassian.net/browse/KK-258) | T238 | Brain walkthrough: 10 notebooks in English and Arabic, 57-term glossary | Revue en cours | Review session: the product owner explains how the brain turns answers into mastery |
| [KK-254](https://kuizi.atlassian.net/browse/KK-254) | T234 | Agent operating model: 14 role briefs, working agreement, `make check` | Revue en cours | The product owner merges the pull request and protects `main` |
| [KK-60](https://kuizi.atlassian.net/browse/KK-60) | T040 | Knowledge-tracing benchmark and ADR 0007 (pulled forward from Sprint 2) | Revue en cours | The product owner decides ADR 0007 |

## Sprint 2 — 2026-11-02 → 2026-11-13, worked ahead on 2026-10-18

| Jira | Ticket | What was built | Status | What is left |
| --- | --- | --- | --- | --- |
| [KK-26](https://kuizi.atlassian.net/browse/KK-26) | T006 | GitHub Actions CI: discovery, lint, tests with coverage gates, SBOM, Trivy, cosign on `main` ([guide](dev/ci.md)) | See the CI note below | Protect `main` with the check **CI result** |
| [KK-32](https://kuizi.atlassian.net/browse/KK-32) | T012 | Keycloak realm, roles and claims, HIBP password policy, Arabic RTL login, `@kuizi/auth` ([guide](dev/identity.md)) | Revue en cours | Kong checks come with T005 (cloud); approvals in the decisions page |
| [KK-43](https://kuizi.atlassian.net/browse/KK-43) | T023 | 15 Avro learner events, data catalogue, compatibility checks, ML sign-off ([catalogue](data/event-catalogue.md)) | Revue en cours | DPO questions (accommodation data protection, retention) |
| [KK-52](https://kuizi.atlassian.net/browse/KK-52) | T032 | Concept graph in PostgreSQL with a cycle-proof trigger, starter Physics seed, JSON export ([doc](curriculum/kc-graph.md)) | Revue en cours | Teacher validation of the seed in T035 |
| [KK-251](https://kuizi.atlassian.net/browse/KK-251) | T231 | Star mark, logotypes «kuizi» and «كويزي», app icons, brand guide (draft) ([guide](design/brand-guide.md)) | Revue en cours | Arabic type designer review and trademark search (people, budget) |

## Waiting for the product owner

The full list, by urgency and ticket, is in [`product-owner-decisions.md`](product-owner-decisions.md). The most urgent:

1. **Merge `feat/sprint-2` into `main`** with one pull request ([compare](https://github.com/salahamami/Kuizi/compare/main...feat/sprint-2)). It contains everything from Sprints 1 and 2. A new chat starts from `main`, so until then it sees an empty repository. The older stacked branches can be deleted after the merge.
2. **Protect `main`**: require a pull request and the status check **CI result** (steps in [`dev/ci.md`](dev/ci.md)).
3. **Decide ADR 0007** (brain model: AKT with Platt calibration, or DKT until T239) and **accept ADRs 0008, 0009, 0010** (monorepo layout, identity, event contracts).
4. **Approve the new dependencies** (list with licences in the decisions page).

## Next work

- **Sprint 3 (2026-11-16 → 2026-11-27):** T013 parental consent (KK-33), T014 authorisation middleware (KK-34), T024 telemetry SDK (KK-44), T033 subject and track first-class (KK-53), T036 item data model (KK-56), T041 pyKT integration (KK-61, after ADR 0007), T076 Next.js app foundation (KK-96, split from 13 to 8 points), T241 shared UI package and Storybook (KK-261, new, 5 points), T214 backend service template (KK-234), T215 threat model and security scanning (KK-235), T235 content operations (KK-255). All their blockers are built.
- Split every 13-point ticket before its sprint starts (CLAUDE.md). Next ones: T042 (Sprint 4, after ADR 0007), then T035, T037, T077 and T092 (Sprint 5). `SPLITS` in `tools/backlog/additions.py` holds the rewritten v1 ticket; T076/T241 is the example.
- After Sprint 2: replace the 134-point ceiling with the measured velocity and rerun `tools/backlog/replan.py`.

## How a new session continues

1. Read `CLAUDE.md` (rules), this page, [`product-owner-decisions.md`](product-owner-decisions.md) and the top entries of `CHANGELOG.md`. If `main` is still empty, check out `feat/sprint-2`.
2. Check the active sprint in Jira `KK` (board 37). The Atlassian site is `kuizi.atlassian.net`; sprint IDs are 439 + sprint number (Sprint 1 = 440); transitions are 11 *À faire*, 21 *En cours*, 31 *Revue en cours*, 41 *Terminé*; story points are `customfield_10016`; the assignee on every ticket is the product owner (get their account with `atlassianUserInfo`).
3. Hand each ticket to the agent of its `agent-*` label (briefs in `.claude/agents/`), review the hand-back, commit on a branch, update Jira, `CHANGELOG.md` and this page. Agents without a shell (product-curriculum, design-ux) need the main session to run their tests or render their files.
4. Run `make check`, `make lint` and `make test` before handing work back.

## Environment notes for Claude sessions

- In cloud containers Docker is installed but not running: start it with `nohup dockerd > /tmp/dockerd.log 2>&1 &`, then `make up`. Docker Hub may answer "429 Too Many Requests"; `mirror.gcr.io` serves the same images.
- **Keycloak is now built from `services/keycloak`** (Maven inside Docker). Behind the cloud container's TLS-intercepting proxy, the Maven step and the HIBP check need the proxy's CA bundle (`/root/.ccr/ca-bundle.crt`) added to the Java truststore; a normal PC needs nothing. A checkout without T012 that runs `make up` recreates Keycloak with the stock image, and the realm then fails with "Password policy not found"; recovery steps are in `dev/identity.md`. After merging, delete the old realm once so the new realm file is imported.
- The brain environment needs uv's own Python (`ml/pyproject.toml` sets `python-preference = "only-managed"`) because pyKT imports `turtle`, which needs Tk.
- ASSISTments 2009 downloads itself into `ml/data/` (git-ignored) on first use, with a fingerprint check.
- Parallel agents: the Agent tool's `isolation: "worktree"` needs `origin/main`, which is empty. Create worktrees by hand instead (`git worktree add -b <branch> .claude/worktrees/<name> feat/sprint-2`; `.claude/worktrees/` is excluded locally in `.git/info/exclude` and in `.prettierignore`).
- The GitHub connector can push branches and read the REST API (CI runs: `gh api repos/salahamami/Kuizi/actions/runs?branch=<branch>`), but cannot use GraphQL or change repository settings. GitHub now spells the repository `salahamami/Kuizi`; the old URL redirects.

## Where things are

| Need | Go to |
| --- | --- |
| Rules for every session | [`../CLAUDE.md`](../CLAUDE.md) |
| Decisions waiting for the product owner | [`product-owner-decisions.md`](product-owner-decisions.md) |
| History of every change | [`../CHANGELOG.md`](../CHANGELOG.md) |
| Backlog and Jira sync | [`backlog/README.md`](backlog/README.md), [`backlog/APL_Full_Backlog.md`](backlog/APL_Full_Backlog.md) |
| Decisions | [`architecture/decisions/`](architecture/decisions/) (0001–0010) |
| Run Kuizi on a PC; CI; identity | [`dev/local-setup.md`](dev/local-setup.md), [`dev/ci.md`](dev/ci.md), [`dev/identity.md`](dev/identity.md) |
| Learner events | [`data/event-catalogue.md`](data/event-catalogue.md), [`../schemas/README.md`](../schemas/README.md) |
| Concept graph | [`curriculum/kc-graph.md`](curriculum/kc-graph.md) |
| Brand | [`design/brand-guide.md`](design/brand-guide.md), [`../brand/README.md`](../brand/README.md) |
| The brain, step by step | [`brain/README.md`](brain/README.md) |
| Model benchmark | [`../ml/benchmarks/README.md`](../ml/benchmarks/README.md) |
| Agent roles and how we work | [`agents/README.md`](agents/README.md), [`process/working-agreement.md`](process/working-agreement.md) |

<div dir="rtl" lang="ar">

## ملخّص بالعربية

- <b>السبرينت 1</b> (17 → 30 أكتوبر): المهام الأربع جاهزة وتنتظر مراجعتك.
- <b>السبرينت 2</b> بدأناه مبكرًا وأنجزنا مهامه الخمس، وكلها تنتظر مراجعتك:
  - فحص آلي للكود عند كل تغيير (CI).
  - تسجيل الدخول بالأدوار، مع صفحة دخول عربية من اليمين إلى اليسار.
  - تعريف أحداث التلميذ التي يتعلّم منها الدماغ.
  - خريطة مفاهيم الفيزياء.
  - الهوية البصرية لكويزي: نجمة ثمانية وشعار بالعربية والفرنسية.
- <b>كل العمل في الفرع <code>feat/sprint-2</code>.</b> ادمجه في <code>main</code> بطلب دمج واحد، ثم احمِ الفرع <code>main</code>.
- <b>قرارات تنتظرك:</b>
  - دماغ كويزي: AKT أو DKT.
  - قبول ثلاثة قرارات معمارية (0008، 0009، 0010).
  - الموافقة على المكتبات الجديدة.
  - مراجع للشعار العربي وبحث عن العلامة التجارية.
  - القائمة كاملة في <code>docs/product-owner-decisions.md</code>.

</div>
