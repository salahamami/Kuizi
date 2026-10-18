#!/usr/bin/env bash
# Run the CI lint and test commands on your PC, on every project scripts/ci/discover.py finds
# (T006). Same commands, versions and coverage gates as .github/workflows/*.yml.
#
#   make lint   ->  scripts/ci/run-checks.sh lint   Ruff, mypy (projects that opt in), Prettier, ESLint, tsc
#   make test   ->  scripts/ci/run-checks.sh test   pytest and Vitest with each project's coverage gate
#
# Container images are not built here: CI builds, scans and (on main) signs them (docs/dev/ci.md).
set -euo pipefail
cd "$(dirname "$0")/../.."

need() {
  command -v "$1" > /dev/null || { echo "error: $1 is needed ($2)" >&2; exit 1; }
}

need python3 "see docs/dev/local-setup.md"
python_projects="$(python3 scripts/ci/discover.py --list python)"
ts_packages="$(python3 scripts/ci/discover.py --list typescript)"

run_lint() {
  need uv "see docs/dev/local-setup.md"
  local ruff_version
  ruff_version="$(sed -n 's/^required-version = "==\(.*\)"$/\1/p' ruff.toml)"
  echo "== Ruff ${ruff_version}: lint and format check"
  uvx "ruff@${ruff_version}" check .
  uvx "ruff@${ruff_version}" format --check .
  while read -r path _coverage typecheck; do
    [ -n "$path" ] && [ "$typecheck" = true ] || continue
    echo "== mypy: ${path}"
    (cd "$path" && uv run --locked mypy)
  done <<< "$python_projects"

  if [ -z "$ts_packages" ]; then
    echo "== No TypeScript package yet: Prettier, ESLint and tsc skipped"
    return
  fi
  need pnpm "Node.js 22, then: corepack enable"
  pnpm install --frozen-lockfile
  echo "== Prettier"
  pnpm run format:check
  while read -r _path name _coverage _contract; do
    echo "== ESLint and tsc: ${name}"
    pnpm --filter "${name}^..." run --if-present build
    pnpm --filter "$name" run lint
    pnpm --filter "$name" run typecheck
  done <<< "$ts_packages"
}

run_tests() {
  need uv "see docs/dev/local-setup.md"
  echo "== CI scripts"
  python3 -m unittest discover -s scripts/ci
  while read -r path coverage _typecheck; do
    [ -n "$path" ] || continue
    echo "== pytest: ${path} (coverage gate ${coverage} %)"
    (cd "$path" && uv run --locked pytest --cov --cov-fail-under="$coverage")
  done <<< "$python_projects"

  if [ -z "$ts_packages" ]; then
    echo "== No TypeScript package yet: Vitest skipped"
    return
  fi
  need pnpm "Node.js 22, then: corepack enable"
  pnpm install --frozen-lockfile
  while read -r _path name coverage contract; do
    echo "== Vitest: ${name} (coverage gate ${coverage} % of lines)"
    pnpm --filter "${name}^..." run --if-present build
    pnpm --filter "$name" run test --coverage.enabled --coverage.thresholds.lines="$coverage"
    if [ "$contract" = true ]; then
      echo "== Contract tests: ${name}"
      pnpm --filter "$name" run test:contract
    fi
  done <<< "$ts_packages"
}

case "${1:-}" in
  lint) run_lint ;;
  test) run_tests ;;
  *) echo "usage: $0 lint|test" >&2; exit 2 ;;
esac
echo "All ${1} checks passed."
