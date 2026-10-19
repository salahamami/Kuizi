#!/usr/bin/env python3
"""Check that the Kuizi repository is consistent before handing work back (T234).

Usage: make check        (or: python3 scripts/check_repo.py [--root DIR])

Prints one ok/FAIL line per check and exits 1 if any check fails:
  1. The local stack's compose file is valid (docker compose config; Docker need not be running).
  2. Every agent brief in .claude/agents/ starts with front matter holding exactly name,
     description and tools, and name equals the file name without .md.
  3. Every agent-* label in docs/backlog/apl_backlog.json has a brief, and every brief
     owns at least one ticket.
  4. The backlog generator runs cleanly and the generated files in the repository match its
     output. It runs on a temporary copy of tools/backlog and docs/backlog, so this check
     never changes your files.
  5. Every third-party action in .github/workflows/ is pinned to a full commit SHA (a tag can be
     moved to other code; T006), and docker:// actions to an image digest.

Standard library only: system Python has no PyYAML, so the simple front matter is parsed by hand.
"""
import argparse
import filecmp
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

BRIEF_KEYS = ("name", "description", "tools")
GENERATOR = "tools/backlog/build_backlog.py"
GENERATOR_TREES = ("tools/backlog", "docs/backlog")  # everything the generator reads and writes


class CheckFailed(Exception):
    """A check found a problem; the message explains it, one problem per line."""


def tail(text, lines=10):
    return "\n".join(text.strip().splitlines()[-lines:])


def unquote(value):
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def check_compose(root):
    if shutil.which("docker") is None:
        raise CheckFailed("docker not found: install Docker (docs/dev/local-setup.md)")
    cmd = ["docker", "compose", "-f", "infra/local/compose.yaml", "--env-file", ".env.example", "config", "-q"]
    run = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=120)
    if run.returncode != 0:
        raise CheckFailed(tail(run.stderr or run.stdout) or f"{' '.join(cmd)} exited with {run.returncode}")
    return "infra/local/compose.yaml with .env.example"


def read_front_matter(path):
    """Return the top-level keys of a simple YAML front matter block as {key: raw value}."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("does not start with a '---' front matter line")
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise ValueError("front matter is not closed by a '---' line") from None
    fields, key = {}, None
    for number, line in enumerate(lines[1:end], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[0] in " \t":  # continuation of the previous value
            if key is None:
                raise ValueError(f"line {number}: indented line before any key")
            fields[key] = (fields[key] + " " + line.strip()).strip()
            continue
        match = re.fullmatch(r"([A-Za-z_][\w-]*):(?:\s+(.*))?", line)
        if not match:
            raise ValueError(f"line {number}: not a 'key: value' line")
        key = match.group(1)
        if key in fields:
            raise ValueError(f"line {number}: '{key}' appears twice")
        fields[key] = (match.group(2) or "").strip()
    return fields


def check_briefs(root):
    briefs = sorted((root / ".claude/agents").glob("*.md"))
    if not briefs:
        raise CheckFailed("no briefs found in .claude/agents/")
    problems = []
    for path in briefs:
        rel = path.relative_to(root)
        try:
            fields = read_front_matter(path)
        except ValueError as error:
            problems.append(f"{rel}: {error}")
            continue
        missing = [k for k in BRIEF_KEYS if k not in fields]
        extra = sorted(set(fields) - set(BRIEF_KEYS))
        empty = [k for k in BRIEF_KEYS if k in fields and not unquote(fields[k])]
        if missing:
            problems.append(f"{rel}: missing {', '.join(missing)}")
        if extra:
            problems.append(f"{rel}: unexpected {', '.join(extra)} (only name, description and tools)")
        if empty:
            problems.append(f"{rel}: empty {', '.join(empty)}")
        name = unquote(fields.get("name", ""))
        if name and name != path.stem:
            problems.append(f"{rel}: name is '{name}', expected '{path.stem}' (the file name)")
    if problems:
        raise CheckFailed("\n".join(problems))
    return f"{len(briefs)} briefs"


def check_labels(root):
    backlog = json.loads((root / "docs/backlog/apl_backlog.json").read_text(encoding="utf-8"))
    tickets = Counter()
    for item in backlog.get("epics", []) + backlog.get("issues", []):
        for label in item.get("labels", []):
            if label.startswith("agent-"):
                tickets[label[len("agent-"):]] += 1
    briefs = {path.stem for path in (root / ".claude/agents").glob("*.md")}
    problems = [f"label agent-{role} ({tickets[role]} tickets) has no brief .claude/agents/{role}.md"
                for role in sorted(set(tickets) - briefs)]
    problems += [f".claude/agents/{role}.md has no ticket labelled agent-{role}"
                 for role in sorted(briefs - set(tickets))]
    if problems:
        raise CheckFailed("\n".join(problems))
    return f"{len(tickets)} roles, {sum(tickets.values())} labelled tickets"


def files_under(base, trees):
    for tree in trees:
        for path in sorted((base / tree).rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                yield path.relative_to(base).as_posix()


def check_generator(root):
    with tempfile.TemporaryDirectory(prefix="kuizi-check-") as tmp:
        copy = Path(tmp)
        for tree in GENERATOR_TREES:
            shutil.copytree(root / tree, copy / tree, ignore=shutil.ignore_patterns("__pycache__"))
        run = subprocess.run([sys.executable, "-B", GENERATOR], cwd=copy, capture_output=True, text=True,
                             timeout=120)
        if run.returncode != 0:
            raise CheckFailed(f"python3 {GENERATOR} exited with {run.returncode}\n"
                              + tail(run.stderr or run.stdout))
        changed = [rel for rel in files_under(copy, GENERATOR_TREES)
                   if not (root / rel).is_file() or not filecmp.cmp(root / rel, copy / rel, shallow=False)]
        if changed:
            raise CheckFailed("generated files are out of date:\n" + "\n".join(changed)
                              + f"\nrun: python3 {GENERATOR}")
        totals = run.stdout.splitlines()[0] if run.stdout.strip() else "no output"
    return f"generated files up to date; {totals}"


def check_pinned_actions(root):
    workflows = sorted((root / ".github/workflows").glob("*.y*ml"))
    problems, count = [], 0
    for path in workflows:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            match = re.match(r"\s*(?:-\s+)?uses:\s*['\"]?([^\s'\"#]+)", line)
            if not match or match.group(1).startswith("./"):
                continue  # local actions and reusable workflows live in this repository
            ref = match.group(1)
            count += 1
            if ref.startswith("docker://"):
                pinned = re.search(r"@sha256:[0-9a-f]{64}$", ref)
            else:
                pinned = re.fullmatch(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}", ref)
            if not pinned:
                problems.append(f"{path.relative_to(root)}:{number}: {ref} is not pinned to a full commit SHA "
                                "(or image digest); keep the version as a comment, e.g. @<sha> # v1.2.3")
    if problems:
        raise CheckFailed("\n".join(problems))
    return f"{count} third-party action references in {len(workflows)} workflows"


CHECKS = [
    ("Local stack compose file is valid", check_compose),
    ("Agent briefs have name, description and tools; name matches the file", check_briefs),
    ("Every agent-* label has a brief and every brief owns tickets", check_labels),
    ("Backlog generator runs cleanly", check_generator),
    ("Workflow actions are pinned to a commit SHA", check_pinned_actions),
]


def main():
    parser = argparse.ArgumentParser(description="Check that the Kuizi repository is consistent.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="repository to check (default: this repository)")
    root = parser.parse_args().root.resolve()

    print("Kuizi repository check")
    failures = 0
    for name, check in CHECKS:
        try:
            detail = check(root)
            print(f"  ok    {name} ({detail})")
        except Exception as error:  # every problem becomes a FAIL line, never a traceback
            message = str(error) if isinstance(error, CheckFailed) else f"{type(error).__name__}: {error}"
            print(f"  FAIL  {name}")
            print("\n".join(f"        {line}" for line in message.splitlines()))
            failures += 1

    print()
    if failures:
        print(f"{failures} check(s) failed.")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
