# 0008. Monorepo layout and toolchains

- Status: Proposed (agents follow it from Sprint 2; the product owner accepts it by merging the Sprint 2 pull request)
- Date: 2026-10-18

## Context

Sprint 2 brings the first code beyond the brain notebooks: the CI pipeline (T006), identity (T012), event schemas (T023), the concept-graph store (T032) and the brand assets (T231). Several role agents work on the repository in parallel (ADR 0005), so they need one agreed place for each kind of code and one toolchain per language. Without that, every agent would invent its own layout and CI would have to learn each one.

## Decision

**One repository** holds every app, service, library, schema, model and document.

| Folder | Holds | Example |
| --- | --- | --- |
| `apps/` | User-facing apps | `apps/web` (Next.js), later `apps/ios`, `apps/android` |
| `services/` | Deployable back-end services, one folder each | `services/routing`, `services/tutor` |
| `packages/` | Shared TypeScript libraries, published only inside the workspace | `packages/auth` (token checks), `packages/events` (generated event types) |
| `ml/` | The brain: Python, notebooks, benchmarks (existing) | `ml/kuizi_brain` |
| `schemas/` | Contracts shared across languages: event schemas (Avro), later OpenAPI | `schemas/events/` |
| `curriculum/` | Curriculum data and its store: knowledge-component graph, later item bank tooling | `curriculum/graph/` |
| `brand/` | Brand source files (SVG) and exported assets | `brand/logo/`, `brand/app-icon/` |
| `infra/` | Local stack (existing), later Terraform and Kubernetes manifests | `infra/local/` |
| `tools/`, `scripts/` | Developer tooling and repository scripts (existing) | `tools/backlog/` |
| `docs/` | Documentation in English | |

**TypeScript** (apps, services, packages)
- Node.js 22 LTS, pnpm workspaces (`pnpm-workspace.yaml` lists `apps/*`, `services/*`, `packages/*`), version pinned in the root `package.json` (`packageManager`).
- TypeScript in strict mode, ES modules, a shared `tsconfig.base.json` at the root.
- ESLint (flat config with typescript-eslint) and Prettier; Vitest for unit tests with V8 coverage.
- Every package has the scripts `lint`, `typecheck`, `test` and `build`, so CI runs them the same way everywhere.

**Python** (brain, data and curriculum tooling, services written in Python)
- Python 3.12, one uv project per folder (`pyproject.toml` and `uv.lock` committed).
- Ruff for linting and formatting (one `ruff.toml` at the root), pytest with pytest-cov for tests, mypy for type checks where the code is typed.

**Shared rules**
- Lockfiles are committed; CI caches are keyed on them.
- Services read the same environment variable names locally and in the cloud (ADR 0006); new names go into `.env.example`.
- Database changes are plain SQL migrations kept next to the code that owns them, numbered `NNN_description.sql`.

## Consequences

- CI (T006) discovers TypeScript packages from the pnpm workspace and Python projects from their `pyproject.toml`, so a new service gets lint, tests and coverage without changing CI.
- Agents know where to put new code without asking; a new top-level folder needs an update to this ADR.
- Mobile apps (E16) keep their native toolchains (Xcode, Gradle) inside `apps/ios` and `apps/android`; their CI is added by their tickets.
