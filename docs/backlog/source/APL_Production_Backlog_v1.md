# Adaptive Bac Learning Platform — Production Engineering Backlog

**Project key:** `APL` · **Subjects:** Physics, Mathématiques, Sciences (SVT / Chimie), Sciences techniques, Économie & Gestion · **Horizon:** 20 two-week sprints (≈ 10 months) starting 2026-11-02 · **Scope:** 13 epics · 132 tickets · 1041 story points

> Companion files: `APL_jira_import.csv` (Jira-ready import) and `APL_Production_Backlog.docx` (stakeholder document). All three are generated from the same source (`backlog_data.py`), so IDs and estimates match across them.

## 1. Architecture this backlog builds

The platform is an adaptive tutor for Tunisian Baccalauréat students covering Physics, Mathématiques, Sciences (SVT / Chimie), Sciences techniques and Économie & Gestion. The engine is subject-agnostic — it sees knowledge components, items, sequences and answers — and every content object carries a first-class `subject` and Bac `track`. Physics is built first because it exercises every part of the stack (simulations, symbolic verification, bilingual content); the other four subjects are loaded onto the same engine as parallel content tracks (epic E13) and ship in waves. The architecture has two halves that this backlog treats as first-class, equally weighted workstreams:

**The Brain** — a self-hosted deep-learning stack. Student micro-interactions feed a Transformer-based Deep Knowledge Tracing model (SAINT+ via pyKT, PyTorch) that predicts per-concept failure probability. An IRT estimator covers the cold-start window. Kubeflow retrains the model every Sunday at 02:00 Africa/Tunis on the week's Snowflake data and promotes it through a champion/challenger gate to TorchServe (p99 ≤ 50 ms). A routing service turns those predictions, plus the curriculum knowledge graph, into the next item or hint in ≤ 80 ms. The Socratic tutor runs through a LiteLLM gateway with curriculum-grounded RAG (pgvector) and a synchronous LLM-as-a-Judge harness that blocks hallucinated physics before a student sees it.

**The Coding Side** — an event-driven, auto-scaling web platform. A Next.js / React Three Fiber frontend streams granular telemetry (slider moves, hover, hesitation, confidence) into Kafka, which fans out to Redis (instant streaks / leaderboards) and Snowflake (training data). Everything runs on AWS EKS provisioned by Terraform with blue/green deploys, Kong at the edge, Datadog tracing, PostgreSQL Row-Level Security for school tenancy, and Stripe seat-based billing.

Three things the original brief did not list are added here because a production build cannot ship without them: a **security & compliance epic** (minors' data under Tunisian Law 2004-63 / INPDP, consent, encryption, pen-test), a **curriculum content epic** (the knowledge graph and a calibrated item bank — the DKT model is useless without KC-tagged items), and a **subject-expansion epic** (per-subject KC graphs, item banks, widget packages and judge verifiers — symbolic for maths/physics/technique, rubric-based for éco/gestion). An observability / load-testing / DR epic closes the loop on the "50,000 students the night before the Bac" requirement.

## 2. Teams and capacity

| Team | Headcount | Owns |
|---|---|---|
| Platform / DevOps | 2 | Terraform, EKS, Kafka, observability, CI/CD |
| Backend (Node.js / TypeScript) | 3 | Microservices, API gateway, multi-tenancy, billing |
| ML Engineering (Python / PyTorch) | 2 | pyKT, SAINT+, IRT, Kubeflow, TorchServe, feature store |
| LLM / Applied AI | 1 | LiteLLM, RAG, LLM-as-a-Judge, prompt registry |
| Frontend (Next.js / R3F) | 3 | App shell, physics widgets, offline PWA, i18n |
| Data Engineering | 1 | Schema registry, Snowflake, dbt, data quality |
| QA / SDET | 1 | Playwright, k6, contract tests, release gates |
| Product + Curriculum | 6 | One subject lead per track (Physics, Maths, Sciences, Technique, Éco/Gestion) + head of curriculum; KC graphs, item banks, pedagogy sign-off |

Total: 19 people. At a conservative 6 points per person per sprint across the 13 engineering roles plus 6 curriculum roles (who own the E04/E13 content tickets), capacity is ≈ 110 points/sprint; the plan below peaks at 102 points in the busiest sprint, so the 10-month horizon carries roughly a two-sprint buffer before the Bac window. Subject content tracks are independent, so a late subject slips its own release wave, not the physics + maths go-live.

## 3. Roadmap by phase

| Phase | Sprints | Dates | Focus |
|---|---|---|---|
| Phase 0 — Foundations | S1–S3 | 2026-11-02 → 2026-12-13 | Infra, security baseline, CI/CD, data contracts. Nothing user-facing ships; everything later depends on this. |
| Phase 1 — Data Plane | S3–S6 | 2026-11-30 → 2027-01-24 | Kafka telemetry, warehouse, curriculum knowledge graph, item bank. Produces the training data the Brain needs. |
| Phase 2 — Intelligence | S6–S11 | 2027-01-11 → 2027-04-04 | DKT models, cold-start IRT, routing service, LLM gateway + guardrails. The core differentiator. |
| Phase 3 — Product Surfaces | S8–S14 | 2027-02-08 → 2027-05-16 | Next.js app, WebGL sandboxes, Socratic tutor UX, offline mode, gamification. |
| Phase 4 — B2B & Hardening | S12–S17 | 2027-04-05 → 2027-06-27 | Multi-tenant school portals, parent app, Stripe billing, load/chaos testing, DR. |
| Phase 5 — Launch | S17–S18 | 2027-06-14 → 2027-07-11 | Pilot cohorts, exam-season readiness, war-room runbooks, go-live with Physics + Maths. |
| Phase 6 — Subject Expansion | S19–S20 | 2027-07-12 → 2027-08-08 | Sciences, Sciences techniques and Économie & Gestion released on the same engine (content tracks run in parallel from S9). |

### Sprint calendar and load

| Sprint | Dates | Tickets | Points | Epics active |
|---|---|---|---|---|
| S1 | 2026-11-02 – 2026-11-15 | 2 | 10 | E01 |
| S2 | 2026-11-16 – 2026-11-29 | 4 | 29 | E01, E02 |
| S3 | 2026-11-30 – 2026-12-13 | 9 | 55 | E01, E02, E03, E04 |
| S4 | 2026-12-14 – 2026-12-27 | 6 | 47 | E01, E02, E03, E04, E09 |
| S5 | 2026-12-28 – 2027-01-10 | 7 | 49 | E01, E02, E03, E04, E09 |
| S6 | 2027-01-11 – 2027-01-24 | 13 | 102 | E01, E02, E03, E04, E05, E07, E09, E11, E12 |
| S7 | 2027-01-25 – 2027-02-07 | 10 | 84 | E02, E03, E05, E06, E07, E09, E12 |
| S8 | 2027-02-08 – 2027-02-21 | 9 | 94 | E02, E04, E05, E07, E09, E12 |
| S9 | 2027-02-22 – 2027-03-07 | 10 | 81 | E03, E05, E06, E07, E08, E09, E13 |
| S10 | 2027-03-08 – 2027-03-21 | 11 | 73 | E05, E06, E07, E08, E10, E13 |
| S11 | 2027-03-22 – 2027-04-04 | 11 | 90 | E04, E06, E07, E08, E09, E10, E13 |
| S12 | 2027-04-05 – 2027-04-18 | 6 | 55 | E06, E09, E11, E12, E13 |
| S13 | 2027-04-19 – 2027-05-02 | 8 | 70 | E06, E08, E09, E10, E11, E13 |
| S14 | 2027-05-03 – 2027-05-16 | 9 | 79 | E08, E10, E11, E12, E13 |
| S15 | 2027-05-17 – 2027-05-30 | 7 | 61 | E02, E11, E12, E13 |
| S16 | 2027-05-31 – 2027-06-13 | 4 | 31 | E11, E12, E13 |
| S17 | 2027-06-14 – 2027-06-27 | 2 | 11 | E12, E13 |
| S18 | 2027-06-28 – 2027-07-11 | 2 | 10 | E12, E13 |
| S19 | 2027-07-12 – 2027-07-25 | 1 | 5 | E13 |
| S20 | 2027-07-26 – 2027-08-08 | 1 | 5 | E13 |

## 4. Epic summary

| ID | Epic | Phase | Priority | Tickets | Points | Sprints |
|---|---|---|---|---|---|---|
| E01 | Platform Foundations: Infrastructure & DevOps | Phase 0 | Highest | 11 | 65 | S1–S6 |
| E02 | Identity, Security & Compliance | Phase 0 | Highest | 10 | 60 | S2–S15 |
| E03 | Event-Driven Telemetry & Data Warehouse | Phase 1 | Highest | 10 | 68 | S3–S9 |
| E04 | Curriculum Knowledge Graph & Content Pipeline (multi-subject) | Phase 1 | High | 9 | 81 | S3–S11 |
| E05 | Deep Knowledge Tracing Core | Phase 2 | Highest | 10 | 84 | S6–S10 |
| E06 | Adaptive Routing & Recommendation Service | Phase 2 | Highest | 8 | 57 | S7–S13 |
| E07 | Multi-Model LLM Gateway & Guardrails | Phase 2 | Highest | 10 | 77 | S6–S11 |
| E08 | Socratic AI Tutor Experience | Phase 3 | High | 7 | 42 | S9–S14 |
| E09 | Interactive Learning Frontend (Next.js / WebGL) | Phase 3 | Highest | 11 | 114 | S4–S13 |
| E10 | Learner Engagement & Gamification | Phase 3 | Medium | 5 | 26 | S10–S14 |
| E11 | Institution & Parent B2B Portals (Multi-Tenancy) | Phase 4 | High | 9 | 79 | S6–S16 |
| E12 | Observability, Quality & Release Readiness | Phase 4 | High | 10 | 81 | S6–S18 |
| E13 | Subject Expansion: Maths, Sciences, Technique, Économie & Gestion | Phase 6 | High | 22 | 207 | S9–S20 |

## 5. Critical path

The longest dependency chain runs through the data plane into the model and the router, then into launch and the final subject wave. Slips anywhere on this chain move the release dates:

`T001` Bootstrap Terraform mono-repo (S1) → `T002` Provision multi-AZ VPC, subnets, NAT and VPC endpoints  (S1) → `T021` Provision Apache Kafka (MSK) cluster (S3) → `T027` Configure Kafka Connect sinks to Snowflake (S5) → `T028` Model the learning-analytics warehouse in dbt (staging  (S6) → `T040` Benchmark SAINT, SAINT+, SAKT and AKT on public dataset (S6) → `T041` Integrate pyKT into the ML mono-repo (S6) → `T042` Implement production SAINT+ model (S7) → `T046` Deploy TorchServe inference service (S8) → `T052` Build the routing microservice (Node.js) (S9) → `T104` Run Bac-eve load test (S14) → `T109` Prepare the exam-season war room (S17) → `T110` Production go-live (Physics + Maths) and 30-day hyperca (S18) → `T131` Release wave 2 (S19) → `T132` Release wave 3 (S20)


## 6. Backlog detail

Conventions: story points are Fibonacci (13 = split before sprint entry); *Blocked by* references the Issue IDs in this file and in the CSV.


### E01 — Platform Foundations: Infrastructure & DevOps

**Phase:** Phase 0 · **Priority:** Highest · **Component:** Platform · **11 tickets / 65 pts**

**Goal.** Reproducible, auto-scaling AWS EKS platform provisioned 100% from Terraform, with blue/green CI/CD and Datadog tracing from day one.

**Definition of done.** A fresh AWS account can be brought to a running staging environment in under 60 minutes from `terraform apply` with zero manual console steps.

| ID | Type | Summary | Pts | Priority | Sprint | Blocked by |
|---|---|---|---|---|---|---|
| T001 | Task | Bootstrap Terraform mono-repo with remote state, workspaces and policy checks | 5 | Highest | S1 | — |
| T002 | Task | Provision multi-AZ VPC, subnets, NAT and VPC endpoints via Terraform | 5 | Highest | S1 | T001 |
| T003 | Task | Deploy AWS EKS cluster with managed node groups, Karpenter and GPU node pool | 8 | Highest | S2 | T002 |
| T004 | Task | Set up ArgoCD GitOps with Helm charts and per-environment overlays | 5 | Highest | S2 | T003 |
| T005 | Task | Deploy Kong API Gateway with rate limiting, JWT validation and per-tenant quotas | 5 | Highest | S3 | T003 |
| T006 | Task | Build GitHub Actions CI pipeline: lint, unit, contract, container scan, SBOM | 8 | Highest | S2 | T001 |
| T007 | Task | Roll out Datadog APM, distributed tracing, log pipeline and memory-leak watchdogs | 8 | Highest | S3 | T003 |
| T008 | Task | Implement zero-downtime blue/green deployments with automated rollback | 8 | High | S4 | T004, T007 |
| T009 | Task | Stand up n8n agentic automation for release notes, flaky-test triage and incident paging | 5 | Medium | S5 | T006 |
| T010 | Task | Provision ephemeral preview environments per pull request | 5 | Medium | S5 | T004, T005 |
| T011 | Task | Implement FinOps guardrails: tagging policy, budgets, Kubecost and spot strategy | 3 | Medium | S6 | T003 |

#### T001 · Bootstrap Terraform mono-repo with remote state, workspaces and policy checks

*Task · 5 pts · Highest · APL Sprint 1 · labels: terraform, iac*

Create the `infra/` Terraform repository: S3 + DynamoDB remote state with locking, `dev`/`staging`/`prod` workspaces, module layout (network, eks, data, observability), pre-commit with tflint + checkov, and Terraform Cloud/Atlantis plan-on-PR.

Acceptance criteria:

- `terraform plan` runs on every PR and posts the diff as a comment
- checkov policy pack blocks public S3 buckets, open security groups and unencrypted volumes
- State is encrypted at rest and locked; a second concurrent apply is rejected

#### T002 · Provision multi-AZ VPC, subnets, NAT and VPC endpoints via Terraform

*Task · 5 pts · Highest · APL Sprint 1 · labels: terraform, network*

Three-AZ VPC in eu-west-3 (Paris — closest region to Tunisia with full service coverage), public/private/isolated subnet tiers, NAT gateways per AZ, VPC endpoints for S3, ECR, Secrets Manager and CloudWatch to avoid NAT egress cost.

Acceptance criteria:

- All data-plane subnets have no route to an Internet Gateway
- Flow logs enabled and shipped to the logging account
- Network module reused unchanged across dev/staging/prod

Blocked by: T001 (Bootstrap Terraform mono-repo with remote state, workspaces and policy checks)

#### T003 · Deploy AWS EKS cluster with managed node groups, Karpenter and GPU node pool

*Task · 8 pts · Highest · APL Sprint 2 · labels: eks, kubernetes, karpenter*

EKS 1.31+ via Terraform: system node group (on-demand), general workload pool (Karpenter, spot-first with on-demand fallback), and a tainted GPU pool (g5 family) for TorchServe and local LLM inference. IRSA for pod identity, EBS/EFS CSI drivers, cluster autoscaler replaced by Karpenter.

Acceptance criteria:

- Cluster passes `kube-bench` CIS benchmark with no failures
- Karpenter scales a 500-pod synthetic load from 0 to ready in < 4 minutes
- GPU pool only schedules pods carrying the `nvidia.com/gpu` toleration

Blocked by: T002 (Provision multi-AZ VPC, subnets, NAT and VPC endpoints via Terraform)

#### T004 · Set up ArgoCD GitOps with Helm charts and per-environment overlays

*Task · 5 pts · Highest · APL Sprint 2 · labels: argocd, gitops, helm*

ArgoCD app-of-apps pattern; every microservice has a Helm chart with values overlays for dev/staging/prod; image tags promoted by commit, not by hand. Sealed Secrets or External Secrets Operator for secret injection from AWS Secrets Manager.

Acceptance criteria:

- A merge to `main` of a chart change reconciles to staging within 2 minutes
- No secret value exists in Git in plaintext (checked by gitleaks in CI)
- ArgoCD sync drift alerts route to #platform-alerts

Blocked by: T003 (Deploy AWS EKS cluster with managed node groups, Karpenter and GPU node pool)

#### T005 · Deploy Kong API Gateway with rate limiting, JWT validation and per-tenant quotas

*Task · 5 pts · Highest · APL Sprint 3 · labels: kong, api-gateway*

Kong (OSS or Konnect) as ingress: JWT plugin validating tokens from the identity provider, rate-limiting plugin keyed by user and tenant, request-size limits, and per-route canary weights for blue/green cutover.

Acceptance criteria:

- Unauthenticated calls to any `/api/v1/*` route return 401 at the gateway, never reaching a service
- Rate limit of 60 req/min/user on tutor endpoints enforced and observable in Datadog
- Canary weight can be shifted 0→100% without a redeploy

Blocked by: T003 (Deploy AWS EKS cluster with managed node groups, Karpenter and GPU node pool)

#### T006 · Build GitHub Actions CI pipeline: lint, unit, contract, container scan, SBOM

*Task · 8 pts · Highest · APL Sprint 2 · labels: ci, github-actions, security*

Reusable workflow per language (TypeScript, Python): lint, type-check, unit tests with coverage gates (≥ 80% backend, ≥ 70% frontend), Pact contract tests, Trivy image scan, Syft SBOM, signed images with cosign. Caches keyed on lockfiles.

Acceptance criteria:

- A PR cannot merge with a failing check or a Critical CVE in the image
- Median CI run for a backend service < 8 minutes
- Every image pushed to ECR is signed and has an attached SBOM

Blocked by: T001 (Bootstrap Terraform mono-repo with remote state, workspaces and policy checks)

#### T007 · Roll out Datadog APM, distributed tracing, log pipeline and memory-leak watchdogs

*Task · 8 pts · Highest · APL Sprint 3 · labels: datadog, otel, observability*

Datadog agent as DaemonSet; OpenTelemetry SDKs in Node.js and Python services with W3C trace context propagated through Kong and Kafka headers; log pipelines with PII scrubbing; monitors for RSS growth > 20%/hour per pod (memory leak detector).

Acceptance criteria:

- A single trace spans Kong → Node service → Kafka producer → Python consumer
- Logs containing student email or national ID patterns are redacted before indexing
- Memory-leak monitor fires on a seeded leaking pod within 30 minutes

Blocked by: T003 (Deploy AWS EKS cluster with managed node groups, Karpenter and GPU node pool)

#### T008 · Implement zero-downtime blue/green deployments with automated rollback

*Task · 8 pts · High · APL Sprint 4 · labels: argo-rollouts, deploy*

Argo Rollouts blue/green strategy: new ReplicaSet receives synthetic smoke traffic and 5% real traffic, promotion gated on Datadog error-rate and latency analysis templates; automatic rollback if SLO burn exceeds threshold within 10 minutes.

Acceptance criteria:

- Deploying a build that returns 5xx on the health route is automatically rolled back within 3 minutes
- Zero failed user requests during a staging deploy under 500 RPS synthetic load
- Rollback is a single `kubectl argo rollouts undo` or ArgoCD button

Blocked by: T004 (Set up ArgoCD GitOps with Helm charts and per-environment overlays), T007 (Roll out Datadog APM, distributed tracing, log pipeline and memory-leak watchdogs)

#### T009 · Stand up n8n agentic automation for release notes, flaky-test triage and incident paging

*Task · 5 pts · Medium · APL Sprint 5 · labels: n8n, automation*

Self-hosted n8n in the tooling namespace: workflows that (1) draft release notes from merged PRs via the LLM gateway, (2) auto-label flaky tests after 3 non-deterministic failures and open a Jira ticket, (3) enrich PagerDuty incidents with recent deploys and Datadog links.

Acceptance criteria:

- Release notes PR is opened automatically on every tag
- Flaky test detection creates a Jira ticket with the failing test name and last 5 runs
- n8n credentials are stored in Secrets Manager, not in the n8n UI

Blocked by: T006 (Build GitHub Actions CI pipeline: lint, unit, contract, container scan, SBOM)

#### T010 · Provision ephemeral preview environments per pull request

*Task · 5 pts · Medium · APL Sprint 5 · labels: preview-env, argocd*

ArgoCD ApplicationSet + Kong route per PR: a full stack (frontend, API, seeded Postgres, shared Kafka topic prefix) at `pr-123.preview.example.tn`, torn down on merge. Budget guardrail destroys previews idle > 48 h.

Acceptance criteria:

- A preview URL is posted on the PR within 6 minutes of push
- Preview databases are seeded with anonymised fixtures, never prod data
- Monthly preview-env spend reported in Datadog cost dashboard

Blocked by: T004 (Set up ArgoCD GitOps with Helm charts and per-environment overlays), T005 (Deploy Kong API Gateway with rate limiting, JWT validation and per-tenant quotas)

#### T011 · Implement FinOps guardrails: tagging policy, budgets, Kubecost and spot strategy

*Task · 3 pts · Medium · APL Sprint 6 · labels: finops*

Mandatory cost-allocation tags enforced by SCP; AWS Budgets with 80/100% alerts per environment; Kubecost for per-namespace cost; GPU pool scheduled to scale to zero outside retraining windows.

Acceptance criteria:

- Untagged resource creation is denied by SCP
- GPU nodes are zero between retraining jobs (verified over a 7-day window)
- Weekly cost report posted to #eng-leadership automatically

Blocked by: T003 (Deploy AWS EKS cluster with managed node groups, Karpenter and GPU node pool)


### E02 — Identity, Security & Compliance

**Phase:** Phase 0 · **Priority:** Highest · **Component:** Security · **10 tickets / 60 pts**

**Goal.** Centralised identity (students, parents, teachers, school admins), encryption everywhere, and compliance with Tunisian Law 2004-63 (INPDP) plus GDPR-equivalent controls for minors' data.

**Definition of done.** External penetration test passes with no High/Critical findings; data-protection impact assessment signed off before first pilot school.

| ID | Type | Summary | Pts | Priority | Sprint | Blocked by |
|---|---|---|---|---|---|---|
| T012 | Task | Deploy Keycloak identity provider with student / parent / teacher / school-admin realms | 8 | Highest | S2 | T003 |
| T013 | Story | As a parent, I give verifiable consent before my under-18 child's account is activated | 5 | Highest | S4 | T012 |
| T014 | Task | Implement attribute-based authorisation middleware shared by all Node.js services | 5 | Highest | S3 | T012 |
| T015 | Task | Encryption at rest and in transit: KMS CMKs, TLS everywhere, field-level encryption for PII | 8 | Highest | S3 | T003 |
| T016 | Task | Centralise secrets in AWS Secrets Manager with automatic rotation | 3 | Highest | S3 | T004 |
| T017 | Task | Produce the Data Protection Impact Assessment and INPDP declaration file | 5 | High | S5 | T013 |
| T018 | Task | Implement data lifecycle: retention, right-to-erasure and export pipelines | 8 | High | S7 | T017 |
| T019 | Task | Deploy AWS WAF + Shield, bot protection and abuse rate limiting on public endpoints | 5 | High | S6 | T005 |
| T020 | Task | Commission third-party penetration test and remediate findings | 8 | High | S15 | T014, T019 |
| T022 | Task | Build immutable audit log for admin actions and data access | 5 | Medium | S8 | T021 |

#### T012 · Deploy Keycloak identity provider with student / parent / teacher / school-admin realms

*Task · 8 pts · Highest · APL Sprint 2 · labels: keycloak, oidc, auth*

Keycloak on EKS (HA, Postgres-backed) as the single OIDC issuer. Roles: student, parent, teacher, school_admin, platform_admin. Social login (Google) for students, email+password with Arabic/French UI, phone OTP for parents. Short-lived access tokens (15 min) and rotating refresh tokens.

Acceptance criteria:

- Kong validates Keycloak-issued JWTs including `tenant_id` and `roles` claims
- Password policy ≥ 12 chars, breached-password check via HIBP k-anonymity
- Login page renders correctly RTL in Arabic

Blocked by: T003 (Deploy AWS EKS cluster with managed node groups, Karpenter and GPU node pool)

#### T013 · As a parent, I give verifiable consent before my under-18 child's account is activated

*Story · 5 pts · Highest · APL Sprint 4 · labels: compliance, consent, minors*

Minors (the majority of Bac students are 17–19) require guardian consent under Tunisian Law 2004-63 and the INPDP's guidance. Implement a consent flow: student signs up → parent phone/email captured → OTP + consent screen → account activates. Consent record is immutable and exportable.

Acceptance criteria:

- An under-18 account cannot access learning content until consent is recorded
- Consent record stores timestamp, parent identifier hash, policy version, IP
- Parent can revoke consent, which freezes the student account within 1 minute

Blocked by: T012 (Deploy Keycloak identity provider with student / parent / teacher / school-admin realms)

#### T014 · Implement attribute-based authorisation middleware shared by all Node.js services

*Task · 5 pts · Highest · APL Sprint 3 · labels: authz, opa*

Shared `@apl/authz` package: policy evaluation (OPA/Cedar) using JWT claims + resource tenant. Every route handler declares required permission; missing declaration fails CI via lint rule.

Acceptance criteria:

- A teacher token cannot read another school's cohort (automated test)
- Routes without an authz decorator fail the lint step
- Policy decisions are logged with decision ID for audit

Blocked by: T012 (Deploy Keycloak identity provider with student / parent / teacher / school-admin realms)

#### T015 · Encryption at rest and in transit: KMS CMKs, TLS everywhere, field-level encryption for PII

*Task · 8 pts · Highest · APL Sprint 3 · labels: encryption, kms, mtls*

Customer-managed KMS keys per environment; RDS, EBS, S3, Kafka (MSK) and Snowflake encrypted with CMKs; mTLS inside the mesh (Linkerd or Istio ambient); application-level envelope encryption for national ID, phone and parent contact fields.

Acceptance criteria:

- No listener accepts plaintext HTTP inside or outside the cluster
- Decrypting a PII field requires a KMS call that is logged in CloudTrail
- Key rotation runs annually without downtime (tested in staging)

Blocked by: T003 (Deploy AWS EKS cluster with managed node groups, Karpenter and GPU node pool)

#### T016 · Centralise secrets in AWS Secrets Manager with automatic rotation

*Task · 3 pts · Highest · APL Sprint 3 · labels: secrets*

All DB, Kafka, Stripe, OpenAI/Anthropic keys in Secrets Manager; External Secrets Operator syncs to Kubernetes; Lambda rotation for RDS credentials every 30 days; gitleaks pre-commit + CI.

Acceptance criteria:

- Rotating the Postgres password causes zero failed requests (connection pool reload)
- A committed fake secret is caught by gitleaks before push
- Secrets access is scoped per service IAM role (IRSA)

Blocked by: T004 (Set up ArgoCD GitOps with Helm charts and per-environment overlays)

#### T017 · Produce the Data Protection Impact Assessment and INPDP declaration file

*Task · 5 pts · High · APL Sprint 5 · labels: compliance, dpia, inpdp*

Document data flows, lawful basis, retention, minors' data handling, cross-border transfer (AWS Paris) and the telemetry profiling risk (DKT constitutes automated profiling of minors). Prepare the INPDP processing declaration. Legal counsel review.

Acceptance criteria:

- DPIA signed by DPO and CTO
- Retention schedule implemented in code (see data lifecycle story)
- Telemetry profiling is disclosed in the privacy notice in Arabic and French

Blocked by: T013 (As a parent, I give verifiable consent before my under-18 child's account is activated)

#### T018 · Implement data lifecycle: retention, right-to-erasure and export pipelines

*Task · 8 pts · High · APL Sprint 7 · labels: gdpr, erasure, retention*

Scheduled jobs that purge raw telemetry > 24 months, pseudonymise inactive accounts > 12 months, and fulfil erasure requests across Postgres, Snowflake, Redis, Kafka (tombstones) and pgvector within 30 days. Self-service data export (JSON) for students and parents.

Acceptance criteria:

- Erasure request leaves no record keyed by the user ID in any store (automated audit script)
- Model training excludes erased users on the next retrain
- Export completes in < 10 minutes for a typical student

Blocked by: T017 (Produce the Data Protection Impact Assessment and INPDP declaration file)

#### T019 · Deploy AWS WAF + Shield, bot protection and abuse rate limiting on public endpoints

*Task · 5 pts · High · APL Sprint 6 · labels: waf, ddos*

WAF managed rule groups (OWASP core, known bad inputs), geo-aware rate rules (Tunisia + diaspora regions whitelisted at higher limits), CAPTCHA challenge on signup after threshold, Shield Advanced on the CloudFront distribution.

Acceptance criteria:

- OWASP ZAP baseline scan reports no High findings on the public API
- Credential-stuffing simulation (10k attempts) is blocked within 60 seconds
- WAF logs land in Datadog with attacker IP and rule ID

Blocked by: T005 (Deploy Kong API Gateway with rate limiting, JWT validation and per-tenant quotas)

#### T020 · Commission third-party penetration test and remediate findings

*Task · 8 pts · High · APL Sprint 15 · labels: pentest, security*

Engage an external firm for a grey-box test of the web app, APIs, multi-tenancy boundaries and the LLM tutor (prompt-injection, data exfiltration via RAG). Two-week remediation window; re-test.

Acceptance criteria:

- Zero Critical/High findings open at re-test
- Prompt-injection attempts cannot extract other students' data or system prompts
- Findings tracked as Jira Bugs linked to this task

Blocked by: T014 (Implement attribute-based authorisation middleware shared by all Node.js services), T019 (Deploy AWS WAF + Shield, bot protection and abuse rate limiting on public endpoints)

#### T022 · Build immutable audit log for admin actions and data access

*Task · 5 pts · Medium · APL Sprint 8 · labels: audit*

Append-only audit stream (Kafka → S3 Object Lock) for: role changes, consent changes, bulk exports, teacher views of student profiles, billing changes. Queryable via Athena; surfaced in the admin console.

Acceptance criteria:

- Audit records cannot be modified or deleted for 7 years (Object Lock compliance mode)
- Every teacher view of a student profile is auditable with timestamp and reason
- Audit query for a user ID returns in < 30 s

Blocked by: T021 (Provision Apache Kafka (MSK) cluster with Schema Registry and topic conventions)


### E03 — Event-Driven Telemetry & Data Warehouse

**Phase:** Phase 1 · **Priority:** Highest · **Component:** Data · **10 tickets / 68 pts**

**Goal.** Every learner micro-interaction (slider drag, hover, hesitation, confidence, answer) is captured as a schema-versioned Kafka event and lands in Snowflake within 5 minutes and in Redis within 200 ms.

**Definition of done.** Sustained 50k events/sec with p99 end-to-end lag < 5 min to warehouse; zero schema-breaking deploys thanks to the registry.

| ID | Type | Summary | Pts | Priority | Sprint | Blocked by |
|---|---|---|---|---|---|---|
| T021 | Task | Provision Apache Kafka (MSK) cluster with Schema Registry and topic conventions | 8 | Highest | S3 | T002 |
| T023 | Task | Define the learner interaction event taxonomy and Avro/Protobuf schemas | 5 | Highest | S3 | T021 |
| T024 | Task | Build the Next.js telemetry SDK: batching, offline buffering, hesitation and time-to-first-click | 8 | Highest | S4 | T023 |
| T025 | Task | Build the telemetry ingestion service (HTTP → Kafka) with validation and backpressure | 8 | Highest | S4 | T023, T005 |
| T026 | Task | Deploy Redis Cluster (ElastiCache) and the real-time aggregation consumer | 8 | Highest | S5 | T021 |
| T027 | Task | Configure Kafka Connect sinks to Snowflake with exactly-once semantics | 5 | Highest | S5 | T021 |
| T028 | Task | Model the learning-analytics warehouse in dbt (staging → marts) with tests | 8 | High | S6 | T027 |
| T029 | Task | Implement data-quality monitoring and anomaly alerts on telemetry volume and shape | 5 | High | S7 | T028 |
| T030 | Task | Stand up the online/offline feature store for student state | 8 | High | S7 | T026, T028 |
| T031 | Task | Build event replay and backfill tooling for reprocessing historical telemetry | 5 | Medium | S9 | T027 |

#### T021 · Provision Apache Kafka (MSK) cluster with Schema Registry and topic conventions

*Task · 8 pts · Highest · APL Sprint 3 · labels: kafka, msk, schema-registry*

Amazon MSK (3 brokers across AZs, KRaft), Confluent/Apicurio Schema Registry, topic naming `<domain>.<entity>.<event>.v<n>`, partitioning by `student_id` for ordering, 7-day retention on raw topics, compacted topics for state. Terraform-managed ACLs per service.

Acceptance criteria:

- Producers cannot publish a message that fails schema validation
- Broker loss in one AZ causes no message loss (acks=all, min.insync.replicas=2)
- Topic creation requires a PR to the topics module

Blocked by: T002 (Provision multi-AZ VPC, subnets, NAT and VPC endpoints via Terraform)

#### T023 · Define the learner interaction event taxonomy and Avro/Protobuf schemas

*Task · 5 pts · Highest · APL Sprint 3 · labels: schema, events, avro*

Event catalogue co-designed with ML: `item.presented`, `item.interaction` (slider_move, drag, hover_enter/exit, focus, keystroke_burst), `item.hesitation` (idle > 3 s after presentation), `item.answered` (response, correct, latency_ms, confidence_1_5, attempts), `hint.requested`, `hint.shown`, `tutor.message`, `session.start/end`. Each carries `student_id`, `tenant_id`, `item_id`, `kc_ids[]`, `client_ts`, `server_ts`, `session_id`, `device`, `app_version`.

Acceptance criteria:

- Schemas versioned in the registry with backward compatibility enforced
- Every event has a documented owner, producer and consumers in the data catalogue
- ML team signs off that the schema contains everything SAINT+ features need

Blocked by: T021 (Provision Apache Kafka (MSK) cluster with Schema Registry and topic conventions)

#### T024 · Build the Next.js telemetry SDK: batching, offline buffering, hesitation and time-to-first-click

*Task · 8 pts · Highest · APL Sprint 4 · labels: telemetry-sdk, nextjs*

`@apl/telemetry` client: captures DOM/R3F interactions with requestIdleCallback, computes time-to-first-click and hesitation windows client-side, batches events (≤ 50 or 2 s), persists unsent batches in IndexedDB, replays on reconnect with idempotency keys, respects Do-Not-Track for non-essential events.

Acceptance criteria:

- No event is lost when the tab is closed mid-batch (sendBeacon + IndexedDB replay)
- SDK adds < 15 ms to Interaction-to-Next-Paint on a mid-range Android device
- Duplicate replay after reconnect is de-duplicated server-side by idempotency key

Blocked by: T023 (Define the learner interaction event taxonomy and Avro/Protobuf schemas)

#### T025 · Build the telemetry ingestion service (HTTP → Kafka) with validation and backpressure

*Task · 8 pts · Highest · APL Sprint 4 · labels: ingestion, fastify*

Node.js (Fastify) ingestion edge behind Kong: validates JWT, enforces schema, enriches with server timestamp and geo, produces to Kafka with idempotent producer. Returns 202 immediately; applies 429 with Retry-After when Kafka lag exceeds threshold.

Acceptance criteria:

- Sustains 50k events/s on 6 pods with p99 < 30 ms
- Invalid events are routed to a dead-letter topic with the validation error
- Backpressure test: Kafka paused for 60 s → clients receive 429, no OOM

Blocked by: T023 (Define the learner interaction event taxonomy and Avro/Protobuf schemas), T005 (Deploy Kong API Gateway with rate limiting, JWT validation and per-tenant quotas)

#### T026 · Deploy Redis Cluster (ElastiCache) and the real-time aggregation consumer

*Task · 8 pts · Highest · APL Sprint 5 · labels: redis, stream-processing*

ElastiCache Redis 7 cluster mode; Kafka Streams / Flink-lite consumer in Node.js that maintains per-student session state, streaks, XP and sorted-set leaderboards with TTLs; exposes a read API for the UI.

Acceptance criteria:

- Streak/XP visible in UI within 200 ms of the answer event (p95)
- Consumer restart replays from committed offset with no double counting
- Redis memory < 70% at 100k active students (capacity model documented)

Blocked by: T021 (Provision Apache Kafka (MSK) cluster with Schema Registry and topic conventions)

#### T027 · Configure Kafka Connect sinks to Snowflake with exactly-once semantics

*Task · 5 pts · Highest · APL Sprint 5 · labels: kafka-connect, snowflake*

Snowflake Kafka connector (Snowpipe Streaming) for all `learner.*` topics into a RAW schema; Iceberg tables on S3 as a cost-efficient cold copy; connector tasks scaled by partition count; DLQ monitoring.

Acceptance criteria:

- p99 event-to-queryable latency in Snowflake < 5 minutes
- Row counts reconcile with Kafka offsets daily (automated check)
- Connector failure pages data-eng on-call within 5 minutes

Blocked by: T021 (Provision Apache Kafka (MSK) cluster with Schema Registry and topic conventions)

#### T028 · Model the learning-analytics warehouse in dbt (staging → marts) with tests

*Task · 8 pts · High · APL Sprint 6 · labels: dbt, warehouse*

dbt project: staging models per event type, `fct_interactions`, `fct_attempts`, `dim_student`, `dim_item`, `dim_kc`, and the `ml_training_sequences` mart consumed by pyKT (one row per student-attempt with KC tags, latency, correctness, ordered). Schema and freshness tests; docs site.

Acceptance criteria:

- `ml_training_sequences` matches the pyKT expected columns exactly
- dbt tests cover uniqueness, not-null and referential integrity on all facts
- Daily build < 20 minutes at 10M interactions/day

Blocked by: T027 (Configure Kafka Connect sinks to Snowflake with exactly-once semantics)

#### T029 · Implement data-quality monitoring and anomaly alerts on telemetry volume and shape

*Task · 5 pts · High · APL Sprint 7 · labels: data-quality*

Great Expectations / Soda checks on RAW and marts: event volume by type vs. 7-day baseline, null rates, latency distribution drift, duplicate rate. Alerts to #data-quality; dashboard in Datadog.

Acceptance criteria:

- A 30% drop in `item.answered` volume for one app version alerts within 15 minutes
- Schema drift from a new client release is detected before dbt fails
- DQ dashboard shows per-topic freshness

Blocked by: T028 (Model the learning-analytics warehouse in dbt (staging → marts) with tests)

#### T030 · Stand up the online/offline feature store for student state

*Task · 8 pts · High · APL Sprint 7 · labels: feature-store, feast*

Feast (or home-grown) with Snowflake offline store and Redis online store: rolling accuracy per KC, mean latency, hint dependency ratio, days-to-exam, session count. Materialised hourly; online reads < 5 ms.

Acceptance criteria:

- Training and serving features are computed from the same definitions (no skew test passes)
- Online feature read p99 < 5 ms
- Feature definitions versioned and reviewed by ML

Blocked by: T026 (Deploy Redis Cluster (ElastiCache) and the real-time aggregation consumer), T028 (Model the learning-analytics warehouse in dbt (staging → marts) with tests)

#### T031 · Build event replay and backfill tooling for reprocessing historical telemetry

*Task · 5 pts · Medium · APL Sprint 9 · labels: replay, ops*

CLI + Airflow DAG to replay a topic time-range into a target consumer group or to re-sink into Snowflake after a bug fix; dry-run mode; rate-limited.

Acceptance criteria:

- Replay of 24 h of events completes in < 2 h without impacting live consumers
- Backfill is idempotent (re-running produces identical warehouse state)
- Runbook documented

Blocked by: T027 (Configure Kafka Connect sinks to Snowflake with exactly-once semantics)


### E04 — Curriculum Knowledge Graph & Content Pipeline (multi-subject)

**Phase:** Phase 1 · **Priority:** High · **Component:** Curriculum · **9 tickets / 81 pts**

**Goal.** A subject-agnostic content system: knowledge-component graphs, a tagged and calibrated item bank, a textbook RAG corpus and a teacher authoring workflow, where every object carries a first-class `subject` and `track` (Bac section). Physics is the first subject loaded here; the other four load through E13 on the same tooling.

**Definition of done.** Tooling supports any subject with zero code changes; Physics track published with ≥ 400 KCs and ≥ 6,000 tagged items, each with ≥ 1 KC tag and pedagogical review.

| ID | Type | Summary | Pts | Priority | Sprint | Blocked by |
|---|---|---|---|---|---|---|
| T032 | Task | Design the knowledge-component (KC) graph schema and store | 5 | High | S3 | — |
| T033 | Task | Make `subject` and `track` first-class across the KC graph, item bank, routing, mastery API and telemetry | 8 | Highest | S3 | T032, T023 |
| T034 | Story | As a curriculum lead, I author and version the KC graph in a web editor with review workflow | 8 | High | S5 | T032, T033 |
| T035 | Task | Populate the Physics KC graph for all Bac tracks (first subject) | 13 | High | S6 | T034 |
| T036 | Task | Define the item (question) data model: types, KC tags, difficulty, distractor rationale, media | 5 | High | S4 | T032 |
| T037 | Story | As a teacher-author, I create, preview and submit items for review in the authoring tool | 13 | High | S6 | T036 |
| T038 | Task | Build the Physics item bank: 6,000 tagged items including 10 years of past Bac papers | 13 | High | S8 | T037, T035 |
| T039 | Task | Ingest official textbooks into the RAG corpus with chapter/KC-aware chunking | 8 | High | S6 | T035 |
| T044 | Task | Run pilot item calibration and prune bad items | 8 | Medium | S11 | T038, T043 |

#### T032 · Design the knowledge-component (KC) graph schema and store

*Task · 5 pts · High · APL Sprint 3 · labels: knowledge-graph, curriculum*

Graph of concepts for the official Tunisian Bac physics programme by section (Sciences expérimentales, Mathématiques, Sciences techniques): nodes = KCs (e.g. `mech.newton2`, `elec.rlc.resonance`), edges = prerequisite / related / sub-concept, attributes = chapter, exam weight, difficulty prior. Stored in Postgres (ltree + edge table) with a cached in-memory graph in the routing service.

Acceptance criteria:

- Schema supports multiple programme tracks sharing KCs
- Cycle detection rejects circular prerequisites on write
- Graph export to JSON used by routing service and tutor RAG

#### T033 · Make `subject` and `track` first-class across the KC graph, item bank, routing, mastery API and telemetry

*Task · 8 pts · Highest · APL Sprint 3 · labels: multi-subject, data-model*

Add `subject_id` (physics, maths, sciences, technique, eco_gestion) and `track_id` (Bac section) to KCs, items, textbook chunks, routing decisions, mastery records, telemetry events and dashboard queries. Enrolment maps each student to a track and the subjects it contains; tenants can enable subjects independently. Shared engine, partitioned content.

Acceptance criteria:

- No table or event schema carrying curriculum content lacks `subject_id`
- Routing never serves an item from a subject the student is not enrolled in (automated test)
- Adding a new subject requires only configuration + content, no migration (verified by a dry run with a dummy subject)

Blocked by: T032 (Design the knowledge-component (KC) graph schema and store), T023 (Define the learner interaction event taxonomy and Avro/Protobuf schemas)

#### T034 · As a curriculum lead, I author and version the KC graph in a web editor with review workflow

*Story · 8 pts · High · APL Sprint 5 · labels: admin-tool, knowledge-graph*

Internal tool (Next.js admin) to add/edit KCs and edges, visual graph view, diff between versions, propose → review → publish workflow. Published version is immutable and referenced by items and models.

Acceptance criteria:

- Publishing a graph version requires a second reviewer approval
- Routing service picks up a new published version without redeploy
- Graph diff shows added/removed edges clearly

Blocked by: T032 (Design the knowledge-component (KC) graph schema and store), T033 (Make `subject` and `track` first-class across the KC graph, item bank, routing, mastery API and telemetry)

#### T035 · Populate the Physics KC graph for all Bac tracks (first subject)

*Task · 13 pts · High · APL Sprint 6 · labels: curriculum, content*

Curriculum team encodes all chapters of the official programme with ~400 KCs and prerequisite edges, cross-checked against the last 10 years of Bac exam topics for exam weight.

Acceptance criteria:

- ≥ 400 KCs with ≥ 600 edges published as v1.0
- Every past-exam question (10 years) maps to at least one KC
- Pedagogical sign-off recorded

Blocked by: T034 (As a curriculum lead, I author and version the KC graph in a web editor with review workflow)

#### T036 · Define the item (question) data model: types, KC tags, difficulty, distractor rationale, media

*Task · 5 pts · High · APL Sprint 4 · labels: item-bank, schema*

Item types: MCQ, numeric with tolerance, multi-step derivation, interactive widget (links to R3F component + parameter space), drag-to-order. Fields: KC tags with weights, IRT a/b/c priors, solution steps, distractor rationales (used by the tutor), Arabic/French variants, media refs, source (past exam year or authored).

Acceptance criteria:

- Item JSON schema published and validated at write time
- Interactive items declare their parameter ranges so randomised variants are generated
- Bilingual fields are mandatory for publish

Blocked by: T032 (Design the knowledge-component (KC) graph schema and store)

#### T037 · As a teacher-author, I create, preview and submit items for review in the authoring tool

*Story · 13 pts · High · APL Sprint 6 · labels: admin-tool, authoring*

Authoring UI with live preview (including interactive widgets), LaTeX math input, KC tag picker from the graph, difficulty estimate, and a review queue with comments. Bulk import from DOCX/CSV for legacy item sets.

Acceptance criteria:

- Author sees the item rendered exactly as a student would, in both languages
- Review queue supports approve / request-changes with inline comments
- Bulk import of 500 legacy MCQs completes with a validation report

Blocked by: T036 (Define the item (question) data model: types, KC tags, difficulty, distractor rationale, media)

#### T038 · Build the Physics item bank: 6,000 tagged items including 10 years of past Bac papers

*Task · 13 pts · High · APL Sprint 8 · labels: content, item-bank*

Content sprint: digitise and tag past Bac physics papers (all sections), author new items per KC to reach ≥ 12 items per KC with a difficulty spread, and translate. Includes a quality rubric and double-tagging on a 10% sample to measure inter-rater agreement.

Acceptance criteria:

- ≥ 6,000 published items; no KC has fewer than 8 items
- Inter-rater KC tagging agreement (Cohen's κ) ≥ 0.75 on the sample
- All past-exam items carry year + section provenance

Blocked by: T037 (As a teacher-author, I create, preview and submit items for review in the authoring tool), T035 (Populate the Physics KC graph for all Bac tracks (first subject))

#### T039 · Ingest official textbooks into the RAG corpus with chapter/KC-aware chunking

*Task · 8 pts · High · APL Sprint 6 · labels: rag, ocr, pgvector*

OCR + layout extraction of the official physics manuals (Arabic and French editions), equation preservation (MathPix or Nougat), chunking by section with KC tags, embeddings (multilingual model) into pgvector with metadata filters. Licensing confirmed with CNP.

Acceptance criteria:

- Equations survive extraction as LaTeX and render in the tutor
- Each chunk carries KC tags, chapter, page, language
- Retrieval precision@5 ≥ 0.85 on a 200-question evaluation set built by curriculum team

Blocked by: T035 (Populate the Physics KC graph for all Bac tracks (first subject))

#### T044 · Run pilot item calibration and prune bad items

*Task · 8 pts · Medium · APL Sprint 11 · labels: irt, calibration*

Expose the item bank to a pilot cohort (≈ 2,000 students) in fixed sequence; fit IRT 2PL/3PL per item; flag items with negative discrimination, extreme difficulty, or distractor dominance; return to authors.

Acceptance criteria:

- IRT parameters stored on every item with ≥ 200 responses
- Items with discrimination < 0.3 are unpublished pending review
- Calibration report shared with curriculum team

Blocked by: T038 (Build the Physics item bank: 6,000 tagged items including 10 years of past Bac papers), T043 (Implement IRT cold-start estimator and blended handoff to SAINT+)


### E05 — Deep Knowledge Tracing Core

**Phase:** Phase 2 · **Priority:** Highest · **Component:** ML · **10 tickets / 84 pts**

**Goal.** Self-hosted SAINT+ model (pyKT) predicting per-concept failure probability, with IRT cold-start fallback, weekly automated retraining and sub-50 ms online inference.

**Definition of done.** AUC ≥ 0.80 on held-out Tunisian cohort data; p99 inference latency ≤ 50 ms at 2,000 RPS; weekly retrain runs unattended with automatic rollback on metric regression.

| ID | Type | Summary | Pts | Priority | Sprint | Blocked by |
|---|---|---|---|---|---|---|
| T040 | Spike | Benchmark SAINT, SAINT+, SAKT and AKT on public datasets and our pilot data | 8 | Highest | S6 | T028 |
| T041 | Task | Integrate pyKT into the ML mono-repo with our data adapter and reproducible training config | 8 | Highest | S6 | T040 |
| T042 | Task | Implement production SAINT+ model with elapsed-time and lag-time embeddings | 13 | Highest | S7 | T041 |
| T043 | Task | Implement IRT cold-start estimator and blended handoff to SAINT+ | 8 | Highest | S7 | T041 |
| T045 | Task | Deploy Kubeflow Pipelines on EKS and the weekly retraining DAG (Sunday 02:00 Africa/Tunis) | 13 | Highest | S8 | T042, T003 |
| T046 | Task | Deploy TorchServe inference service with batching, warm pools and model versioning | 8 | Highest | S8 | T042 |
| T047 | Task | Build champion/challenger evaluation gate and automatic rollback on metric regression | 8 | Highest | S9 | T045, T046 |
| T048 | Task | Build the online sequence builder: assemble a student's recent interaction window for inference | 8 | Highest | S8 | T026, T030 |
| T049 | Task | Expose per-KC mastery estimates and attention-based explanations via an internal API | 5 | High | S10 | T046, T048 |
| T050 | Task | Implement model monitoring: prediction drift, input drift and data-leak tests | 5 | High | S10 | T047 |

#### T040 · Benchmark SAINT, SAINT+, SAKT and AKT on public datasets and our pilot data

*Spike · 8 pts · Highest · APL Sprint 6 · labels: spike, pykt, research*

Time-boxed (1 sprint) evaluation using pyKT: train SAKT, SAINT, SAINT+ and AKT on ASSIST2009/2017, EdNet subset, and the first pilot sequences. Compare AUC, calibration (ECE), inference cost and sequence-length sensitivity. Decide the production architecture and write the ADR.

Acceptance criteria:

- ADR published with chosen model, rationale and fallback
- Reproducible benchmark notebook in `ml/benchmarks/`
- Inference latency per model measured on CPU and GPU

Blocked by: T028 (Model the learning-analytics warehouse in dbt (staging → marts) with tests)

#### T041 · Integrate pyKT into the ML mono-repo with our data adapter and reproducible training config

*Task · 8 pts · Highest · APL Sprint 6 · labels: pykt, mlflow*

Vendor pyKT as a pinned dependency; write the Snowflake → pyKT sequence adapter (`ml_training_sequences` → question/KC/response/elapsed-time tensors); Hydra configs; MLflow experiment tracking; deterministic seeds; unit tests on the adapter.

Acceptance criteria:

- `make train MODEL=saint_plus` runs end-to-end on a 10k-sequence sample in CI (CPU)
- Every run logs params, metrics, data snapshot hash and model artifact to MLflow
- Adapter handles multi-KC items and interactive-item partial credit

Blocked by: T040 (Benchmark SAINT, SAINT+, SAKT and AKT on public datasets and our pilot data)

#### T042 · Implement production SAINT+ model with elapsed-time and lag-time embeddings

*Task · 13 pts · Highest · APL Sprint 7 · labels: saint, transformer, pytorch*

SAINT+ encoder–decoder: encoder over exercise sequence (item + KC embeddings + position), decoder over response sequence (correctness, elapsed time bucket, lag time bucket, hint usage, confidence). Separated self-attention per the SAINT architecture; causal masking; max sequence 512 with sliding window; mixed-precision training.

Acceptance criteria:

- AUC ≥ 0.80 and ECE ≤ 0.05 on held-out pilot cohort
- Training on 50M interactions completes < 4 h on 4×A10G
- Model card documents data, metrics, known biases

Blocked by: T041 (Integrate pyKT into the ML mono-repo with our data adapter and reproducible training config)

#### T043 · Implement IRT cold-start estimator and blended handoff to SAINT+

*Task · 8 pts · Highest · APL Sprint 7 · labels: irt, cold-start*

For students with < 20 interactions: Bayesian 2PL IRT ability estimate per chapter using item priors; blend weight ramps from IRT to SAINT+ as sequence length grows (configurable schedule). Placement mini-test (12 items, adaptive) at onboarding.

Acceptance criteria:

- New student receives a routed item after a 12-item placement with ability CI < 0.5 logits
- Blend schedule configurable without redeploy
- Offline eval shows blended model beats either alone on sequences < 50

Blocked by: T041 (Integrate pyKT into the ML mono-repo with our data adapter and reproducible training config)

#### T045 · Deploy Kubeflow Pipelines on EKS and the weekly retraining DAG (Sunday 02:00 Africa/Tunis)

*Task · 13 pts · Highest · APL Sprint 8 · labels: kubeflow, retraining, mlops*

Kubeflow Pipelines (or Argo Workflows + KFP SDK) in the `ml` namespace with GPU node affinity. Pipeline: snapshot Snowflake mart → validate data → train SAINT+ → evaluate vs. champion → register in MLflow → (if better) package for TorchServe → canary deploy. Triggered by cron Sunday 02:00 Africa/Tunis; Airflow owns the data snapshot step.

Acceptance criteria:

- Pipeline runs unattended end-to-end in staging for 3 consecutive weeks
- GPU nodes scale from 0 at 01:55 and back to 0 after completion
- Pipeline failure pages ML on-call with the failing step and logs

Blocked by: T042 (Implement production SAINT+ model with elapsed-time and lag-time embeddings), T003 (Deploy AWS EKS cluster with managed node groups, Karpenter and GPU node pool)

#### T046 · Deploy TorchServe inference service with batching, warm pools and model versioning

*Task · 8 pts · Highest · APL Sprint 8 · labels: torchserve, inference*

TorchServe on the GPU pool (plus a CPU fallback deployment) serving SAINT+ via gRPC; dynamic batching (max batch 64, 5 ms wait); model store on S3; blue/green model version swap via management API; Datadog metrics for latency, batch size, GPU utilisation.

Acceptance criteria:

- p99 latency ≤ 50 ms at 2,000 RPS with sequence length 256
- Model version swap causes zero failed requests
- CPU fallback keeps p99 ≤ 150 ms if GPU pool is unavailable

Blocked by: T042 (Implement production SAINT+ model with elapsed-time and lag-time embeddings)

#### T047 · Build champion/challenger evaluation gate and automatic rollback on metric regression

*Task · 8 pts · Highest · APL Sprint 9 · labels: mlops, evaluation, fairness*

Evaluation step compares challenger vs. champion on the last 2 weeks of held-out data (AUC, ECE, per-section AUC, fairness slices by region/gender/school type). Promotion only if no slice regresses > 1 pt AUC. Post-deploy online monitor compares predicted vs. observed accuracy; auto-rollback if calibration drifts.

Acceptance criteria:

- A deliberately degraded challenger is rejected by the gate
- Online calibration drift alert triggers rollback to previous TorchServe version within 10 minutes
- Fairness slice report attached to every promotion

Blocked by: T045 (Deploy Kubeflow Pipelines on EKS and the weekly retraining DAG (Sunday 02:00 Africa/Tunis)), T046 (Deploy TorchServe inference service with batching, warm pools and model versioning)

#### T048 · Build the online sequence builder: assemble a student's recent interaction window for inference

*Task · 8 pts · Highest · APL Sprint 8 · labels: redis, inference*

Service that maintains per-student rolling interaction windows in Redis (last 512 events, compact encoding), updated from Kafka in real time, and serves the tensor-ready sequence to TorchServe in one call.

Acceptance criteria:

- Sequence is fresh within 300 ms of the latest answer (p95)
- Memory footprint ≤ 8 KB per active student
- Cold student (no Redis state) rebuilds from Snowflake in < 2 s

Blocked by: T026 (Deploy Redis Cluster (ElastiCache) and the real-time aggregation consumer), T030 (Stand up the online/offline feature store for student state)

#### T049 · Expose per-KC mastery estimates and attention-based explanations via an internal API

*Task · 5 pts · High · APL Sprint 10 · labels: api, explainability*

`/ml/v1/mastery/{student}` returns per-KC probability + confidence and the top-3 past interactions (by attention weight) that drove the estimate, for teacher dashboards and tutor context.

Acceptance criteria:

- Response includes KC, p(correct), confidence interval, last-updated
- Explanation references real item IDs and timestamps
- p99 < 80 ms including TorchServe call

Blocked by: T046 (Deploy TorchServe inference service with batching, warm pools and model versioning), T048 (Build the online sequence builder: assemble a student's recent interaction window for inference)

#### T050 · Implement model monitoring: prediction drift, input drift and data-leak tests

*Task · 5 pts · High · APL Sprint 10 · labels: monitoring, drift*

Evidently-based drift jobs on prediction distributions and input features; test that forbids training on data after the evaluation cut-off; alert on sequence-length distribution shift (e.g., new client release).

Acceptance criteria:

- Drift dashboard in Datadog with weekly report
- Leak test fails CI if evaluation window overlaps training window
- Drift alert threshold tuned on 4 weeks of pilot data

Blocked by: T047 (Build champion/challenger evaluation gate and automatic rollback on metric regression)


### E06 — Adaptive Routing & Recommendation Service

**Phase:** Phase 2 · **Priority:** Highest · **Component:** ML · **8 tickets / 57 pts**

**Goal.** Per-click decision engine that turns DKT predictions + the knowledge graph into the next item, next hint level, or next concept, with spaced-repetition scheduling and exam-date awareness.

**Definition of done.** Routing decision returned in ≤ 80 ms p99 end-to-end; A/B framework shows measurable learning-gain lift vs. fixed-sequence control.

| ID | Type | Summary | Pts | Priority | Sprint | Blocked by |
|---|---|---|---|---|---|---|
| T051 | Spike | Design the routing policy: mastery thresholds, exploration, spaced repetition and exam-date weighting | 5 | Highest | S7 | T040, T035 |
| T052 | Task | Build the routing microservice (Node.js) with cached graph, TorchServe client and policy engine | 13 | Highest | S9 | T051, T046, T048 |
| T053 | Story | As a student stuck on a concept, I am routed to a prerequisite-level remediation path instead of harder items | 8 | High | S10 | T052 |
| T054 | Task | Implement spaced-repetition scheduler with exam-date compression | 8 | High | S11 | T052 |
| T055 | Task | Build the experimentation framework: assignment, exposure logging, learning-gain metrics | 8 | High | S11 | T052, T028 |
| T056 | Task | Add pre-computation of next-item candidates to hide inference latency behind the UI | 5 | Medium | S10 | T052 |
| T057 | Story | As a student in a track with several subjects, I get a daily plan that splits time across subjects by exam weight and weakness | 5 | Medium | S12 | T052 |
| T058 | Story | As a teacher, I can pin a chapter or assign a set for my class and the router respects it | 5 | Medium | S13 | T052 |

#### T051 · Design the routing policy: mastery thresholds, exploration, spaced repetition and exam-date weighting

*Spike · 5 pts · Highest · APL Sprint 7 · labels: spike, routing*

Decide the decision function combining SAINT+ p(correct) per KC, knowledge-graph prerequisites, item exposure control, spaced-repetition intervals (FSRS-style), exam-weight of KCs and days-to-exam. Produce a design doc with offline simulation on pilot data.

Acceptance criteria:

- Design doc approved by ML lead and pedagogy lead
- Simulator shows routing policy reaches mastery on a synthetic student faster than fixed sequence
- Guardrails defined: max difficulty jump, max consecutive failures before remediation

Blocked by: T040 (Benchmark SAINT, SAINT+, SAKT and AKT on public datasets and our pilot data), T035 (Populate the Physics KC graph for all Bac tracks (first subject))

#### T052 · Build the routing microservice (Node.js) with cached graph, TorchServe client and policy engine

*Task · 13 pts · Highest · APL Sprint 9 · labels: routing, microservice*

`routing-svc`: loads published KC graph into memory, calls sequence builder + TorchServe, applies the policy, selects the next item from the bank with exposure balancing, emits `routing.decision` event with full rationale. Feature-flagged policies.

Acceptance criteria:

- p99 end-to-end routing decision ≤ 80 ms
- Decision event records inputs, candidate set and chosen item for audit and offline replay
- Policy can be switched per tenant via flag

Blocked by: T051 (Design the routing policy: mastery thresholds, exploration, spaced repetition and exam-date weighting), T046 (Deploy TorchServe inference service with batching, warm pools and model versioning), T048 (Build the online sequence builder: assemble a student's recent interaction window for inference)

#### T053 · As a student stuck on a concept, I am routed to a prerequisite-level remediation path instead of harder items

*Story · 8 pts · High · APL Sprint 10 · labels: routing, remediation*

When p(correct) on a KC stays < 0.4 after N attempts, the router walks the prerequisite edges to find the weakest ancestor KC and inserts a short remediation sequence (worked example → easy item → original KC).

Acceptance criteria:

- Simulated struggling student receives remediation within 3 failures
- Remediation never loops more than 2 levels deep
- Student sees an explanation of why they were redirected (in Arabic/French)

Blocked by: T052 (Build the routing microservice (Node.js) with cached graph, TorchServe client and policy engine)

#### T054 · Implement spaced-repetition scheduler with exam-date compression

*Task · 8 pts · High · APL Sprint 11 · labels: spaced-repetition*

FSRS-style memory model per KC; review intervals compressed as the Bac date approaches; daily review queue computed in a batch job and merged into the router's candidate set.

Acceptance criteria:

- Review queue updates nightly for 100k students in < 30 minutes
- Intervals shorten monotonically as days-to-exam decreases
- Reviews account for ≤ 30% of a session by default (configurable)

Blocked by: T052 (Build the routing microservice (Node.js) with cached graph, TorchServe client and policy engine)

#### T055 · Build the experimentation framework: assignment, exposure logging, learning-gain metrics

*Task · 8 pts · High · APL Sprint 11 · labels: experimentation, ab-testing*

Deterministic bucketing by student hash; experiment config in LaunchDarkly/Unleash; exposure events to Kafka; metrics pipeline in dbt for learning gain (pre/post mastery delta), time-to-mastery, retention; guardrail metrics for frustration (abandon rate).

Acceptance criteria:

- First A/B (policy v1 vs. fixed sequence) launches to 10% of pilot
- Sequential testing dashboard shows p-values and guardrail status
- Experiment can be killed from the flag UI in < 1 minute

Blocked by: T052 (Build the routing microservice (Node.js) with cached graph, TorchServe client and policy engine), T028 (Model the learning-analytics warehouse in dbt (staging → marts) with tests)

#### T056 · Add pre-computation of next-item candidates to hide inference latency behind the UI

*Task · 5 pts · Medium · APL Sprint 10 · labels: performance, routing*

While the student works on item N, pre-compute top-3 candidates for N+1 under each outcome (correct/incorrect) and push to the client; on answer, the client renders instantly and the router confirms asynchronously.

Acceptance criteria:

- Perceived time between answer and next item < 100 ms on 3G
- Confirmation mismatch rate < 2% (logged)
- Pre-computation disabled automatically under TorchServe overload

Blocked by: T052 (Build the routing microservice (Node.js) with cached graph, TorchServe client and policy engine)

#### T057 · As a student in a track with several subjects, I get a daily plan that splits time across subjects by exam weight and weakness

*Story · 5 pts · Medium · APL Sprint 12 · labels: routing, multi-subject*

Cross-subject planner: allocates session time across the student's enrolled subjects using per-subject mastery gaps, Bac coefficients for the track, and days-to-exam; each subject's router then fills its slot. Student can override the split.

Acceptance criteria:

- Default split follows Bac coefficients unless mastery gaps justify a shift (documented rule)
- Planner decision event logged with rationale
- Override persists and is respected by the router

Blocked by: T052 (Build the routing microservice (Node.js) with cached graph, TorchServe client and policy engine)

#### T058 · As a teacher, I can pin a chapter or assign a set for my class and the router respects it

*Story · 5 pts · Medium · APL Sprint 13 · labels: routing, teacher*

Teacher assignments become hard constraints on the candidate set for the assignment window; the router still chooses order and difficulty within the constraint.

Acceptance criteria:

- Assigned items appear first in the student's queue until completed
- Router explains the constraint in the decision event
- Teacher sees completion status per student

Blocked by: T052 (Build the routing microservice (Node.js) with cached graph, TorchServe client and policy engine)


### E07 — Multi-Model LLM Gateway & Guardrails

**Phase:** Phase 2 · **Priority:** Highest · **Component:** LLM · **10 tickets / 77 pts**

**Goal.** LiteLLM proxy fronting OpenAI / Anthropic / local models with semantic caching, curriculum-grounded RAG over pgvector, and an LLM-as-a-Judge harness with pluggable per-subject verifiers (symbolic for maths/physics/technique, rubric-based for éco/gestion) that blocks hallucinated content before it reaches a student.

**Definition of done.** Judge blocks ≥ 95% of seeded formula hallucinations with ≤ 3% false-block rate; semantic cache hit rate ≥ 35%; per-student daily LLM cost capped and enforced.

| ID | Type | Summary | Pts | Priority | Sprint | Blocked by |
|---|---|---|---|---|---|---|
| T059 | Task | Deploy LiteLLM proxy with provider routing, fallbacks, budgets and key management | 8 | Highest | S6 | T003, T016 |
| T060 | Task | Serve a local open-weights model on vLLM for the judge and low-cost paths | 8 | High | S7 | T003 |
| T061 | Task | Build the curriculum RAG pipeline over pgvector with KC-filtered hybrid retrieval | 8 | Highest | S7 | T039, T059 |
| T062 | Task | Implement the LLM-as-a-Judge harness that intercepts tutor output before delivery | 13 | Highest | S8 | T060, T061 |
| T063 | Task | Refactor the judge into a verifier plug-in interface with symbolic and rubric implementations | 8 | High | S10 | T062 |
| T064 | Task | Build the semantic cache in Redis for tutor and explanation queries | 8 | High | S9 | T062 |
| T065 | Task | Create the prompt registry with versioning, evals and staged rollout | 5 | High | S9 | T062 |
| T066 | Task | Harden the tutor against prompt injection, jailbreaks and data exfiltration | 8 | High | S10 | T062 |
| T067 | Task | Build the LLM cost dashboard and automated cost-control policies | 3 | Medium | S11 | T059 |
| T068 | Task | Curate the golden evaluation dataset for tutor quality with curriculum team | 8 | High | S8 | T038 |

#### T059 · Deploy LiteLLM proxy with provider routing, fallbacks, budgets and key management

*Task · 8 pts · Highest · APL Sprint 6 · labels: litellm, llm-gateway*

LiteLLM in the `llm` namespace fronting OpenAI, Anthropic and a local vLLM endpoint (Qwen/Llama class on the GPU pool); routing rules by task (tutor → frontier model, judge → local, summarise → cheap); automatic fallback on 5xx/timeout; per-tenant and per-student daily budgets; virtual keys per service.

Acceptance criteria:

- Provider outage simulated → traffic fails over within 2 s with no student-visible error
- A student exceeding their daily budget gets a graceful 'come back tomorrow' message
- All LLM calls traced in Datadog with model, tokens, cost, latency

Blocked by: T003 (Deploy AWS EKS cluster with managed node groups, Karpenter and GPU node pool), T016 (Centralise secrets in AWS Secrets Manager with automatic rotation)

#### T060 · Serve a local open-weights model on vLLM for the judge and low-cost paths

*Task · 8 pts · High · APL Sprint 7 · labels: vllm, local-llm*

vLLM deployment on g5 nodes with tensor parallel as needed, quantised weights, continuous batching, prometheus metrics; autoscaled on queue depth; used for LLM-as-a-Judge, classification and semantic-cache embedding.

Acceptance criteria:

- Judge call p99 < 400 ms at 200 concurrent requests
- Pod scales to zero overnight and warms in < 3 minutes on first request
- Model weights pulled from S3, not the public hub, at runtime

Blocked by: T003 (Deploy AWS EKS cluster with managed node groups, Karpenter and GPU node pool)

#### T061 · Build the curriculum RAG pipeline over pgvector with KC-filtered hybrid retrieval

*Task · 8 pts · Highest · APL Sprint 7 · labels: rag, pgvector*

pgvector (HNSW) + BM25 hybrid retrieval, filtered by KC tags from the current item and student language; reranking with a small cross-encoder; prompt assembly with citations (chapter + page); retrieval evaluation harness with the 200-question set.

Acceptance criteria:

- Precision@5 ≥ 0.85 on the evaluation set
- Every tutor message that states a formula carries a textbook citation
- Retrieval p99 < 120 ms

Blocked by: T039 (Ingest official textbooks into the RAG corpus with chapter/KC-aware chunking), T059 (Deploy LiteLLM proxy with provider routing, fallbacks, budgets and key management)

#### T062 · Implement the LLM-as-a-Judge harness that intercepts tutor output before delivery

*Task · 13 pts · Highest · APL Sprint 8 · labels: guardrails, llm-judge, langsmith*

Synchronous judge in the tutor path: (1) extract formulas/claims from the candidate hint, (2) verify against retrieved textbook chunks and a symbolic checker (SymPy) for dimensional analysis and algebraic equivalence, (3) local LLM judge scores correctness, curriculum alignment, and 'does not reveal the answer'. Block + regenerate on fail (max 2 retries), then fall back to a template hint. LangSmith/Phoenix traces for every decision.

Acceptance criteria:

- Seeded hallucination suite (300 cases) blocked ≥ 95%, false-block ≤ 3%
- Judge adds ≤ 500 ms p95 to tutor latency
- Every block is logged with reason and surfaced in the eval dashboard

Blocked by: T060 (Serve a local open-weights model on vLLM for the judge and low-cost paths), T061 (Build the curriculum RAG pipeline over pgvector with KC-filtered hybrid retrieval)

#### T063 · Refactor the judge into a verifier plug-in interface with symbolic and rubric implementations

*Task · 8 pts · High · APL Sprint 10 · labels: guardrails, multi-subject*

Define a `Verifier` interface (input: candidate message + retrieved chunks + item metadata; output: pass/fail + reasons). Implementations: `SymbolicVerifier` (SymPy algebra, units, numeric tolerance) for physics/maths/technique, and `RubricVerifier` (local LLM scoring against curriculum rubric + fact check vs. textbook) for éco/gestion and descriptive sciences content. Verifier selected by `subject_id`; results logged per verifier.

Acceptance criteria:

- Both verifiers pass their own seeded test suites (≥ 95% catch, ≤ 3% false block)
- Adding a verifier requires no change to the tutor path
- Per-verifier latency and block rate visible in the eval dashboard

Blocked by: T062 (Implement the LLM-as-a-Judge harness that intercepts tutor output before delivery)

#### T064 · Build the semantic cache in Redis for tutor and explanation queries

*Task · 8 pts · High · APL Sprint 9 · labels: semantic-cache, redis*

Embed (local model) the normalised student question + item context; cosine search in Redis (RediSearch vector) with threshold; cache judged-approved responses only; invalidate on item or textbook version change; per-language namespaces.

Acceptance criteria:

- Cache hit rate ≥ 35% after 2 weeks of pilot traffic
- Hit returns in < 30 ms and bypasses both LLM and judge
- A response blocked by the judge is never cached

Blocked by: T062 (Implement the LLM-as-a-Judge harness that intercepts tutor output before delivery)

#### T065 · Create the prompt registry with versioning, evals and staged rollout

*Task · 5 pts · High · APL Sprint 9 · labels: prompts, evals*

Prompts stored as versioned files with metadata, loaded by the gateway; each change runs the offline eval suite (judge pass rate, Socratic-ness score, language quality) in CI; staged rollout 5% → 100% with flag.

Acceptance criteria:

- No prompt reaches prod without a passing eval run linked in the PR
- Rollback to previous prompt version is a flag flip
- Prompt diff visible in the LangSmith trace

Blocked by: T062 (Implement the LLM-as-a-Judge harness that intercepts tutor output before delivery)

#### T066 · Harden the tutor against prompt injection, jailbreaks and data exfiltration

*Task · 8 pts · High · APL Sprint 10 · labels: security, prompt-injection*

Input classifier (local model) for injection patterns, strict separation of system/retrieved/user content, output filter for secrets and other-student data, red-team suite of 500 attacks run nightly, rate limiting on repeated refusals.

Acceptance criteria:

- Red-team suite pass rate ≥ 98% with no exfiltration of system prompt or PII
- Attack attempts are logged and counted per student for abuse review
- New attack classes added within one sprint of discovery

Blocked by: T062 (Implement the LLM-as-a-Judge harness that intercepts tutor output before delivery)

#### T067 · Build the LLM cost dashboard and automated cost-control policies

*Task · 3 pts · Medium · APL Sprint 11 · labels: finops, llm*

Datadog + Snowflake cost model per tenant/student/feature; policies: downgrade model tier when daily spend > forecast, enforce cache-first, cap tokens; weekly cost review report.

Acceptance criteria:

- Cost per active student per day visible within 1 h latency
- Automatic tier downgrade triggers in staging when budget exceeded
- Finance receives weekly report automatically

Blocked by: T059 (Deploy LiteLLM proxy with provider routing, fallbacks, budgets and key management)

#### T068 · Curate the golden evaluation dataset for tutor quality with curriculum team

*Task · 8 pts · High · APL Sprint 8 · labels: evals, dataset*

1,000 (item, student state, expected hint level, forbidden content) cases across all chapters and both languages, labelled by teachers; used by prompt CI and judge calibration; refreshed quarterly.

Acceptance criteria:

- Dataset covers every chapter with ≥ 30 cases
- Inter-annotator agreement ≥ 0.8 on 'reveals answer' label
- Stored in versioned storage with a datasheet

Blocked by: T038 (Build the Physics item bank: 6,000 tagged items including 10 years of past Bac papers)


### E08 — Socratic AI Tutor Experience

**Phase:** Phase 3 · **Priority:** High · **Component:** Frontend · **7 tickets / 42 pts**

**Goal.** A streaming, bilingual (Arabic / French) Socratic tutor that asks before it tells, escalates hints in levels, cites the official textbook, and never gives the full answer on first ask.

**Definition of done.** ≥ 70% of tutor sessions end with the student answering correctly without the final answer being revealed; CSAT ≥ 4.2/5 in pilot.

| ID | Type | Summary | Pts | Priority | Sprint | Blocked by |
|---|---|---|---|---|---|---|
| T069 | Story | As a student, I chat with a streaming tutor beside the item, in Arabic or French, with LaTeX rendering | 8 | High | S9 | T059 |
| T070 | Story | As a student, hints escalate in levels (question → nudge → worked step → solution) and never start at the answer | 8 | High | S9 | T062, T069 |
| T071 | Task | Build misconception diagnosis from distractor choice and interaction trace | 8 | Medium | S11 | T070, T036 |
| T072 | Story | As a student, I rate a hint and report a wrong explanation in one tap | 3 | Medium | S10 | T064 |
| T073 | Story | As a student on mobile, I can dictate my question in Tunisian Arabic or French | 5 | Low | S14 | T069, T060 |
| T074 | Task | Bilingual content strategy: translation memory, glossary enforcement and QA for tutor output | 5 | High | S10 | T065 |
| T075 | Story | As a parent, I receive a weekly plain-language summary of what my child worked on and where they struggle | 5 | Medium | S13 | T049, T059 |

#### T069 · As a student, I chat with a streaming tutor beside the item, in Arabic or French, with LaTeX rendering

*Story · 8 pts · High · APL Sprint 9 · labels: tutor, frontend, streaming*

Tutor panel in the learning view: SSE streaming via the gateway, KaTeX rendering, RTL support, code-less equation input via a math keypad, message history per item, 'I'm still stuck' escalation button.

Acceptance criteria:

- First token visible < 1.2 s p75 on 3G
- Arabic messages render RTL with correctly embedded LTR equations
- Tutor conversation persists across reloads

Blocked by: T059 (Deploy LiteLLM proxy with provider routing, fallbacks, budgets and key management)

#### T070 · As a student, hints escalate in levels (question → nudge → worked step → solution) and never start at the answer

*Story · 8 pts · High · APL Sprint 9 · labels: tutor, pedagogy*

Hint policy service: level 1 Socratic question referencing the student's error (from distractor rationale), level 2 conceptual nudge with textbook citation, level 3 worked step, level 4 full solution only after ≥ 2 attempts or teacher setting. Levels logged as events for DKT features.

Acceptance criteria:

- Level 4 is unreachable on first attempt (enforced server-side)
- Each level's content passes the judge
- Hint level requested is a feature in SAINT+ training

Blocked by: T062 (Implement the LLM-as-a-Judge harness that intercepts tutor output before delivery), T069 (As a student, I chat with a streaming tutor beside the item, in Arabic or French, with LaTeX rendering)

#### T071 · Build misconception diagnosis from distractor choice and interaction trace

*Task · 8 pts · Medium · APL Sprint 11 · labels: misconceptions, tutor*

Map wrong answers and interaction patterns (e.g., sign error on vectors, unit confusion) to a misconception taxonomy curated by the curriculum team; feed the tutor prompt and teacher dashboard.

Acceptance criteria:

- ≥ 60% of wrong MCQ answers map to a named misconception
- Tutor's level-1 question references the diagnosed misconception
- Taxonomy editable in the admin tool

Blocked by: T070 (As a student, hints escalate in levels (question → nudge → worked step → solution) and never start at the answer), T036 (Define the item (question) data model: types, KC tags, difficulty, distractor rationale, media)

#### T072 · As a student, I rate a hint and report a wrong explanation in one tap

*Story · 3 pts · Medium · APL Sprint 10 · labels: feedback, tutor*

Thumbs + 'this is wrong' report; reports create a LangSmith annotation and a Jira ticket when 3 reports hit the same cached response; the response is evicted from the semantic cache immediately.

Acceptance criteria:

- Reported response is removed from cache within 1 minute
- Weekly report of top-reported items to curriculum team
- Feedback events used in prompt eval set refresh

Blocked by: T064 (Build the semantic cache in Redis for tutor and explanation queries)

#### T073 · As a student on mobile, I can dictate my question in Tunisian Arabic or French

*Story · 5 pts · Low · APL Sprint 14 · labels: voice, accessibility*

Speech-to-text via browser API with server fallback (Whisper on vLLM pool); dialect handling tested with Tunisian speakers; transcript editable before send.

Acceptance criteria:

- Word error rate ≤ 20% on a 100-utterance Tunisian Arabic test set
- Transcription < 2 s for a 10 s clip
- Feature flagged per tenant

Blocked by: T069 (As a student, I chat with a streaming tutor beside the item, in Arabic or French, with LaTeX rendering), T060 (Serve a local open-weights model on vLLM for the judge and low-cost paths)

#### T074 · Bilingual content strategy: translation memory, glossary enforcement and QA for tutor output

*Task · 5 pts · High · APL Sprint 10 · labels: i18n, arabic, french*

Physics glossary (Arabic ↔ French ↔ symbols) injected into prompts; output checker flags non-glossary terms; translation memory for templated hints; native-speaker QA pass.

Acceptance criteria:

- Glossary coverage of 100% of KC names
- Glossary violation rate < 2% on eval set
- QA sign-off from two native-speaker teachers

Blocked by: T065 (Create the prompt registry with versioning, evals and staged rollout)

#### T075 · As a parent, I receive a weekly plain-language summary of what my child worked on and where they struggle

*Story · 5 pts · Medium · APL Sprint 13 · labels: parent, summaries*

Weekly batch job generates summaries from mastery deltas via the gateway (cheap model), judged for tone and accuracy, delivered by email/SMS in the parent's language.

Acceptance criteria:

- Summary never includes raw scores that rank the child against peers
- Judge blocks any summary containing unsupported claims
- Opt-out honoured within one cycle

Blocked by: T049 (Expose per-KC mastery estimates and attention-based explanations via an internal API), T059 (Deploy LiteLLM proxy with provider routing, fallbacks, budgets and key management)


### E09 — Interactive Learning Frontend (Next.js / WebGL)

**Phase:** Phase 3 · **Priority:** Highest · **Component:** Frontend · **11 tickets / 114 pts**

**Goal.** A per-subject widget package system on React Three Fiber, with the physics package (mechanics, circuits, optics, waves) built first, an offline-first PWA that survives outages mid-assessment, and real-time peer trivia battles.

**Definition of done.** Lighthouse performance ≥ 85 on a mid-range Android device over 3G; a 20-minute assessment completes with the network cut for 5 minutes and syncs losslessly.

| ID | Type | Summary | Pts | Priority | Sprint | Blocked by |
|---|---|---|---|---|---|---|
| T076 | Task | Architect the Next.js 15 app: App Router, design system, i18n (ar/fr) with RTL, auth integration | 13 | Highest | S4 | T012 |
| T077 | Task | Build the React Three Fiber physics canvas core: scene, camera rigs, units, touch controls, performance tiers | 13 | Highest | S5 | T076 |
| T078 | Task | Build the per-subject widget package system (registry, lazy loading, parameter-space contract) | 5 | High | S6 | T077 |
| T079 | Story | As a student, I explore mechanics sandboxes: projectile motion, inclined plane, pendulum, collisions — with draggable vectors | 13 | High | S7 | T077, T024, T078 |
| T080 | Story | As a student, I build DC and RLC circuits on a canvas and watch current, voltage and resonance curves | 13 | High | S8 | T077 |
| T081 | Story | As a student, I manipulate wave and optics simulations: interference, diffraction, lenses, Doppler | 13 | High | S9 | T077 |
| T082 | Task | Build the dynamic charts and graph-reading components (Recharts/Visx) linked to simulations | 5 | Medium | S9 | T077 |
| T083 | Story | As a student, I complete an assessment during a 5-minute internet outage and nothing is lost | 13 | Highest | S11 | T076, T024, T056 |
| T084 | Story | As a student, I challenge a peer to a real-time 5-question physics battle | 13 | High | S12 | T026, T076 |
| T085 | Task | Accessibility and low-end device pass: WCAG 2.2 AA, keyboard physics controls, 2 GB RAM devices | 8 | High | S13 | T079, T080, T081 |
| T086 | Task | Enforce web performance budgets and real-user monitoring | 5 | High | S6 | T076, T007 |

#### T076 · Architect the Next.js 15 app: App Router, design system, i18n (ar/fr) with RTL, auth integration

*Task · 13 pts · Highest · APL Sprint 4 · labels: nextjs, design-system, i18n*

Monorepo (Turborepo) with `apps/web`, `packages/ui`, `packages/telemetry`, `packages/physics`. Server components for shells, client islands for widgets; next-intl with RTL layout switching; Keycloak PKCE flow; Storybook for the design system; bundle budget enforced in CI.

Acceptance criteria:

- Initial JS ≤ 180 KB gz on the learning route
- Switching ar ↔ fr flips layout direction with no layout shift
- Storybook deployed per PR

Blocked by: T012 (Deploy Keycloak identity provider with student / parent / teacher / school-admin realms)

#### T077 · Build the React Three Fiber physics canvas core: scene, camera rigs, units, touch controls, performance tiers

*Task · 13 pts · Highest · APL Sprint 5 · labels: react-three-fiber, webgl, rapier*

`@apl/physics` package: shared scene wrapper, SI unit helpers, deterministic fixed-step integrator (Rapier WASM for rigid bodies), touch/pointer gesture layer, three performance tiers detected from GPU benchmark (shadows/particles toggled), WebGL context-loss recovery.

Acceptance criteria:

- 60 fps on a mid-range Android (e.g., Snapdragon 6-series) at tier 2
- Context loss recovers without losing the student's state
- Simulation is deterministic given the same seed and inputs (replayable)

Blocked by: T076 (Architect the Next.js 15 app: App Router, design system, i18n (ar/fr) with RTL, auth integration)

#### T078 · Build the per-subject widget package system (registry, lazy loading, parameter-space contract)

*Task · 5 pts · High · APL Sprint 6 · labels: widgets, multi-subject*

`@apl/widgets-<subject>` packages registered at runtime; each widget declares its parameter space, scoring hook and telemetry events; items reference widgets by id + version; packages are lazy-loaded per subject so a maths student never downloads physics sims.

Acceptance criteria:

- A new widget package can be added without touching the app shell
- Loading the learning route for a maths-only student downloads no physics code (bundle analysis)
- Widget version pinning: an item keeps rendering with the version it was authored against

Blocked by: T077 (Build the React Three Fiber physics canvas core: scene, camera rigs, units, touch controls, performance tiers)

#### T079 · As a student, I explore mechanics sandboxes: projectile motion, inclined plane, pendulum, collisions — with draggable vectors

*Story · 13 pts · High · APL Sprint 7 · labels: widgets, mechanics*

Four interactive widgets with parameter sliders, draggable force/velocity vectors, live graphs (x-t, v-t), and 'predict then play' prompts. Each widget exposes a parameter space for randomised items.

Acceptance criteria:

- Each widget passes the curriculum team's physics-accuracy review
- Slider and drag events flow to telemetry with hesitation metrics
- Widget loads < 1.5 s on 3G (lazy-loaded chunk)

Blocked by: T077 (Build the React Three Fiber physics canvas core: scene, camera rigs, units, touch controls, performance tiers), T024 (Build the Next.js telemetry SDK: batching, offline buffering, hesitation and time-to-first-click), T078 (Build the per-subject widget package system (registry, lazy loading, parameter-space contract))

#### T080 · As a student, I build DC and RLC circuits on a canvas and watch current, voltage and resonance curves

*Story · 13 pts · High · APL Sprint 8 · labels: widgets, electricity*

Circuit builder: drag components (R, L, C, source, switch, voltmeter, ammeter), snap-to-grid wiring, modified nodal analysis solver (DC + AC phasor + transient RC/RL), oscilloscope view for RLC resonance.

Acceptance criteria:

- Solver matches SPICE reference on 30 test circuits within 1%
- Transient RC charging curve animates in real time
- Student can save and share a circuit

Blocked by: T077 (Build the React Three Fiber physics canvas core: scene, camera rigs, units, touch controls, performance tiers)

#### T081 · As a student, I manipulate wave and optics simulations: interference, diffraction, lenses, Doppler

*Story · 13 pts · High · APL Sprint 9 · labels: widgets, optics, waves*

GPU shader-based wave field (GLSL) for interference/diffraction; ray-tracing lens bench; Doppler audio+visual; parameters linked to items.

Acceptance criteria:

- Shader runs at tier 1 on integrated GPUs with reduced resolution
- Lens bench ray diagram matches thin-lens formula within 1%
- Accessibility: all sims have a reduced-motion mode

Blocked by: T077 (Build the React Three Fiber physics canvas core: scene, camera rigs, units, touch controls, performance tiers)

#### T082 · Build the dynamic charts and graph-reading components (Recharts/Visx) linked to simulations

*Task · 5 pts · Medium · APL Sprint 9 · labels: charts*

Reusable chart components with live binding to sim state, graph-reading items (click the slope, shade the area), export to PNG for teacher reports.

Acceptance criteria:

- Charts update at ≥ 30 fps while a slider is dragged
- Graph-reading item scoring tolerant to touch imprecision
- RTL axis labels render correctly in Arabic

Blocked by: T077 (Build the React Three Fiber physics canvas core: scene, camera rigs, units, touch controls, performance tiers)

#### T083 · As a student, I complete an assessment during a 5-minute internet outage and nothing is lost

*Story · 13 pts · Highest · APL Sprint 11 · labels: pwa, offline, workbox*

Offline-first PWA: Workbox service worker precaches the shell and the current assignment's items/widgets; answers and telemetry queued in IndexedDB; background sync on reconnect with conflict rules (server-authoritative timestamps); UI shows offline state.

Acceptance criteria:

- Cut network for 5 minutes mid-assessment → 100% of answers and events sync on reconnect
- Pre-fetch of the next 10 routed items happens on Wi-Fi only (configurable)
- Service worker update does not interrupt an active session

Blocked by: T076 (Architect the Next.js 15 app: App Router, design system, i18n (ar/fr) with RTL, auth integration), T024 (Build the Next.js telemetry SDK: batching, offline buffering, hesitation and time-to-first-click), T056 (Add pre-computation of next-item candidates to hide inference latency behind the UI)

#### T084 · As a student, I challenge a peer to a real-time 5-question physics battle

*Story · 13 pts · High · APL Sprint 12 · labels: websockets, battles, realtime*

WebSocket service (Node.js + Socket.IO on Redis adapter) for matchmaking by mastery band, synchronised question reveal, 15 s timers with server-authoritative scoring, anti-cheat (answer hash submitted before reveal), spectator mode for class battles.

Acceptance criteria:

- Two clients on 3G see question reveal within 300 ms of each other
- A disconnect/reconnect within 10 s resumes the battle
- Load test: 5,000 concurrent battles on 4 pods

Blocked by: T026 (Deploy Redis Cluster (ElastiCache) and the real-time aggregation consumer), T076 (Architect the Next.js 15 app: App Router, design system, i18n (ar/fr) with RTL, auth integration)

#### T085 · Accessibility and low-end device pass: WCAG 2.2 AA, keyboard physics controls, 2 GB RAM devices

*Task · 8 pts · High · APL Sprint 13 · labels: accessibility, performance*

Axe CI gate, keyboard-operable sliders and drags, screen-reader descriptions of sim state, high-contrast theme, memory budget tests on 2 GB devices, data-saver mode.

Acceptance criteria:

- Zero Axe critical violations on all routes
- All widgets operable by keyboard alone
- App remains responsive on a 2 GB RAM Android emulator with 3 widgets loaded

Blocked by: T079 (As a student, I explore mechanics sandboxes: projectile motion, inclined plane, pendulum, collisions — with draggable vectors), T080 (As a student, I build DC and RLC circuits on a canvas and watch current, voltage and resonance curves), T081 (As a student, I manipulate wave and optics simulations: interference, diffraction, lenses, Doppler)

#### T086 · Enforce web performance budgets and real-user monitoring

*Task · 5 pts · High · APL Sprint 6 · labels: performance, rum*

Lighthouse CI per PR with budgets; Datadog RUM with Core Web Vitals by device class and region (Tunis vs. interior governorates); error tracking with source maps.

Acceptance criteria:

- PR fails if LCP budget on learning route exceeds 2.5 s (throttled)
- RUM dashboard segments by governorate and connection type
- Source-mapped stack traces for 100% of prod JS errors

Blocked by: T076 (Architect the Next.js 15 app: App Router, design system, i18n (ar/fr) with RTL, auth integration), T007 (Roll out Datadog APM, distributed tracing, log pipeline and memory-leak watchdogs)


### E10 — Learner Engagement & Gamification

**Phase:** Phase 3 · **Priority:** Medium · **Component:** Backend · **5 tickets / 26 pts**

**Goal.** Streaks, XP, leaderboards and smart nudges computed in real time from the Kafka stream via Redis, tuned for exam-season motivation rather than vanity metrics.

**Definition of done.** Day-7 retention ≥ 40% in pilot; leaderboard reads p99 < 20 ms.

| ID | Type | Summary | Pts | Priority | Sprint | Blocked by |
|---|---|---|---|---|---|---|
| T087 | Story | As a student, I see my streak, XP and daily goal update instantly after each answer | 5 | Medium | S10 | T026 |
| T088 | Story | As a student, I see class and national leaderboards that reward mastery gain, not volume | 5 | Medium | S11 | T026, T049 |
| T089 | Task | Build the notification service: push (web/FCM), SMS, email with quiet hours and per-tenant templates | 8 | Medium | S11 | T026 |
| T090 | Story | As a student at risk of dropping off, I receive a personalised nudge with a 10-minute plan | 5 | Low | S13 | T089, T055 |
| T091 | Task | Implement achievements and chapter-mastery certificates (shareable, verifiable) | 3 | Low | S14 | T049 |

#### T087 · As a student, I see my streak, XP and daily goal update instantly after each answer

*Story · 5 pts · Medium · APL Sprint 10 · labels: gamification, redis*

Streak/XP rules engine on the Redis consumer; UI badges; streak-freeze item earned by mastery (not purchase); daily goal adapts to days-to-exam.

Acceptance criteria:

- Streak updates in UI < 200 ms after answer (p95)
- Timezone-correct day boundaries (Africa/Tunis)
- Rules configurable per tenant

Blocked by: T026 (Deploy Redis Cluster (ElastiCache) and the real-time aggregation consumer)

#### T088 · As a student, I see class and national leaderboards that reward mastery gain, not volume

*Story · 5 pts · Medium · APL Sprint 11 · labels: leaderboard*

Sorted-set leaderboards keyed on weekly mastery delta (from DKT) with ties broken by consistency; opt-out and anonymous mode; school-level leaderboards visible to teachers.

Acceptance criteria:

- Leaderboard read p99 < 20 ms
- A student who opts out never appears, including in cached pages
- Ranking metric documented and explained in-app

Blocked by: T026 (Deploy Redis Cluster (ElastiCache) and the real-time aggregation consumer), T049 (Expose per-KC mastery estimates and attention-based explanations via an internal API)

#### T089 · Build the notification service: push (web/FCM), SMS, email with quiet hours and per-tenant templates

*Task · 8 pts · Medium · APL Sprint 11 · labels: notifications, sms, push*

Notification microservice consuming engagement events; providers: FCM web push, SMS via local Tunisian gateway (e.g., Tunisie Telecom API or aggregator), email via SES; quiet hours 22:00–07:00 Africa/Tunis; template management in Arabic/French.

Acceptance criteria:

- No notification sent during quiet hours (automated test)
- SMS delivery rate ≥ 95% with Tunisian operators in pilot
- Unsubscribe link honoured within 1 minute

Blocked by: T026 (Deploy Redis Cluster (ElastiCache) and the real-time aggregation consumer)

#### T090 · As a student at risk of dropping off, I receive a personalised nudge with a 10-minute plan

*Story · 5 pts · Low · APL Sprint 13 · labels: retention, nudges*

Churn-risk heuristic (later a model) on engagement features; nudge content generated through the gateway and judged; A/B tested against no-nudge.

Acceptance criteria:

- Nudge A/B shows statistically significant retention lift or is turned off
- Max 1 nudge per day per student
- Nudges respect parental notification preferences

Blocked by: T089 (Build the notification service: push (web/FCM), SMS, email with quiet hours and per-tenant templates), T055 (Build the experimentation framework: assignment, exposure logging, learning-gain metrics)

#### T091 · Implement achievements and chapter-mastery certificates (shareable, verifiable)

*Task · 3 pts · Low · APL Sprint 14 · labels: achievements*

Badge rules on mastery thresholds; signed certificate PDF with verification URL; share card image generated server-side.

Acceptance criteria:

- Certificate verification URL validates signature
- Badges localised and RTL-correct
- No badge rewards raw time-on-platform

Blocked by: T049 (Expose per-KC mastery estimates and attention-based explanations via an internal API)


### E11 — Institution & Parent B2B Portals (Multi-Tenancy)

**Phase:** Phase 4 · **Priority:** High · **Component:** Backend · **9 tickets / 79 pts**

**Goal.** Strict PostgreSQL RLS tenant isolation, a teacher dashboard with cohort anomaly detection and intervention alerts, a parent portal, and seat-based Stripe billing for schools.

**Definition of done.** Cross-tenant data access is impossible by construction (verified by automated RLS test suite); a school can be onboarded and billed with zero engineering involvement.

| ID | Type | Summary | Pts | Priority | Sprint | Blocked by |
|---|---|---|---|---|---|---|
| T092 | Task | Implement PostgreSQL Row-Level Security multi-tenancy with a tenant-context connection layer | 13 | Highest | S6 | T014 |
| T093 | Story | As a platform admin, I onboard a school in 10 minutes: tenant, admins, classes, CSV student import | 8 | High | S12 | T092, T013 |
| T094 | Story | As a school, I sign in with our Microsoft 365 / Google Workspace SSO | 8 | Medium | S14 | T012, T092 |
| T095 | Story | As a teacher, I see real-time mastery heatmaps for my cohort and get intervention alerts | 13 | High | S13 | T049, T026, T092 |
| T096 | Task | Build cohort anomaly detection: sudden drops, cheating patterns, disengagement | 8 | High | S14 | T095 |
| T097 | Story | As a parent, I see my child's progress, consent settings and screen-time controls | 8 | Medium | S14 | T013, T049 |
| T098 | Task | Build seat-based B2B subscription billing with Stripe (annual school licences, proration, invoices) | 13 | High | S15 | T093 |
| T099 | Spike | Evaluate local payment rails for B2C (Flouci, D17, ClicToPay, bank transfer) alongside Stripe | 3 | Medium | S15 | T098 |
| T100 | Story | As a school admin, I export term reports and usage analytics per class | 5 | Medium | S16 | T095 |

#### T092 · Implement PostgreSQL Row-Level Security multi-tenancy with a tenant-context connection layer

*Task · 13 pts · Highest · APL Sprint 6 · labels: multi-tenant, rls, postgres*

Every tenant-scoped table gets `tenant_id` + RLS policies; app sets `SET LOCAL app.tenant_id` per transaction from the JWT; service roles cannot bypass RLS; shared tables (items, KC graph) are read-only to tenants; migration tooling validates policies exist on every new table.

Acceptance criteria:

- Automated test suite attempts 200 cross-tenant reads/writes via every service and all fail
- A new table without RLS fails the migration CI check
- RLS adds < 5% query latency on the top-20 queries

Blocked by: T014 (Implement attribute-based authorisation middleware shared by all Node.js services)

#### T093 · As a platform admin, I onboard a school in 10 minutes: tenant, admins, classes, CSV student import

*Story · 8 pts · High · APL Sprint 12 · labels: onboarding, admin*

Admin console: create tenant, invite school admin, bulk-import students/classes from CSV (with validation and consent-status tracking), custom subdomain, branding.

Acceptance criteria:

- CSV import of 1,500 students completes with a per-row error report
- Students receive activation + parent-consent flow automatically
- Tenant deletion fully purges tenant data (verified by audit script)

Blocked by: T092 (Implement PostgreSQL Row-Level Security multi-tenancy with a tenant-context connection layer), T013 (As a parent, I give verifiable consent before my under-18 child's account is activated)

#### T094 · As a school, I sign in with our Microsoft 365 / Google Workspace SSO

*Story · 8 pts · Medium · APL Sprint 14 · labels: sso, saml*

Keycloak identity brokering per tenant (SAML/OIDC), just-in-time provisioning with role mapping, SCIM for roster sync where available.

Acceptance criteria:

- SSO login works for a pilot school using Microsoft 365
- Role mapping configurable by school admin
- Deprovisioned user loses access within 15 minutes

Blocked by: T012 (Deploy Keycloak identity provider with student / parent / teacher / school-admin realms), T092 (Implement PostgreSQL Row-Level Security multi-tenancy with a tenant-context connection layer)

#### T095 · As a teacher, I see real-time mastery heatmaps for my cohort and get intervention alerts

*Story · 13 pts · High · APL Sprint 13 · labels: teacher-dashboard, analytics*

Dashboard: KC × student heatmap from mastery API, live 'struggling now' feed from Kafka, trend per chapter, assignment completion; alerts when a student's mastery drops or disengages for 5 days; export to PDF.

Acceptance criteria:

- Heatmap for a 40-student class loads < 2 s
- Intervention alert fires within 10 minutes of the trigger condition
- Teacher can act on an alert (message, assign remediation) in-app

Blocked by: T049 (Expose per-KC mastery estimates and attention-based explanations via an internal API), T026 (Deploy Redis Cluster (ElastiCache) and the real-time aggregation consumer), T092 (Implement PostgreSQL Row-Level Security multi-tenancy with a tenant-context connection layer)

#### T096 · Build cohort anomaly detection: sudden drops, cheating patterns, disengagement

*Task · 8 pts · High · APL Sprint 14 · labels: anomaly-detection, integrity*

Streaming detectors: accuracy drop vs. own baseline, impossibly fast correct answers (cheating), copy-paste bursts, answer-pattern similarity across students in the same session (collusion), 5-day inactivity. Alerts to teacher dashboard with explanation.

Acceptance criteria:

- Seeded cheating pattern detected ≥ 90% with ≤ 5% false positive on pilot data
- Alerts are explainable (which signal fired)
- Teacher can mark false positive, which tunes the threshold

Blocked by: T095 (As a teacher, I see real-time mastery heatmaps for my cohort and get intervention alerts)

#### T097 · As a parent, I see my child's progress, consent settings and screen-time controls

*Story · 8 pts · Medium · APL Sprint 14 · labels: parent-portal*

Parent web/mobile portal: progress summary, weekly reports, consent management, daily time limit, notification preferences; linked to child via consent flow.

Acceptance criteria:

- Parent can only see children linked by verified consent
- Time limit enforced in the student app within 1 minute
- Portal fully bilingual

Blocked by: T013 (As a parent, I give verifiable consent before my under-18 child's account is activated), T049 (Expose per-KC mastery estimates and attention-based explanations via an internal API)

#### T098 · Build seat-based B2B subscription billing with Stripe (annual school licences, proration, invoices)

*Task · 13 pts · High · APL Sprint 15 · labels: stripe, billing*

Stripe Billing: products for school seat packs and B2C family plans, usage reporting of active seats, proration on seat changes, Tunisian VAT handling, invoices in French, webhook processing with idempotency, dunning emails, grace period before read-only mode.

Acceptance criteria:

- Seat count change mid-term produces a correct prorated invoice (tested against Stripe test clocks)
- Webhook replay does not double-apply
- Tenant enters read-only mode 14 days after failed payment with warnings at 3 and 7 days

Blocked by: T093 (As a platform admin, I onboard a school in 10 minutes: tenant, admins, classes, CSV student import)

#### T099 · Evaluate local payment rails for B2C (Flouci, D17, ClicToPay, bank transfer) alongside Stripe

*Spike · 3 pts · Medium · APL Sprint 15 · labels: payments, spike*

Stripe card coverage is limited for Tunisian consumers. Evaluate local PSP integration options, compliance and reconciliation; recommend an approach for family plans.

Acceptance criteria:

- Recommendation doc with costs, settlement times and integration effort
- Decision recorded as ADR
- Follow-up stories created

Blocked by: T098 (Build seat-based B2B subscription billing with Stripe (annual school licences, proration, invoices))

#### T100 · As a school admin, I export term reports and usage analytics per class

*Story · 5 pts · Medium · APL Sprint 16 · labels: reports*

Scheduled and on-demand PDF/XLSX reports: mastery by chapter, usage, licence utilisation; branded per tenant; delivered to admin email and portal.

Acceptance criteria:

- Report for 2,000 students generates < 5 minutes
- Reports exclude students who opted out of analytics sharing
- XLSX opens cleanly in Excel and LibreOffice

Blocked by: T095 (As a teacher, I see real-time mastery heatmaps for my cohort and get intervention alerts)


### E12 — Observability, Quality & Release Readiness

**Phase:** Phase 4 · **Priority:** High · **Component:** QA · **10 tickets / 81 pts**

**Goal.** Prove the system survives Bac-eve traffic: load tests at 50k concurrent users, chaos experiments, DR drills, SLOs with alerting, and a launch war-room runbook.

**Definition of done.** 50k-concurrent load test passes all SLOs; RPO ≤ 15 min, RTO ≤ 1 h demonstrated in a drill; on-call rotation and runbooks signed off.

| ID | Type | Summary | Pts | Priority | Sprint | Blocked by |
|---|---|---|---|---|---|---|
| T101 | Task | Define SLOs and error budgets per service and wire burn-rate alerting | 5 | Highest | S6 | T007 |
| T102 | Task | Build the Playwright end-to-end suite covering the core learner journey in both languages | 13 | High | S8 | T010, T076 |
| T103 | Task | Implement consumer-driven contract tests (Pact) between frontend, gateway and microservices | 8 | High | S7 | T006 |
| T104 | Task | Run Bac-eve load test: 50,000 concurrent students, 50k events/s, 2,000 inference RPS | 13 | Highest | S14 | T101, T052, T084, T025 |
| T105 | Task | Run chaos experiments: AZ loss, Kafka broker loss, TorchServe outage, LLM provider outage, Redis failover | 8 | High | S15 | T104 |
| T106 | Task | Implement backups and disaster recovery: cross-region replication, RPO 15 min / RTO 1 h, quarterly drill | 13 | High | S16 | T003, T021 |
| T107 | Task | Write operational runbooks, on-call rotation and incident process | 5 | High | S16 | T101 |
| T108 | Task | Run the closed pilot with 3 schools (≈ 2,000 students) and triage findings | 8 | Highest | S12 | T052, T069, T079, T093 |
| T109 | Task | Prepare the exam-season war room: freeze window, scaling pre-warm, comms plan | 3 | High | S17 | T104, T107 |
| T110 | Task | Production go-live (Physics + Maths) and 30-day hypercare | 5 | Highest | S18 | T108, T020, T106, T109 |

#### T101 · Define SLOs and error budgets per service and wire burn-rate alerting

*Task · 5 pts · Highest · APL Sprint 6 · labels: slo, alerting*

SLOs: API availability 99.9%, routing p99 ≤ 80 ms, telemetry ingest success ≥ 99.99%, tutor first-token p75 ≤ 1.2 s, inference p99 ≤ 50 ms. Multi-window burn-rate alerts in Datadog → PagerDuty; SLO dashboard per team.

Acceptance criteria:

- Every production service has an SLO doc and dashboard
- Fast-burn alert fires within 5 minutes of a simulated outage
- Error-budget policy agreed (feature freeze when exhausted)

Blocked by: T007 (Roll out Datadog APM, distributed tracing, log pipeline and memory-leak watchdogs)

#### T102 · Build the Playwright end-to-end suite covering the core learner journey in both languages

*Task · 13 pts · High · APL Sprint 8 · labels: playwright, e2e*

Journeys: signup + consent, placement test, routed session with widget interaction, tutor hint ladder, offline/online assessment, battle, teacher dashboard, billing. Runs on preview envs per PR (smoke subset) and nightly (full) on real mobile device cloud.

Acceptance criteria:

- Full suite < 25 minutes, flake rate < 2%
- Smoke subset blocks merge
- Runs on Chrome, Safari iOS and Android WebView

Blocked by: T010 (Provision ephemeral preview environments per pull request), T076 (Architect the Next.js 15 app: App Router, design system, i18n (ar/fr) with RTL, auth integration)

#### T103 · Implement consumer-driven contract tests (Pact) between frontend, gateway and microservices

*Task · 8 pts · High · APL Sprint 7 · labels: pact, contract-testing*

Pact broker; contracts for every public API and Kafka event schema (via Schema Registry compatibility checks); can-I-deploy gate in CI.

Acceptance criteria:

- A breaking API change fails the provider's CI before merge
- Pact broker shows contract matrix for all services
- Kafka compatibility check integrated into the same gate

Blocked by: T006 (Build GitHub Actions CI pipeline: lint, unit, contract, container scan, SBOM)

#### T104 · Run Bac-eve load test: 50,000 concurrent students, 50k events/s, 2,000 inference RPS

*Task · 13 pts · Highest · APL Sprint 14 · labels: load-test, k6, capacity*

k6 scenarios modelled on pilot traffic shapes (evening peak, exam eve), including widgets, tutor, routing and battles; executed against a prod-sized staging; Karpenter scaling, Kafka lag, TorchServe and Redis observed; capacity report and tuning.

Acceptance criteria:

- All SLOs met for 60 minutes at target load
- Auto-scaling reaches steady state < 5 minutes after the ramp
- Capacity model documents headroom and cost at 100k concurrent

Blocked by: T101 (Define SLOs and error budgets per service and wire burn-rate alerting), T052 (Build the routing microservice (Node.js) with cached graph, TorchServe client and policy engine), T084 (As a student, I challenge a peer to a real-time 5-question physics battle), T025 (Build the telemetry ingestion service (HTTP → Kafka) with validation and backpressure)

#### T105 · Run chaos experiments: AZ loss, Kafka broker loss, TorchServe outage, LLM provider outage, Redis failover

*Task · 8 pts · High · APL Sprint 15 · labels: chaos, resilience*

Litmus/AWS FIS experiments in staging with hypotheses and abort conditions; verify graceful degradation paths (IRT fallback, template hints, read-only mode).

Acceptance criteria:

- Each experiment has a written hypothesis and outcome
- No experiment causes data loss
- Three degradation paths exercised and found working

Blocked by: T104 (Run Bac-eve load test: 50,000 concurrent students, 50k events/s, 2,000 inference RPS)

#### T106 · Implement backups and disaster recovery: cross-region replication, RPO 15 min / RTO 1 h, quarterly drill

*Task · 13 pts · High · APL Sprint 16 · labels: dr, backups*

RDS PITR + cross-region snapshots, Kafka MirrorMaker to DR region (or S3 tiered storage), Snowflake replication, S3 CRR, Terraform-driven DR environment; documented failover and failback; first drill executed.

Acceptance criteria:

- Drill restores a full environment in DR region within 1 h with ≤ 15 min data loss
- Drill report with action items
- Backups tested by restore, not just existence

Blocked by: T003 (Deploy AWS EKS cluster with managed node groups, Karpenter and GPU node pool), T021 (Provision Apache Kafka (MSK) cluster with Schema Registry and topic conventions)

#### T107 · Write operational runbooks, on-call rotation and incident process

*Task · 5 pts · High · APL Sprint 16 · labels: runbooks, on-call*

Runbooks for top-20 alerts; PagerDuty rotation across backend/platform/ML; incident severity matrix; postmortem template; status page.

Acceptance criteria:

- Every paging alert links to a runbook
- Two tabletop incident exercises completed
- Public status page live

Blocked by: T101 (Define SLOs and error budgets per service and wire burn-rate alerting)

#### T108 · Run the closed pilot with 3 schools (≈ 2,000 students) and triage findings

*Task · 8 pts · Highest · APL Sprint 12 · labels: pilot, launch*

Pilot plan, success metrics (learning gain, retention, CSAT, SLOs), feedback loops with teachers, weekly triage; exit criteria to open launch.

Acceptance criteria:

- Pilot exit criteria met or explicit go/no-go decision documented
- All Sev-1/2 pilot bugs closed
- Teacher and student CSAT ≥ 4.0

Blocked by: T052 (Build the routing microservice (Node.js) with cached graph, TorchServe client and policy engine), T069 (As a student, I chat with a streaming tutor beside the item, in Arabic or French, with LaTeX rendering), T079 (As a student, I explore mechanics sandboxes: projectile motion, inclined plane, pendulum, collisions — with draggable vectors), T093 (As a platform admin, I onboard a school in 10 minutes: tenant, admins, classes, CSV student import)

#### T109 · Prepare the exam-season war room: freeze window, scaling pre-warm, comms plan

*Task · 3 pts · High · APL Sprint 17 · labels: launch, exam-season*

Change freeze 2 weeks before Bac; pre-scaled node pools and Redis; LLM budget uplift; on-call doubled; status comms templates in Arabic/French; daily readiness checklist.

Acceptance criteria:

- Freeze enforced via ArgoCD sync windows
- Pre-warm script tested in staging
- Comms templates approved

Blocked by: T104 (Run Bac-eve load test: 50,000 concurrent students, 50k events/s, 2,000 inference RPS), T107 (Write operational runbooks, on-call rotation and incident process)

#### T110 · Production go-live (Physics + Maths) and 30-day hypercare

*Task · 5 pts · Highest · APL Sprint 18 · labels: launch*

Final security review, DPIA sign-off check, go-live checklist, phased rollout by governorate, daily hypercare standups, success metrics dashboard.

Acceptance criteria:

- Go-live checklist 100% complete and signed
- No Sev-1 open at day 30
- Hypercare report delivered to leadership

Blocked by: T108 (Run the closed pilot with 3 schools (≈ 2,000 students) and triage findings), T020 (Commission third-party penetration test and remediate findings), T106 (Implement backups and disaster recovery: cross-region replication, RPO 15 min / RTO 1 h, quarterly drill), T109 (Prepare the exam-season war room: freeze window, scaling pre-warm, comms plan)


### E13 — Subject Expansion: Maths, Sciences, Technique, Économie & Gestion

**Phase:** Phase 6 · **Priority:** High · **Component:** Curriculum · **22 tickets / 207 pts**

**Goal.** Load four more subjects onto the same engine: a KC graph, item bank, textbook corpus, glossary and misconception taxonomy per subject, plus the subject-specific widget packages and verifiers. Content tracks run in parallel from S9 under one subject lead each; Maths ships with the physics go-live, the rest in two waves after.

**Definition of done.** All five subjects live with ≥ 300 KCs and ≥ 4,000 calibrated items each; no engine code forked per subject; cross-subject daily planner active for every track.

| ID | Type | Summary | Pts | Priority | Sprint | Blocked by |
|---|---|---|---|---|---|---|
| T111 | Task | Mathématiques: encode the KC graph for all relevant Bac tracks | 8 | High | S9 | T034, T033 |
| T112 | Task | Mathématiques: build and tag the item bank incl. past Bac papers | 13 | High | S11 | T111, T037 |
| T113 | Task | Mathématiques: ingest official textbooks into the RAG corpus and build glossary + misconception taxonomy | 8 | High | S11 | T111, T039 |
| T114 | Task | Sciences (SVT / Chimie): encode the KC graph for all relevant Bac tracks | 8 | High | S10 | T034, T033 |
| T115 | Task | Sciences (SVT / Chimie): build and tag the item bank incl. past Bac papers | 13 | High | S13 | T114, T037 |
| T116 | Task | Sciences (SVT / Chimie): ingest official textbooks into the RAG corpus and build glossary + misconception taxonomy | 8 | High | S13 | T114, T039 |
| T117 | Task | Sciences techniques: encode the KC graph for all relevant Bac tracks | 8 | High | S11 | T034, T033 |
| T118 | Task | Sciences techniques: build and tag the item bank incl. past Bac papers | 13 | High | S14 | T117, T037 |
| T119 | Task | Sciences techniques: ingest official textbooks into the RAG corpus and build glossary + misconception taxonomy | 8 | High | S14 | T117, T039 |
| T120 | Task | Économie & Gestion: encode the KC graph for all relevant Bac tracks | 8 | High | S12 | T034, T033 |
| T121 | Task | Économie & Gestion: build and tag the item bank incl. past Bac papers | 13 | High | S15 | T120, T037 |
| T122 | Task | Économie & Gestion: ingest official textbooks into the RAG corpus and build glossary + misconception taxonomy | 8 | High | S15 | T120, T039 |
| T123 | Story | As a maths student, I use graphing, geometry and sequence/limit explorers with draggable parameters | 13 | High | S10 | T078, T111 |
| T124 | Story | As a sciences student, I explore chemistry and biology sims: titration, kinetics, molecular geometry, genetics crosses | 13 | High | S12 | T078, T114 |
| T125 | Story | As a sciences-techniques student, I build mechanisms and logic/automation schematics and simulate them | 13 | High | S13 | T078, T080, T117 |
| T126 | Story | As an éco/gestion student, I work in interactive financial statements, supply/demand and accounting-entry widgets | 13 | High | S14 | T078, T120 |
| T127 | Task | Calibrate the rubric verifier and tutor prompts for éco/gestion and descriptive sciences | 8 | High | S15 | T063, T068, T122, T116 |
| T128 | Task | Calibrate Maths, Sciences, Technique and Éco/Gestion items on pilot cohorts | 8 | Medium | S17 | T044, T112, T115, T118, T121 |
| T129 | Task | Train and validate SAINT+ per subject (or shared with subject embedding) and gate per subject | 8 | High | S16 | T047, T112, T115 |
| T130 | Task | Release Mathématiques with the physics go-live (S18) | 5 | High | S18 | T112, T113, T123, T057, T108 |
| T131 | Task | Release wave 2: Sciences and Sciences techniques | 5 | High | S19 | T110, T115, T116, T118, T119, T124, T125, T128 |
| T132 | Task | Release wave 3: Économie & Gestion and full-track coverage review | 5 | High | S20 | T131, T121, T122, T126, T127, T129 |

#### T111 · Mathématiques: encode the KC graph for all relevant Bac tracks

*Task · 8 pts · High · APL Sprint 9 · labels: content, maths, knowledge-graph*

Subject lead encodes the official Mathématiques programme as knowledge components with prerequisite edges, chapter mapping and exam weight per track, cross-checked against 10 years of Bac papers.

Acceptance criteria:

- ≥ 350 KCs published as maths graph v1.0 with prerequisite edges
- Every past-exam question (10 years) maps to at least one KC
- Pedagogical sign-off recorded

Blocked by: T034 (As a curriculum lead, I author and version the KC graph in a web editor with review workflow), T033 (Make `subject` and `track` first-class across the KC graph, item bank, routing, mastery API and telemetry)

#### T112 · Mathématiques: build and tag the item bank incl. past Bac papers

*Task · 13 pts · High · APL Sprint 11 · labels: content, maths, item-bank*

Digitise and tag past Bac Mathématiques papers, author new items to reach ≥ 8 items per KC with a difficulty spread, bilingual where the programme is bilingual; double-tag a 10% sample.

Acceptance criteria:

- ≥ 5000 published items; no KC with fewer than 8
- Inter-rater tagging agreement κ ≥ 0.75 on the sample
- Provenance (year, track) on every past-exam item

Blocked by: T111 (Mathématiques: encode the KC graph for all relevant Bac tracks), T037 (As a teacher-author, I create, preview and submit items for review in the authoring tool)

#### T113 · Mathématiques: ingest official textbooks into the RAG corpus and build glossary + misconception taxonomy

*Task · 8 pts · High · APL Sprint 11 · labels: content, maths, rag*

OCR/layout extraction of the official Mathématiques manuals with KC-aware chunking into pgvector; Arabic/French glossary of all KC names; misconception taxonomy from past-paper examiner reports.

Acceptance criteria:

- Retrieval precision@5 ≥ 0.85 on a 150-question subject eval set
- Glossary covers 100% of KC names
- ≥ 50% of wrong answers map to a named misconception

Blocked by: T111 (Mathématiques: encode the KC graph for all relevant Bac tracks), T039 (Ingest official textbooks into the RAG corpus with chapter/KC-aware chunking)

#### T114 · Sciences (SVT / Chimie): encode the KC graph for all relevant Bac tracks

*Task · 8 pts · High · APL Sprint 10 · labels: content, sciences, knowledge-graph*

Subject lead encodes the official Sciences (SVT / Chimie) programme as knowledge components with prerequisite edges, chapter mapping and exam weight per track, cross-checked against 10 years of Bac papers.

Acceptance criteria:

- ≥ 400 KCs published as sciences graph v1.0 with prerequisite edges
- Every past-exam question (10 years) maps to at least one KC
- Pedagogical sign-off recorded

Blocked by: T034 (As a curriculum lead, I author and version the KC graph in a web editor with review workflow), T033 (Make `subject` and `track` first-class across the KC graph, item bank, routing, mastery API and telemetry)

#### T115 · Sciences (SVT / Chimie): build and tag the item bank incl. past Bac papers

*Task · 13 pts · High · APL Sprint 13 · labels: content, sciences, item-bank*

Digitise and tag past Bac Sciences (SVT / Chimie) papers, author new items to reach ≥ 8 items per KC with a difficulty spread, bilingual where the programme is bilingual; double-tag a 10% sample.

Acceptance criteria:

- ≥ 5000 published items; no KC with fewer than 8
- Inter-rater tagging agreement κ ≥ 0.75 on the sample
- Provenance (year, track) on every past-exam item

Blocked by: T114 (Sciences (SVT / Chimie): encode the KC graph for all relevant Bac tracks), T037 (As a teacher-author, I create, preview and submit items for review in the authoring tool)

#### T116 · Sciences (SVT / Chimie): ingest official textbooks into the RAG corpus and build glossary + misconception taxonomy

*Task · 8 pts · High · APL Sprint 13 · labels: content, sciences, rag*

OCR/layout extraction of the official Sciences (SVT / Chimie) manuals with KC-aware chunking into pgvector; Arabic/French glossary of all KC names; misconception taxonomy from past-paper examiner reports.

Acceptance criteria:

- Retrieval precision@5 ≥ 0.85 on a 150-question subject eval set
- Glossary covers 100% of KC names
- ≥ 50% of wrong answers map to a named misconception

Blocked by: T114 (Sciences (SVT / Chimie): encode the KC graph for all relevant Bac tracks), T039 (Ingest official textbooks into the RAG corpus with chapter/KC-aware chunking)

#### T117 · Sciences techniques: encode the KC graph for all relevant Bac tracks

*Task · 8 pts · High · APL Sprint 11 · labels: content, technique, knowledge-graph*

Subject lead encodes the official Sciences techniques programme as knowledge components with prerequisite edges, chapter mapping and exam weight per track, cross-checked against 10 years of Bac papers.

Acceptance criteria:

- ≥ 300 KCs published as technique graph v1.0 with prerequisite edges
- Every past-exam question (10 years) maps to at least one KC
- Pedagogical sign-off recorded

Blocked by: T034 (As a curriculum lead, I author and version the KC graph in a web editor with review workflow), T033 (Make `subject` and `track` first-class across the KC graph, item bank, routing, mastery API and telemetry)

#### T118 · Sciences techniques: build and tag the item bank incl. past Bac papers

*Task · 13 pts · High · APL Sprint 14 · labels: content, technique, item-bank*

Digitise and tag past Bac Sciences techniques papers, author new items to reach ≥ 8 items per KC with a difficulty spread, bilingual where the programme is bilingual; double-tag a 10% sample.

Acceptance criteria:

- ≥ 4000 published items; no KC with fewer than 8
- Inter-rater tagging agreement κ ≥ 0.75 on the sample
- Provenance (year, track) on every past-exam item

Blocked by: T117 (Sciences techniques: encode the KC graph for all relevant Bac tracks), T037 (As a teacher-author, I create, preview and submit items for review in the authoring tool)

#### T119 · Sciences techniques: ingest official textbooks into the RAG corpus and build glossary + misconception taxonomy

*Task · 8 pts · High · APL Sprint 14 · labels: content, technique, rag*

OCR/layout extraction of the official Sciences techniques manuals with KC-aware chunking into pgvector; Arabic/French glossary of all KC names; misconception taxonomy from past-paper examiner reports.

Acceptance criteria:

- Retrieval precision@5 ≥ 0.85 on a 150-question subject eval set
- Glossary covers 100% of KC names
- ≥ 50% of wrong answers map to a named misconception

Blocked by: T117 (Sciences techniques: encode the KC graph for all relevant Bac tracks), T039 (Ingest official textbooks into the RAG corpus with chapter/KC-aware chunking)

#### T120 · Économie & Gestion: encode the KC graph for all relevant Bac tracks

*Task · 8 pts · High · APL Sprint 12 · labels: content, eco, knowledge-graph*

Subject lead encodes the official Économie & Gestion programme as knowledge components with prerequisite edges, chapter mapping and exam weight per track, cross-checked against 10 years of Bac papers.

Acceptance criteria:

- ≥ 300 KCs published as eco graph v1.0 with prerequisite edges
- Every past-exam question (10 years) maps to at least one KC
- Pedagogical sign-off recorded

Blocked by: T034 (As a curriculum lead, I author and version the KC graph in a web editor with review workflow), T033 (Make `subject` and `track` first-class across the KC graph, item bank, routing, mastery API and telemetry)

#### T121 · Économie & Gestion: build and tag the item bank incl. past Bac papers

*Task · 13 pts · High · APL Sprint 15 · labels: content, eco, item-bank*

Digitise and tag past Bac Économie & Gestion papers, author new items to reach ≥ 8 items per KC with a difficulty spread, bilingual where the programme is bilingual; double-tag a 10% sample.

Acceptance criteria:

- ≥ 4000 published items; no KC with fewer than 8
- Inter-rater tagging agreement κ ≥ 0.75 on the sample
- Provenance (year, track) on every past-exam item

Blocked by: T120 (Économie & Gestion: encode the KC graph for all relevant Bac tracks), T037 (As a teacher-author, I create, preview and submit items for review in the authoring tool)

#### T122 · Économie & Gestion: ingest official textbooks into the RAG corpus and build glossary + misconception taxonomy

*Task · 8 pts · High · APL Sprint 15 · labels: content, eco, rag*

OCR/layout extraction of the official Économie & Gestion manuals with KC-aware chunking into pgvector; Arabic/French glossary of all KC names; misconception taxonomy from past-paper examiner reports.

Acceptance criteria:

- Retrieval precision@5 ≥ 0.85 on a 150-question subject eval set
- Glossary covers 100% of KC names
- ≥ 50% of wrong answers map to a named misconception

Blocked by: T120 (Économie & Gestion: encode the KC graph for all relevant Bac tracks), T039 (Ingest official textbooks into the RAG corpus with chapter/KC-aware chunking)

#### T123 · As a maths student, I use graphing, geometry and sequence/limit explorers with draggable parameters

*Story · 13 pts · High · APL Sprint 10 · labels: widgets, maths*

`@apl/widgets-maths`: interactive function grapher (parameters, derivatives, integrals shading), 2D/3D geometry bench (vectors, complex plane, solids), sequence and limit explorer, probability simulators; parameter spaces exposed for randomised items.

Acceptance criteria:

- Each widget passes the maths lead's accuracy review
- Graph-reading items score robustly to touch imprecision
- Package lazy-loads only for maths-enrolled students

Blocked by: T078 (Build the per-subject widget package system (registry, lazy loading, parameter-space contract)), T111 (Mathématiques: encode the KC graph for all relevant Bac tracks)

#### T124 · As a sciences student, I explore chemistry and biology sims: titration, kinetics, molecular geometry, genetics crosses

*Story · 13 pts · High · APL Sprint 12 · labels: widgets, sciences*

`@apl/widgets-sciences`: titration curve lab, reaction kinetics with rate laws, 3D molecule viewer, Punnett/genetics cross tool, cell-process animations; linked to items.

Acceptance criteria:

- Titration and kinetics results match reference calculations within 1%
- 3D viewer runs at tier 1 on integrated GPUs
- Reduced-motion mode on all animations

Blocked by: T078 (Build the per-subject widget package system (registry, lazy loading, parameter-space contract)), T114 (Sciences (SVT / Chimie): encode the KC graph for all relevant Bac tracks)

#### T125 · As a sciences-techniques student, I build mechanisms and logic/automation schematics and simulate them

*Story · 13 pts · High · APL Sprint 13 · labels: widgets, technique*

`@apl/widgets-technique`: mechanism bench (gears, linkages, transmission ratios), logic-gate and GRAFCET/automation simulator, basic electrical schematic reuse from the physics circuit builder, technical-drawing reading items.

Acceptance criteria:

- GRAFCET simulator validated against 20 reference sequences
- Reuses the physics circuit solver without a fork
- Mechanism bench passes the technique lead's review

Blocked by: T078 (Build the per-subject widget package system (registry, lazy loading, parameter-space contract)), T080 (As a student, I build DC and RLC circuits on a canvas and watch current, voltage and resonance curves), T117 (Sciences techniques: encode the KC graph for all relevant Bac tracks)

#### T126 · As an éco/gestion student, I work in interactive financial statements, supply/demand and accounting-entry widgets

*Story · 13 pts · High · APL Sprint 14 · labels: widgets, eco*

`@apl/widgets-eco`: spreadsheet-style balance sheet / income statement builder with live ratios, supply-demand and elasticity graphs, journal-entry and ledger posting tool, case-study reader with structured-answer forms.

Acceptance criteria:

- Accounting widgets validate entries against the Tunisian chart of accounts (PCG)
- Ratio calculations match reference within rounding
- Structured-answer forms feed the rubric verifier

Blocked by: T078 (Build the per-subject widget package system (registry, lazy loading, parameter-space contract)), T120 (Économie & Gestion: encode the KC graph for all relevant Bac tracks)

#### T127 · Calibrate the rubric verifier and tutor prompts for éco/gestion and descriptive sciences

*Task · 8 pts · High · APL Sprint 15 · labels: evals, eco, sciences*

Build a 600-case golden set (essays, case studies, SVT explanations) labelled by subject leads; tune the rubric verifier thresholds and the Socratic prompts per subject; run the red-team suite per subject.

Acceptance criteria:

- Rubric verifier ≥ 93% catch / ≤ 5% false block on the golden set
- Per-subject prompt eval passes in CI
- Red-team suite ≥ 98% per subject

Blocked by: T063 (Refactor the judge into a verifier plug-in interface with symbolic and rubric implementations), T068 (Curate the golden evaluation dataset for tutor quality with curriculum team), T122 (Économie & Gestion: ingest official textbooks into the RAG corpus and build glossary + misconception taxonomy), T116 (Sciences (SVT / Chimie): ingest official textbooks into the RAG corpus and build glossary + misconception taxonomy)

#### T128 · Calibrate Maths, Sciences, Technique and Éco/Gestion items on pilot cohorts

*Task · 8 pts · Medium · APL Sprint 17 · labels: irt, calibration*

Expose each new bank to its pilot cohort in fixed sequence; fit IRT per item; prune negative-discrimination items; return to authors. Reuses the physics calibration pipeline.

Acceptance criteria:

- IRT parameters on every item with ≥ 200 responses per subject
- Items with discrimination < 0.3 unpublished pending review
- Calibration reports per subject

Blocked by: T044 (Run pilot item calibration and prune bad items), T112 (Mathématiques: build and tag the item bank incl. past Bac papers), T115 (Sciences (SVT / Chimie): build and tag the item bank incl. past Bac papers), T118 (Sciences techniques: build and tag the item bank incl. past Bac papers), T121 (Économie & Gestion: build and tag the item bank incl. past Bac papers)

#### T129 · Train and validate SAINT+ per subject (or shared with subject embedding) and gate per subject

*Task · 8 pts · High · APL Sprint 16 · labels: pykt, multi-subject*

Evaluate one shared model with a subject embedding vs. one model per subject on pilot data; champion/challenger gate reports per-subject AUC/ECE; TorchServe serves the chosen layout with per-subject model versions.

Acceptance criteria:

- ADR on shared vs. per-subject model with evidence
- AUC ≥ 0.78 per subject on held-out data
- Promotion gate blocks on any single-subject regression

Blocked by: T047 (Build champion/challenger evaluation gate and automatic rollback on metric regression), T112 (Mathématiques: build and tag the item bank incl. past Bac papers), T115 (Sciences (SVT / Chimie): build and tag the item bank incl. past Bac papers)

#### T130 · Release Mathématiques with the physics go-live (S18)

*Task · 5 pts · High · APL Sprint 18 · labels: release, maths*

Maths KC graph, item bank, widgets and verifier enabled for pilot tenants; cross-subject planner active for tracks containing both subjects; readiness checklist.

Acceptance criteria:

- Maths enabled for all pilot tenants with physics
- Planner splits sessions across both subjects
- No Sev-1/2 maths content bugs open

Blocked by: T112 (Mathématiques: build and tag the item bank incl. past Bac papers), T113 (Mathématiques: ingest official textbooks into the RAG corpus and build glossary + misconception taxonomy), T123 (As a maths student, I use graphing, geometry and sequence/limit explorers with draggable parameters), T057 (As a student in a track with several subjects, I get a daily plan that splits time across subjects by exam weight and weakness), T108 (Run the closed pilot with 3 schools (≈ 2,000 students) and triage findings)

#### T131 · Release wave 2: Sciences and Sciences techniques

*Task · 5 pts · High · APL Sprint 19 · labels: release, sciences, technique*

Enable both subjects for all tenants whose tracks include them; hypercare; content hot-fix process with subject leads.

Acceptance criteria:

- Both subjects enabled with calibrated banks
- Load test re-run with 4-subject traffic shape passes SLOs
- Hypercare report delivered

Blocked by: T110 (Production go-live (Physics + Maths) and 30-day hypercare), T115 (Sciences (SVT / Chimie): build and tag the item bank incl. past Bac papers), T116 (Sciences (SVT / Chimie): ingest official textbooks into the RAG corpus and build glossary + misconception taxonomy), T118 (Sciences techniques: build and tag the item bank incl. past Bac papers), T119 (Sciences techniques: ingest official textbooks into the RAG corpus and build glossary + misconception taxonomy), T124 (As a sciences student, I explore chemistry and biology sims: titration, kinetics, molecular geometry, genetics crosses), T125 (As a sciences-techniques student, I build mechanisms and logic/automation schematics and simulate them), T128 (Calibrate Maths, Sciences, Technique and Éco/Gestion items on pilot cohorts)

#### T132 · Release wave 3: Économie & Gestion and full-track coverage review

*Task · 5 pts · High · APL Sprint 20 · labels: release, eco*

Enable éco/gestion; review every Bac track for subject coverage; publish the subject roadmap for the following year (philosophy, languages).

Acceptance criteria:

- Éco/gestion enabled with rubric verifier live
- Every supported track has all its coefficient-weighted subjects available
- Next-year subject roadmap approved

Blocked by: T131 (Release wave 2: Sciences and Sciences techniques), T121 (Économie & Gestion: build and tag the item bank incl. past Bac papers), T122 (Économie & Gestion: ingest official textbooks into the RAG corpus and build glossary + misconception taxonomy), T126 (As an éco/gestion student, I work in interactive financial statements, supply/demand and accounting-entry widgets), T127 (Calibrate the rubric verifier and tutor prompts for éco/gestion and descriptive sciences), T129 (Train and validate SAINT+ per subject (or shared with subject embedding) and gate per subject)


## 7. Importing the CSV into Jira

`APL_jira_import.csv` is built for Jira's **External System Import → CSV** (Settings → System → External System Import). It creates the 13 epics and 132 tickets in one pass with parent links, dependencies, labels, components and sprints.

1. Create the project first (key `APL`) and the components: Backend, Curriculum, Data, Frontend, LLM, ML, Platform, QA, Security. Create sprints named `APL Sprint 1` … `APL Sprint 20` on the board (or let the importer create them if your site allows it).
2. Upload the CSV. Field mapping:
   - `Issue ID` → Issue ID · `Issue Type` → Issue Type · `Summary` → Summary · `Description` → Description (wiki markup renders the h3./bullet structure)
   - `Priority` → Priority · `Story Points` → Story Points (or *Story point estimate* on team-managed projects)
   - **Company-managed projects:** `Epic Name` → Epic Name, `Epic Link` → Epic Link. **Team-managed projects:** `Parent` → Parent (ignore the two Epic columns).
   - `Components` → Component/s · `Sprint` → Sprint · `Fix Version` → Fix Version (phases) · `Team` → a custom "Team" field or ignore
   - Each `Labels` column → Labels (Jira merges repeated columns)
   - Each `Blocked By` column → Link type **"Blocks"** (choose the *is blocked by* direction; the importer resolves the IDs to the issues created in the same run)
3. Date format is not needed (no date columns). Encoding is UTF-8 with BOM so Arabic/French characters and `≥`/`→` survive Excel round-trips.
4. Dry-run on a sandbox project once: Jira will report any unmapped priority or issue-type names. `Spike` is not a default issue type — map it to Task if you don't have one.

After import, sort the board by Sprint and you have the 18-sprint plan loaded; the *Fix Version* field gives you a release-per-phase view in the roadmap.
