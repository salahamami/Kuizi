# 0006. Local-first development, cloud before the pilot

- Status: Accepted
- Date: 2026-10-17

## Context

The backlog started with five sprints of AWS foundations (Terraform, VPC, EKS, Kong, Kafka on MSK, Aurora, Snowflake) before any product or brain work, which suits a large team that needs shared environments from day one. Kuizi is built by one product owner with role agents (ADR 0005), working on the product owner's PC. Nobody outside the project uses Kuizi before the closed pilot in Sprint 12 (T108), and the product owner wants to understand the brain early.

## Decision

- **Local stack first.** T237 (Sprint 1) runs every service Kuizi needs on one PC with Docker Compose: PostgreSQL with pgvector, Kafka (Redpanda), Redis, object storage (MinIO), Keycloak, MLflow and LiteLLM, plus a Python environment for the brain. Services read the same environment variable names the cloud will use.
- **Brain track early.** T238 (Sprint 1) walks the product owner through every Neural Core concept with notebooks on public data. The model benchmark (T040) runs on public datasets in Sprint 2, pyKT in Sprint 3, SAINT+ and the IRT cold start in Sprint 4. The re-run on Kuizi pilot data is T239, after the pilot.
- **Dependencies on cloud infrastructure are replaced by the local stack** where a ticket only needed somewhere to run (`LOCAL_FIRST_SWAPS` in `tools/backlog/additions.py`). Tickets that genuinely need the cloud keep their dependency: KMS keys (T151), the self-hosted model on GPU (T060), Kubeflow on EKS (T045), WAF, CDN and performance monitoring.
- **Cloud in Sprints 8 to 11.** The AWS foundations move to S8–S11, and T240 moves every locally built service to staging and production in S11. The pilot (S12) is blocked by T240.
- **The sprint plan is recomputed** by `tools/backlog/replan.py`: original order as priority, dependencies respected, a ramp of 13 / 40 / 65 / 80 / 95 points for S1–S5 then the 134-point ceiling, pilot fixed in S12 and everything from S18 unchanged.

## Consequences

- 144 tickets change sprint; four tickets are added (T237–T240). The backlog has 240 tickets and 1,636 points. S17 is left almost empty as a buffer before go-live.
- No cloud cost before Sprint 8, and the brain and the first screens arrive about three sprints earlier.
- Risk: something that works on the PC behaves differently on AWS. T237 keeps configuration names identical and T240 ends with an end-to-end smoke test a sprint before the pilot.
- Phase labels follow the sprint, so moved tickets change phase label (for example, the cloud tickets now carry `phase-2`).
