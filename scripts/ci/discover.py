#!/usr/bin/env python3
"""Find the projects CI checks, so a new project gets CI without editing a workflow (T006, ADR 0008).

Usage:
  python3 scripts/ci/discover.py                  # summary for people
  python3 scripts/ci/discover.py --github-output  # JSON lists for .github/workflows/ci.yml
  python3 scripts/ci/discover.py --list python    # one project per line, for the Makefile

What is found (files known to git, plus new files not ignored by .gitignore):
  Python projects   every folder holding a pyproject.toml.
                    Coverage gate: fail_under in its [tool.coverage.report], otherwise 80 (the
                    backend gate). Type check with mypy when it has a [tool.mypy] section.
                    Services for its tests: [tool.kuizi.ci] services = ["postgres"] starts the
                    local stack's PostgreSQL (pgvector) in CI and makes database tests mandatory.
  TypeScript        every folder matched by pnpm-workspace.yaml that holds a package.json.
  packages          Coverage gate: "kuizi": {"coverage": N} in its package.json, otherwise 70 under
                    apps/ (the frontend gate) and 80 elsewhere. Contract tests run when it has a
                    "test:contract" script.
  Container images  every file named Dockerfile; the image is named kuizi-<folder name> and is
                    published from main. Build context: the Dockerfile's folder, as in docker
                    compose; a Dockerfile that needs the whole repository (workspace packages,
                    root lockfile) says so on its own line: `# kuizi-ci: context=repo-root`.
                    Folders under .github/ci-fixtures/ hold CI's own test images: they are built
                    and scanned, never published.

Standard library only (system Python 3.12 on the CI runner, no PyYAML).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path, PurePosixPath

BACKEND_COVERAGE = 80
FRONTEND_COVERAGE = 70
FRONTEND_ROOT = "apps"
FIXTURES = ".github/ci-fixtures"
IMAGE_PREFIX = "kuizi-"
# Services a Python project can ask for in [tool.kuizi.ci] services (started by python.yml).
CI_SERVICES = {"postgres"}
# `# kuizi-ci: context=folder|repo-root` on its own line in a Dockerfile.
CONTEXT_DIRECTIVE = re.compile(r"#\s*kuizi-ci:\s*context\s*=\s*(\S*)")
CONTEXTS = ("folder", "repo-root")
SKIPPED_DIRS = {"node_modules", ".venv", "venv", "__pycache__", "dist", "build", "coverage"}


class DiscoveryError(Exception):
    """The repository layout breaks a CI rule; the message says how to fix it."""


def repo_files(root: Path) -> list[str]:
    """Tracked files and new files that .gitignore does not exclude, as POSIX paths."""
    run = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    files = []
    for path in sorted(set(filter(None, run.stdout.split("\0")))):
        parts = PurePosixPath(path).parts
        if any(part in SKIPPED_DIRS for part in parts) or not (root / path).is_file():
            continue
        files.append(path)
    return files


def folder_of(path: str) -> str:
    parent = PurePosixPath(path).parent.as_posix()
    return "." if parent in ("", ".") else parent


def slug(folder: str) -> str:
    """A name safe for artifacts and cache keys: curriculum/graph -> curriculum-graph."""
    return re.sub(r"[^a-z0-9._-]+", "-", folder.lower()).strip("-.")


def is_hidden(folder: str) -> bool:
    return folder != "." and any(part.startswith(".") for part in PurePosixPath(folder).parts)


def find_python(root: Path, files: list[str]) -> list[dict]:
    projects = []
    for path in files:
        if PurePosixPath(path).name != "pyproject.toml":
            continue
        folder = folder_of(path)
        if is_hidden(folder) or folder == ".":
            continue
        try:
            config = tomllib.loads((root / path).read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as error:
            raise DiscoveryError(f"{path} is not valid TOML: {error}") from None
        tool = config.get("tool", {})
        coverage = tool.get("coverage", {}).get("report", {}).get("fail_under", BACKEND_COVERAGE)
        if not isinstance(coverage, int | float) or not 0 <= coverage <= 100:
            raise DiscoveryError(f"{path}: [tool.coverage.report] fail_under must be a number from 0 to 100")
        services = tool.get("kuizi", {}).get("ci", {}).get("services", [])
        if not isinstance(services, list) or not set(services) <= CI_SERVICES:
            known = ", ".join(f'"{name}"' for name in sorted(CI_SERVICES))
            raise DiscoveryError(f"{path}: [tool.kuizi.ci] services must be a list drawn from {known}")
        projects.append(
            {
                "path": folder,
                "id": slug(folder),
                "coverage": coverage,
                "typecheck": "mypy" in tool or (root / folder / "mypy.ini").is_file(),
                "services": sorted(set(services)),
            }
        )
    return projects


def workspace_globs(root: Path) -> list[str]:
    """The `packages:` list of pnpm-workspace.yaml (a plain list of quoted or bare globs)."""
    path = root / "pnpm-workspace.yaml"
    if not path.is_file():
        return []
    globs, inside = [], False
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.split("#", 1)[0].rstrip()
        if not stripped:
            continue
        if not line[0].isspace():
            inside = stripped == "packages:"
            continue
        item = re.fullmatch(r"\s*-\s*(['\"]?)(.+?)\1\s*", stripped)
        if inside and item:
            globs.append(item.group(2))
    return globs


def glob_to_regex(pattern: str) -> re.Pattern[str]:
    """pnpm-style glob: `*` stays inside one folder, `**` crosses folders."""
    out, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out, i = out + "(?:.*/)?", i + 3
        elif pattern.startswith("**", i):
            out, i = out + ".*", i + 2
        elif pattern[i] == "*":
            out, i = out + "[^/]*", i + 1
        elif pattern[i] == "?":
            out, i = out + "[^/]", i + 1
        else:
            out, i = out + re.escape(pattern[i]), i + 1
    return re.compile(out.rstrip("/"))


def find_typescript(root: Path, files: list[str]) -> list[dict]:
    globs = workspace_globs(root)
    include = [glob_to_regex(g) for g in globs if not g.startswith("!")]
    exclude = [glob_to_regex(g[1:]) for g in globs if g.startswith("!")]
    packages = []
    for path in files:
        if PurePosixPath(path).name != "package.json":
            continue
        folder = folder_of(path)
        if not any(r.fullmatch(folder) for r in include) or any(r.fullmatch(folder) for r in exclude):
            continue
        try:
            manifest = json.loads((root / path).read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise DiscoveryError(f"{path} is not valid JSON: {error}") from None
        name = manifest.get("name")
        if not name:
            raise DiscoveryError(f"{path} has no name: pnpm --filter needs one")
        frontend = PurePosixPath(folder).parts[0] == FRONTEND_ROOT
        coverage = manifest.get("kuizi", {}).get("coverage", FRONTEND_COVERAGE if frontend else BACKEND_COVERAGE)
        if not isinstance(coverage, int | float) or not 0 <= coverage <= 100:
            raise DiscoveryError(f'{path}: "kuizi": {{"coverage": N}} must be a number from 0 to 100')
        packages.append(
            {
                "path": folder,
                "id": slug(folder),
                "name": name,
                "coverage": coverage,
                "contract": "test:contract" in manifest.get("scripts", {}),
            }
        )
    return packages


def build_context(root: Path, path: str, folder: str) -> str:
    """The Dockerfile's folder, or the repository root when the Dockerfile asks for it."""
    choices = []
    for line in (root / path).read_text(encoding="utf-8").splitlines():
        match = CONTEXT_DIRECTIVE.fullmatch(line.strip())
        if match:
            choices.append(match.group(1))
    if not choices:
        return folder
    if len(choices) > 1 or choices[0] not in CONTEXTS:
        found = ", ".join(f"context={c}" for c in choices)
        raise DiscoveryError(
            f"{path}: write one `# kuizi-ci: context=folder` or `context=repo-root` line (found {found})"
        )
    return "." if choices[0] == "repo-root" else folder


def find_containers(root: Path, files: list[str]) -> list[dict]:
    images, seen = [], {}
    for path in files:
        if PurePosixPath(path).name != "Dockerfile":
            continue
        folder = folder_of(path)
        fixture = folder.startswith(FIXTURES + "/")
        if is_hidden(folder) and not fixture:
            continue
        if folder == ".":
            raise DiscoveryError("Dockerfile at the repository root: move it into its app or service folder")
        base = ("ci-fixture-" if fixture else "") + PurePosixPath(folder).name
        name = IMAGE_PREFIX + slug(base)
        if name in seen:
            raise DiscoveryError(f"{path} and {seen[name]} would both build the image {name}: rename a folder")
        seen[name] = path
        images.append(
            {
                "name": name,
                "dockerfile": path,
                "context": build_context(root, path, folder),
                "publish": not fixture,
            }
        )
    return images


def discover(root: Path) -> dict[str, list[dict]]:
    files = repo_files(root)
    containers = find_containers(root, files)
    return {
        "python": find_python(root, files),
        "typescript": find_typescript(root, files),
        "containers": containers,
        "images": [image for image in containers if image["publish"]],
    }


def summary(found: dict[str, list[dict]]) -> str:
    lines = []
    for project in found["python"]:
        typecheck = "mypy" if project["typecheck"] else "no type check"
        services = "".join(f", with {name}" for name in project["services"])
        lines.append(f"python      {project['path']}  (coverage >= {project['coverage']}%, {typecheck}{services})")
    for package in found["typescript"]:
        contract = ", contract tests" if package["contract"] else ""
        lines.append(f"typescript  {package['path']}  {package['name']} (coverage >= {package['coverage']}%{contract})")
    for image in found["containers"]:
        target = "published from main" if image["publish"] else "built and scanned only"
        context = "repository root" if image["context"] == "." else "its folder"
        lines.append(f"container   {image['dockerfile']}  -> {image['name']} (context: {context}, {target})")
    return "\n".join(lines) or "nothing found"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Find the projects CI checks (docs/dev/ci.md).")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--github-output", action="store_true", help="write JSON lists to $GITHUB_OUTPUT")
    mode.add_argument("--list", choices=["python", "typescript"], help="one project per line (space separated)")
    args = parser.parse_args(argv)

    try:
        found = discover(args.root.resolve())
    except DiscoveryError as error:
        print(f"::error::{error}" if args.github_output else f"error: {error}", file=sys.stderr)
        return 1

    if args.list == "python":
        for p in found["python"]:
            print(p["path"], p["coverage"], str(p["typecheck"]).lower(), ",".join(p["services"]) or "-")
    elif args.list == "typescript":
        for p in found["typescript"]:
            print(p["path"], p["name"], p["coverage"], str(p["contract"]).lower())
    elif args.github_output:
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as out:
            for key, value in found.items():
                out.write(f"{key}={json.dumps(value, separators=(',', ':'))}\n")
        if os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as out:
                out.write(f"### Projects found by CI\n\n```\n{summary(found)}\n```\n")
        print(summary(found))
    else:
        print(summary(found))
    return 0


if __name__ == "__main__":
    sys.exit(main())
