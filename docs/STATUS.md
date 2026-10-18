# Project status — start here

**Last updated:** 2026-10-18, end of the first working session (final check: all work committed and pushed on `feat/t040-benchmark`). Every session updates this page before it ends (`CLAUDE.md`).

Kuizi is planned (240 tickets in 20 two-week sprints, mirrored in Jira `KK`), runs on the product owner's PC (local-first, ADR 0006), and is built by the product owner with one AI agent per role (ADR 0005). Sprint 1 is active and all its work is built and waiting for review.

## Sprint 1 — active, 2026-10-17 → 2026-10-30

| Jira | Ticket | What it is | Status | What closes it |
| --- | --- | --- | --- | --- |
| [KK-257](https://kuizi.atlassian.net/browse/KK-257) | T237 | Local stack on the PC: `make up`, `make smoke` | Revue en cours | The product owner runs `make up` and `make smoke` on their PC |
| [KK-258](https://kuizi.atlassian.net/browse/KK-258) | T238 | Brain walkthrough: 10 notebooks in English and Arabic, 57-term glossary | Revue en cours | Review session: the product owner explains how the brain turns answers into mastery |
| [KK-254](https://kuizi.atlassian.net/browse/KK-254) | T234 | Agent operating model: 14 role briefs, working agreement, `make check` | Revue en cours | The product owner merges the pull request and protects `main` |
| [KK-60](https://kuizi.atlassian.net/browse/KK-60) | T040 | Knowledge-tracing benchmark and ADR 0007 (pulled forward from Sprint 2) | Revue en cours | The product owner decides ADR 0007 |

## Waiting for the product owner

1. **Decide ADR 0007** ([proposal](architecture/decisions/0007-knowledge-tracing-model.md)): AKT with Platt calibration as the brain, DKT as fallback; or DKT as champion until the pilot re-check (T239). Benchmark on ASSISTments 2009, students never seen in training: AKT AUC 0.768, DKT 0.756, SAKT 0.719, SAINT 0.699, SAINT+ 0.699. If AKT is accepted, update E05's goal, T041, T042, T046 (also gets the GPU latency measurement from T040), T049 and `architecture/overview.md`, in the backlog and Jira.
2. **Merge the work into `main`.** Everything is on stacked branches (`docs/project-foundation` → `feat/t237-local-stack` → `feat/t238-brain-walkthrough` → `feat/t234-agent-operating-model` → `feat/t040-benchmark`); the last one contains all of it. One pull request from `feat/t040-benchmark` into `main` brings everything; then the old branches can be deleted.
3. **Protect `main`** on GitHub (Settings → Branches): require a pull request, block force pushes and deletion, no bypass. Agents cannot change repository settings.
4. **Repository visibility.** `salahamami/kuizi` is public. Decide whether it should be private.
5. **Remove 17 obsolete "Blocks" links in Jira** left by the local-first re-plan (list in `CHANGELOG.md`, entry "Local-first plan", section "Pending Jira sync"). The connector cannot delete links.
6. Optional: sign up for ASSISTments 2017 (terms of use) if a second dataset is wanted; transfer the repository to the product owner's main GitHub account later.

## Next work

- **Sprint 2 (2026-11-02 → 2026-11-13):** T006 CI pipeline (KK-26), T012 Keycloak identity (KK-32), T023 event taxonomy (KK-43), T032 concept-graph schema (KK-52), T231 brand identity (KK-251). All on the local stack.
- After ADR 0007 is decided: T041 (pyKT integration, Sprint 3), then T042 and T043 (Sprint 4).
- After Sprint 2: replace the 134-point ceiling with the measured velocity and rerun `tools/backlog/replan.py`.

## How a new session continues

1. Read `CLAUDE.md` (rules), this page, and the top entries of `CHANGELOG.md`.
2. Check the active sprint in Jira `KK` (board 37). The Atlassian site is `kuizi.atlassian.net`; sprint IDs are 439 + sprint number (Sprint 1 = 440); transitions are 11 *À faire*, 21 *En cours*, 31 *Revue en cours*, 41 *Terminé*; story points are `customfield_10016`; the assignee on every ticket is the product owner (get their account with `atlassianUserInfo`).
3. Hand each ticket to the agent of its `agent-*` label (briefs in `.claude/agents/`), review the hand-back, commit on a branch, update Jira, `CHANGELOG.md` and this page.
4. Run `make check` before handing work back.

## Environment notes for Claude sessions

- In cloud containers Docker is installed but not running: start it with `nohup dockerd > /tmp/dockerd.log 2>&1 &`, then `make up`. Docker Hub may answer "429 Too Many Requests"; retry later or use pinned tags.
- The brain environment needs uv's own Python (`ml/pyproject.toml` sets `python-preference = "only-managed"`) because pyKT imports `turtle`, which needs Tk.
- ASSISTments 2009 downloads itself into `ml/data/` (git-ignored) on first use, with a fingerprint check.
- The GitHub connector can push branches but cannot change repository settings (branch protection, visibility).

## Where things are

| Need | Go to |
| --- | --- |
| Rules for every session | [`../CLAUDE.md`](../CLAUDE.md) |
| History of every change | [`../CHANGELOG.md`](../CHANGELOG.md) |
| Backlog and Jira sync | [`backlog/README.md`](backlog/README.md), [`backlog/APL_Full_Backlog.md`](backlog/APL_Full_Backlog.md) |
| Decisions | [`architecture/decisions/`](architecture/decisions/) (0001–0007) |
| Run Kuizi on a PC | [`dev/local-setup.md`](dev/local-setup.md) |
| The brain, step by step | [`brain/README.md`](brain/README.md) |
| Model benchmark | [`../ml/benchmarks/README.md`](../ml/benchmarks/README.md) |
| Agent roles and how we work | [`agents/README.md`](agents/README.md), [`process/working-agreement.md`](process/working-agreement.md) |

<div dir="rtl" lang="ar">

## ملخّص بالعربية

- <b>السبرينت 1 بدأ في 17 أكتوبر وينتهي في 30 أكتوبر.</b> المهام الأربع جاهزة وتنتظر مراجعتك: تجهيز الحاسوب (KK-257)، دليل الدماغ (KK-258)، قواعد الوكلاء (KK-254)، مقارنة نماذج الدماغ (KK-60).
- <b>قرار ينتظرك:</b> دماغ كويزي يكون AKT (الأدقّ) أو DKT (الأبسط والأسرع) حتى نتأكّد ببيانات التجربة.
- <b>على GitHub:</b> ادمج طلب الدمج في <code>main</code>، واحمِ الفرع <code>main</code>، وقرّر هل المستودع عام أم خاص.
- <b>السبرينت 2 من 2 نوفمبر:</b> CI، تسجيل الدخول، أحداث التلاميذ، خريطة المفاهيم، الهوية البصرية.

</div>
