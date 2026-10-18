# Decisions waiting for the product owner

**Last updated:** 2026-10-18. Agents prepare the options; only the product owner decides (ADR 0005). When a decision is taken, record it in `CHANGELOG.md`, apply it in the backlog and Jira if it changes scope, and remove it from this page. [`STATUS.md`](STATUS.md) lists the most urgent ones.

## 1. Blocking: needed before the next work can be merged or started

| # | Decision | Options and recommendation | Where |
| --- | --- | --- | --- |
| 1.1 | Merge the work into `main` | One pull request from `feat/sprint-2` into `main` brings everything (Sprint 1 and the Sprint 2 work); `main` is still empty | [compare](https://github.com/salahamami/Kuizi/compare/main...feat/sprint-2) |
| 1.2 | Protect `main` | Require a pull request and the status check **CI result**; block force pushes and deletion | [`dev/ci.md`](dev/ci.md), section "Protect main" |
| 1.3 | Brain model (ADR 0007) | AKT with Platt calibration, DKT as fallback (recommended by the ML agent), or DKT as champion until the pilot re-check (T239) | [ADR 0007](architecture/decisions/0007-knowledge-tracing-model.md) |
| 1.4 | Accept ADRs 0008, 0009, 0010 | 0008 monorepo layout and toolchains; 0009 one Keycloak realm and a Kuizi Keycloak image with Java extensions; 0010 learner event contracts (Avro, one topic per event, BACKWARD_TRANSITIVE; ML review signed off with conditions, all applied) | [`architecture/decisions/`](architecture/decisions/) |
| 1.5 | Split T076 (13 points) before Sprint 3 | The working agreement splits anything at 13 before sprint entry; the frontend agent proposes the split | backlog |

## 2. New dependencies and services to approve

| Area | Dependency or service | Licence | Ticket |
| --- | --- | --- | --- |
| Identity | `jose` (token checks in `@kuizi/auth`) | MIT | T012 |
| Identity | Java 21 and Maven, only inside the Keycloak image build | GPL-2.0 with classpath exception (JDK), Apache-2.0 (Maven) | T012 |
| Events | `fastavro`, `avro`, `PyYAML` | MIT, Apache-2.0, MIT | T023 |
| Curriculum | `psycopg[binary]` (used unmodified; alternative pg8000, BSD), `PyYAML`, `jsonschema` | LGPL-3.0, MIT, MIT | T032 |
| Tests | `pytest`, `pytest-cov`, `coverage`, `ruff`, `vitest`, ESLint, Prettier | MIT / Apache-2.0 | T006, ADR 0008 |
| CI | Trivy, Syft, cosign, actionlint (GitHub Actions only) | Apache-2.0, MIT | T006 |
| Registry | GitHub Container Registry for images built from `main`, until ECR (T240) | free for a public repository | T006 |
| Breach check | Have I Been Pwned range API (only a 5-character hash prefix is sent) | free API | T012 |

## 3. Per ticket

**T006 CI (KK-26)**
- Coverage gate for the brain library `ml/`: 75 % (measured 98 %); services keep 80 %, frontends 70 %.

**T012 identity (KK-32)**
- Role names `student`, `parent`, `teacher`, `school_admin`, `platform_admin`, plus `curriculum_author`: keep `curriculum_author`?
- Session lengths: web 30 minutes idle and 10 hours at most; phone 30 days idle and 60 days at most.
- When the Have I Been Pwned API is unreachable, let the password through (current) or refuse it?
- Reserved tenants `individual` (no school) and `platform` (Kuizi staff); a parent with children in two schools is open (T092, T093).
- Review the French and Arabic breached-password messages.
- A Google Cloud project, if Google sign-in is to be switched on.
- Phone OTP for parents needs an SMS provider and a phone field (with T013 consent and T089 delivery).

**T023 learner events (KK-43)** (also for the DPO)
- How to protect accommodation data before the pilot: topic access control plus warehouse column masking (T217), or field-level encryption (T015, T151).
- Retention hints for the DPIA (T017): Kafka 7 days (3 for `item.interaction`); warehouse 24 months (12 for interactions, hesitations and read-aloud).
- `student_id`: the Keycloak `sub`, or a separate learner pseudonym that makes erasure easier (T012, T018).
- T025 says ingestion "enriches with geo": not in the schemas on purpose; adding it needs your and the DPO's approval.
- When accommodation consent is withdrawn, clear the historical accommodation fields?
- Parent notification opens are attached to the learner they are about: acceptable?
- `response.expression` stores up to 500 characters a learner typed: acceptable?
- The timings in personal-class fields can reveal the time multiplier; the DPIA should record this.

**ML review of the events (signed off with conditions)**
- T145: does a time multiplier the school has not attested yet apply to practice timers?
- T047 fairness slices "by region, gender, school type" have no source in the events by design: keep them (needs a lawful source and a DPIA line) or replace them with section, school, language, device and accommodation?
- Requirements section 4.1: the ML agent proposes not dividing lag time by the multiplier (lag measures forgetting, not speed); only durations inside an item are normalised.

**T032 concept graph (KK-52)**
- Citing the sigmaths.net copies of the CNP textbooks as the source of the starter seed (licensing with the CNP is T039).
- Should T035 ("all Bac tracks") include 4e Sciences de l'informatique?
- One PostgreSQL schema per component (`curriculum` is the first): worth an ADR?

**T231 brand (KK-251)**
- Lowercase logotype "kuizi"; the spelling «كويزي»; the geometric Kufi style.
- A tagline, for example « Ton Bac, notion par notion. » / «باكالوريتك، مفهومًا بعد مفهوم.»
- Forms of address: *tu* for students and *vous* for adults; gender-neutral Arabic; *derja* in marketing; Western digits in Arabic copy.
- Choose and pay a native Arabic type designer (AC2) and a trademark search (AC3); keep T231 in review until then, or split the reviews into a follow-up ticket.

## 4. Backlog wording proposed by the agents (not applied)

The agents proposed local-first wording for acceptance criteria that mention cloud pieces. They are not applied: the current wording stays until you accept a change, and then the backlog and Jira change together.

| Ticket | Proposal |
| --- | --- |
| T006 AC1 | "A pull request cannot merge into main unless the required check *CI result* passes; it fails on any failing lint, type, test, coverage or contract check, or on any CRITICAL vulnerability in a built image (branch protection set by the product owner)." |
| T006 AC3 | "Every image published from main is signed with cosign (keyless) and carries its Syft SBOM as a signed attestation; GHCR until T240, then ECR." |
| T012 AC1 | "Keycloak access tokens carry `tenant_id` and `roles`; the shared `@kuizi/auth` library verifies signature, issuer, audience, expiry, `tenant_id` and `roles` in services, and Kong applies the same checks once T005 lands." |
| T012 title | "Deploy Keycloak identity provider: one realm with student / parent / teacher / school-admin / platform-admin roles" |
| T023 AC1–AC3 | Name the subject strategy (`<topic>-value`, BACKWARD_TRANSITIVE), the catalogue file, and the ML sign-off table; possible AC4 "every field has a privacy class; sensitive fields only in AccommodationContext" |
| T148 AC2 | "while Kuizi audio plays or a voice command runs" (third-party screen-reader speech cannot be observed) |

## 5. Older items

- Repository visibility: `salahamami/Kuizi` is public.
- Remove 17 obsolete "Blocks" links in Jira (list in `CHANGELOG.md`, entry "Local-first plan").
- Optional: ASSISTments 2017 sign-up; transfer the repository to your main GitHub account.
