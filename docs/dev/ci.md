# Continuous integration (CI)

Every push and every pull request runs the checks below on GitHub Actions (T006). A pull request can merge only when the check **CI result** is green, once the product owner has protected `main` ([below](#protect-main-product-owner-once)). The workflows live in [`.github/workflows/`](../../.github/workflows/); the layout and toolchains they check come from [ADR 0008](../architecture/decisions/0008-monorepo-layout-and-toolchains.md).

## What runs

| Check (as GitHub shows it) | What it does | When |
| --- | --- | --- |
| Discover projects | Finds the Python projects, TypeScript packages and Dockerfiles ([`scripts/ci/discover.py`](../../scripts/ci/discover.py)) | Always |
| Repository checks | `make check` (compose file, agent briefs, backlog, actions pinned to commit SHAs), tests of the CI scripts, Ruff on Python outside the projects, `pnpm install --frozen-lockfile` and Prettier, actionlint with shellcheck on the workflows | Always |
| Python / `<folder>` | Ruff lint and format check, `uv sync --locked`, PostgreSQL if the project asks for it, mypy if the project opts in, pytest with the project's coverage gate | One job per Python project |
| TypeScript / `<folder>` | `lint`, `typecheck`, Vitest with the coverage gate, `test:contract` if the package has it, `build` | One job per workspace package; skipped while there is none |
| Containers / `<image>` | Build with Buildx, Syft SBOM, Trivy scan that fails on any CRITICAL finding. Nothing is pushed | Branches and pull requests |
| Containers (publish) / `<image>` | The same, then push to GHCR, sign with cosign and attach the SBOM as a signed attestation | `main` only, after every other check passed |
| **CI result** | Fails if any job above failed or was cancelled; skipped jobs (nothing to check) are fine | Always: **the only required check** |

Triggers: every push to any branch (agents get feedback before a pull request exists), every pull request to `main` (tests the merge result) and a manual run (*Actions → CI → Run workflow*). A newer push to the same branch cancels the older run; runs on `main` always finish.

Each job writes a summary on the run page (coverage table, image findings) and keeps its reports as artifacts for 14 to 30 days: `coverage.xml` and `junit.xml` for Python, the coverage folder and pact files for TypeScript, `<image>.spdx.json` (SBOM) and `<image>-trivy-report` for images.

## How a new project gets CI

Nothing to edit in the workflows: discovery reads the repository on every run.

**Python project** (a folder with a `pyproject.toml`, for example `schemas/events` or `curriculum/graph`):

- Commit `uv.lock` next to `pyproject.toml` (`uv lock`); CI runs `uv sync --locked`, which fails if the lockfile is stale.
- Add the test tools to a dev group: `uv add --dev pytest pytest-cov` (and `mypy` if the code is typed). Put tests in `tests/`; CI fails when a project has no test.
- Set the coverage gate, if not 80 %, in `pyproject.toml`: `[tool.coverage.report]` `fail_under = 90`. Also set `[tool.coverage.run]` `source = ["your_package"]`.
- Type checks: add a `[tool.mypy]` section with `files = [...]` (and `strict = true` for new code); CI then runs `uv run mypy`.
- Tests that need PostgreSQL: add the lines below. CI then starts the local stack's image (`pgvector/pgvector:pg16`, pinned by digest, with the `vector` and `ltree` extensions available) before the tests and sets `DATABASE_URL=postgresql://kuizi:kuizi-ci-only@127.0.0.1:5432/kuizi` and `KUIZI_REQUIRE_POSTGRES=1`. Write the tests so that this flag turns a missing database into a failure instead of a skip (as `curriculum/graph/tests/conftest.py` does), and give each test its own schema so runs never collide. `make test` sets the same flag and uses `DATABASE_URL` from `.env`, so start the local stack first (`make up`).

  ```toml
  [tool.kuizi.ci]
  services = ["postgres"]
  ```

  PostgreSQL is the only service so far; a project asking for an unknown one fails discovery. Another service (for example the Kafka schema registry for T023's live tests) is added in `scripts/ci/discover.py` (`CI_SERVICES`) and `.github/workflows/python.yml`.
- Ruff settings come from the root [`ruff.toml`](../../ruff.toml). Do not add `[tool.ruff]` to a project: it would replace the shared settings. If a project really needs a different rule, start its `[tool.ruff]` with `extend = "../../ruff.toml"` (the path from the project to the root) and say why in the pull request.

**TypeScript package** (a folder under `apps/`, `services/` or `packages/` with a `package.json`):

- A `name` and the four scripts `lint`, `typecheck`, `test` (Vitest) and `build`, as in ADR 0008. CI runs them with `pnpm --filter <name>`, after building the workspace packages it depends on.
- `pnpm install` at the root updates `pnpm-lock.yaml`; commit it (CI installs with `--frozen-lockfile`).
- Coverage gate: 80 % of lines, 70 % under `apps/`. To change it: `"kuizi": { "coverage": 85 }` in the package's `package.json`.
- Contract tests: a `test:contract` script (see [below](#contract-tests-pact)).

**Container image**: a file named `Dockerfile` in the app or service folder.

- The image is `ghcr.io/salahamami/kuizi-<folder name>` (two folders with the same name are refused).
- **Build context**: the Dockerfile's own folder, as in `docker compose` (`build: ../../services/keycloak`), so `COPY themes/ ...` means `services/keycloak/themes/`, and a `.dockerignore` in that folder applies.
- A Dockerfile that needs the whole repository (a TypeScript service that copies workspace packages and `pnpm-lock.yaml`, for example) opts in with one line anywhere in the Dockerfile: `# kuizi-ci: context=repo-root`. Its `COPY` paths then start at the root (`COPY services/routing/...`), and its ignore file is `Dockerfile.dockerignore` next to the Dockerfile. Use the same context in compose (`build: {context: ../.., dockerfile: services/routing/Dockerfile}`). Any other value, or two such lines, fails discovery.
- Branches and pull requests: build, SBOM and scan only. `main`: also published, tagged `sha-<12 characters of the commit>` and `main`.

## Coverage gates

| Project | Gate | Where it is set |
| --- | --- | --- |
| Backend services and shared packages (`services/`, `packages/`, Python projects by default) | 80 % | Default in `scripts/ci/discover.py` |
| Frontend apps (`apps/`) | 70 % of lines | Default in `scripts/ci/discover.py` |
| Brain library (`ml/kuizi_brain`) | 75 % (measured 98 % on 2026-10-18) | `ml/pyproject.toml`, `fail_under` |

Why the brain library has its own gate: `kuizi_brain` is teaching and research code (T238, T040–T043) that grows through experiments run from notebooks; its plotting and dataset download are exercised there, not in unit tests. The gate is set to stop the library from growing without tests rather than to tax every experiment: at today's size, adding an untested module about a third as big as the library breaks it. The decisions the library feeds are guarded separately: the T040 benchmark's fairness checks run as tests on every pull request, and production versions of these models are rebuilt as services with the 80 % gate. Raise it once the library settles (after T042).

Lowering any gate weakens a quality check and needs the product owner's approval in the pull request.

## Contract tests (Pact)

There is nothing to test yet; the convention is ready for T103 and T214.

- A TypeScript package that has a `test:contract` script gets a "Contract tests" step after its unit tests. Consumer tests write pact files to `<package>/pacts/`; CI keeps them as artifacts.
- Python projects run their contract tests (pact-python) inside the normal pytest suite.
- The Pact Broker and provider verification against published pacts come with T103; until then the pact files in the artifacts are the record.

## Container images: SBOM, scan, signature

1. **Build**: Buildx with a layer cache per image; the image is loaded into the runner, not pushed.
2. **SBOM**: Syft v1.54.0 writes an SPDX JSON file, kept as an artifact.
3. **Scan**: Trivy v0.70.0 keeps a full report, then the gate reads that report and fails the job on any **CRITICAL** vulnerability (fixed or not) or CRITICAL secret baked into the image. HIGH findings are shown but do not fail the job. A CRITICAL finding that cannot be fixed by a newer base image goes in a `.trivyignore` file at the root, one CVE per line with a comment (reason, link, review date), and needs the product owner's approval in the pull request.
4. **Publish** (`main` only, after every other check passed): push the exact image that was scanned, sign its digest with cosign v3 **keyless** (the workflow's GitHub OIDC identity, no key to store), attach the SBOM as a signed SPDX attestation, then verify both.

Check an image yourself:

```bash
cosign verify ghcr.io/salahamami/kuizi-<name>@sha256:<digest> \
  --certificate-identity https://github.com/salahamami/Kuizi/.github/workflows/container.yml@refs/heads/main \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
cosign verify-attestation --type spdxjson ghcr.io/salahamami/kuizi-<name>@sha256:<digest> \
  --certificate-identity https://github.com/salahamami/Kuizi/.github/workflows/container.yml@refs/heads/main \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
```

The identity is the signing workflow on `main` and is case-sensitive: it follows the repository's current name, `salahamami/Kuizi`.

A CI fixture in [`.github/ci-fixtures/container/`](../../.github/ci-fixtures/container/) (distroless, pinned by digest) is built and scanned on every branch so the workflow stays proven before the first service has a Dockerfile; it is never pushed. The publish path runs for the first time when a real service Dockerfile reaches `main`: watch that run.

**Cost**: none today. Standard GitHub-hosted runners are free for a public repository, and nothing is published until a service has a Dockerfile. GHCR storage is free for public images; a private image counts against the account's free package storage (500 MB on the Free plan). After the first publish, the package appears under the account's *Packages*, linked to this repository by the `org.opencontainers.image.source` label; its visibility is the product owner's choice.

**After the cloud move (T240)**: images go to Amazon ECR. The workflow takes a `registry` input; T240 replaces the GHCR login with `aws-actions/configure-aws-credentials` (an IAM role trusted through GitHub OIDC, no stored keys) and `aws-actions/amazon-ecr-login`. Signing and attestations work the same on ECR, and the cluster can then refuse unsigned images (admission policy, a later ticket).

## Run the same checks on your PC

| Command | What it runs |
| --- | --- |
| `make lint` | Ruff lint and format check (whole repository), mypy for projects that opt in, then with pnpm installed: frozen-lockfile install, Prettier, ESLint and tsc for each package |
| `make test` | Tests of the CI scripts, pytest with each Python project's coverage gate, Vitest with each package's gate, contract tests |
| `make check` | Repository consistency, including the rule that workflow actions are pinned to commit SHAs |

They use the same tool versions as CI (Ruff from `ruff.toml`, uv, pnpm from `package.json`). Container images are not built locally by these commands; to scan one yourself, install [Trivy](https://trivy.dev/) and run `trivy image --severity CRITICAL <image>`.

## Caches

| Cache | Key |
| --- | --- |
| uv packages and Python, per project | `uv.lock` of the project |
| pnpm store | `pnpm-lock.yaml` |
| Docker layers, per image | Buildx GitHub Actions cache, scope = image name |
| Trivy vulnerability database | the day (refreshed daily) |

## How the pipeline protects itself

- Every third-party action is pinned to a full commit SHA with its version in a comment, and `make check` fails on an unpinned one. Tools are pinned too: uv 0.11.32, Ruff 0.16.8, Syft v1.54.0, Trivy v0.70.0, cosign v3.0.6 (through `sigstore/cosign-installer` v4.1.2) and actionlint 1.7.12 (checked against its SHA-256).
- Pinning matters because a tag can be moved to other code; that is how Aqua's Trivy actions were attacked in 2026. The pinned `aquasecurity/setup-trivy` v0.3.1 is a June 2026 release made after the clean-up (its code was read before pinning), and CI runs the Trivy CLI itself so the gate is visible in the workflow.
- Every job declares its own `permissions`; the default is none. Only the `main` publish job can write packages and request an OIDC token.
- Checkouts do not keep the token (`persist-credentials: false`); values from discovery reach shell scripts through environment variables, never pasted into them. actionlint, shellcheck and [zizmor](https://docs.zizmor.sh/) report no finding on the workflows (zizmor: 4 low "self-repository" style hints).
- To update a pinned action: take the release's commit SHA from the action's repository (`git ls-remote --tags https://github.com/<owner>/<action>`), read its changelog, and update the SHA and the version comment together. Automated update pull requests come with T215.

## Protect `main` (product owner, once)

Agents cannot change repository settings, so this step makes acceptance criterion 1 of T006 ("a PR cannot merge with a failing check or a Critical CVE in the image") true on GitHub. It extends the protection described in the [working agreement](../process/working-agreement.md#branches-commits-and-pull-requests).

1. On GitHub, open the repository, then **Settings → Rules → Rulesets → New ruleset → New branch ruleset**.
2. **Ruleset name**: `main`. **Enforcement status**: *Active*. Leave the **Bypass list** empty.
3. **Target branches → Add target → Include default branch**.
4. Tick **Restrict deletions** and **Block force pushes**.
5. Tick **Require a pull request before merging** (required approvals: 0 for now, see the working agreement).
6. Tick **Require status checks to pass**, then **Add checks**, type `CI result` and pick it (source *GitHub Actions*). Also tick **Require branches to be up to date before merging**.
7. **Create**.

The check list only offers names that ran in the last week; `CI result` has been running on the `feat/t006-ci` branch since 2026-10-18. Require **only** `CI result`: it already fails when any other job fails, and the names of the other jobs change as projects are added.

If you prefer the classic screen: **Settings → Branches → Add classic branch protection rule**, branch name pattern `main`, tick *Require a pull request before merging*, *Require status checks to pass before merging* (search `CI result`, tick *Require branches to be up to date*), and *Do not allow bypassing the above settings*.

## Measured duration

Wall-clock time of the whole CI run on GitHub-hosted runners (`ubuntu-24.04`), from the run's creation to its end. Jobs run in parallel.

| Run | Commit | What it checked | Result | Duration |
| --- | --- | --- | --- | --- |
| [39169540642](https://github.com/salahamami/Kuizi/actions/runs/39169540642) | `8873939` | First run, empty caches: `ml/` and the fixture image | passed | 1 min 11 s |
| [39169721233](https://github.com/salahamami/Kuizi/actions/runs/39169721233) | `f4cdbc0` | The same with warm caches | passed | 50 s |
| [39169819736](https://github.com/salahamami/Kuizi/actions/runs/39169819736) | `faaf061` | Plus a temporary TypeScript service with a Dockerfile (canary, reverted) | passed | 1 min 1 s |
| [39169941697](https://github.com/salahamami/Kuizi/actions/runs/39169941697) | `a752721` | Negative test: a Ruff error, coverage under the gate, a CRITICAL CVE (reverted) | failed, as intended | 58 s |

Median of the passing runs: **about 1 minute**, against the 8-minute target for a backend service (T006, criterion 2). The longest jobs are Python / ml (33 to 48 s, it installs PyTorch), a service image (47 s: build, SBOM, scan) and a TypeScript service (17 s). In the negative test each fault failed its own job (`F401` in Ruff; "Coverage for lines (20%) does not meet global threshold (80%)"; "Total: 4 (CRITICAL: 4)") and **CI result** failed.
