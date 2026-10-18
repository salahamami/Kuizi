"""Command line: `uv run kuizi-schemas <command>` from schemas/, or the make targets at the root.

check     every offline check: schemas, house rules, catalogue, examples, generated page, compatibility
docs      regenerate docs/data/event-catalogue.md
compat    only the compatibility check against the git history
register  register every event schema in the schema registry (SCHEMA_REGISTRY_URL)
expand    write the self-contained schemas, one file per subject (for code generators, T024)
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from pathlib import Path

from . import Paths
from .avsc import SchemaError, Sources, load_sources, to_registry_string
from .catalogue import Catalogue, CatalogueError, check_catalogue, load_catalogue
from .compat import GitError, Version, check_against_history, check_subject
from .docs import doc_is_current, write_doc
from .examples import check_all_examples
from .lint import lint_all
from .registry import IncompatibleSchema, Registry, RegistryError, registry_url


class Failed(Exception):
    """A check found problems; one per line."""


def load(paths: Paths) -> tuple[Catalogue, Sources]:
    try:
        return load_catalogue(paths.catalogue), load_sources(paths.events)
    except (CatalogueError, SchemaError) as error:
        raise Failed(str(error)) from None


def run_checks(checks: list[tuple[str, Callable[[], str]]]) -> int:
    failures = 0
    for name, check in checks:
        try:
            detail = check()
            print(f"  ok    {name}{f' ({detail})' if detail else ''}")
        except Failed as error:
            failures += 1
            print(f"  FAIL  {name}")
            for line in str(error).splitlines():
                print(f"        {line}")
    print()
    print("All checks passed." if not failures else f"{failures} check(s) failed.")
    return 1 if failures else 0


def compat_check(paths: Paths, level: str, ref: str, require_history: bool) -> str:
    try:
        report = check_against_history(paths, level, ref)
    except GitError as error:
        raise Failed(f"cannot read the git history: {error}") from None
    if require_history and any("shallow" in n for n in report.notes):
        raise Failed("\n".join(report.notes))
    if report.problems:
        raise Failed("\n".join(report.problems + report.notes))
    note = f"; {'; '.join(report.notes)}" if report.notes else ""
    return f"{level}: {report.checked} subjects against {report.versions} committed versions from {ref}{note}"


def cmd_check(args: argparse.Namespace, paths: Paths) -> int:
    print("Kuizi event schemas check")
    state: dict = {}

    def schemas() -> str:
        state["catalogue"], state["sources"] = load(paths)
        problems = lint_all(state["sources"], state["catalogue"])
        if problems:
            raise Failed("\n".join(problems))
        return f"{len(state['sources'].events)} events, {len(state['sources'].common)} shared types"

    def needs_sources() -> tuple[Catalogue, Sources]:
        if "sources" not in state:
            raise Failed("skipped: the schemas do not load")
        return state["catalogue"], state["sources"]

    def catalogue() -> str:
        cat, sources = needs_sources()
        problems = check_catalogue(cat, sources, paths)
        if problems:
            raise Failed("\n".join(problems))
        return f"{len(cat.events)} entries, {len(cat.ml_features)} model inputs mapped"

    def examples() -> str:
        cat, sources = needs_sources()
        problems = check_all_examples(cat, sources, paths)
        if problems:
            raise Failed("\n".join(problems))
        return "every event has synthetic examples that match its schema and rules"

    def docs() -> str:
        cat, sources = needs_sources()
        if not doc_is_current(paths, cat, sources):
            raise Failed(f"{Paths.DOC_REL} is out of date: run make schemas-docs")
        return Paths.DOC_REL

    def compat() -> str:
        cat, _ = needs_sources()
        if args.no_git:
            return "skipped (--no-git)"
        return compat_check(paths, args.level or cat.compatibility, args.against, args.require_full_history)

    return run_checks(
        [
            ("Schemas parse and follow the house rules", schemas),
            ("Catalogue and schemas match", catalogue),
            ("Example events are valid and synthetic", examples),
            ("Generated catalogue page is up to date", docs),
            ("Schemas stay compatible with the committed versions", compat),
        ]
    )


def cmd_docs(args: argparse.Namespace, paths: Paths) -> int:
    catalogue, sources = load(paths)
    problems = check_catalogue(catalogue, sources, paths)
    if problems:
        print("Fix the catalogue first:\n" + "\n".join(f"  {p}" for p in problems))
        return 1
    changed = write_doc(paths, catalogue, sources)
    print(f"{Paths.DOC_REL} {'written' if changed else 'already up to date'}")
    return 0


def cmd_compat(args: argparse.Namespace, paths: Paths) -> int:
    catalogue, _ = load(paths)
    level = args.level or catalogue.compatibility
    print("Kuizi event schemas compatibility")
    return run_checks(
        [
            (
                "Schemas stay compatible with the committed versions",
                lambda: compat_check(paths, level, args.against, args.require_full_history),
            )
        ]
    )


def cmd_register(args: argparse.Namespace, paths: Paths) -> int:
    catalogue, sources = load(paths)
    problems = lint_all(sources, catalogue) + check_catalogue(catalogue, sources, paths)
    if problems:
        print("Refusing to register: run make schemas-check\n" + "\n".join(f"  {p}" for p in problems))
        return 1
    registry = Registry(args.url or registry_url(paths.env_file))
    level = catalogue.compatibility
    print(f"Schema registry {registry.url} · compatibility {level}")
    plan = []
    refused = []
    for name, event in sorted(catalogue.events.items()):
        subject = args.subject_prefix + event.subject
        schema = to_registry_string(sources.expanded(name))
        existing = registry.lookup(subject, schema)
        if existing:
            plan.append((subject, schema, f"unchanged, version {existing['version']} (id {existing['id']})"))
            continue
        versions = registry.versions(subject)
        if versions:
            # The registry checks at the subject's current level, which may still be the global default;
            # the offline check adds the catalogue's level against every registered version.
            ok, messages = registry.check(subject, schema)
            registered = [Version(str(v), json.loads(registry.get_version(subject, v)["schema"])) for v in versions]
            messages += check_subject(subject, sources.expanded(name), registered, level)
            if not ok or messages:
                refused.append(f"{subject}: " + " ".join(messages))
                continue
        plan.append((subject, schema, None))
    if refused:
        print("Incompatible with the registered versions; nothing was registered:")
        for line in refused:
            print(f"  {line}")
        return 1
    for subject, schema, status in plan:
        if status is None and args.dry_run:
            status = "would register a new version"
        elif status is None:
            if registry.compatibility_level(subject) != level:
                registry.set_compatibility(subject, level)
            try:
                schema_id = registry.register(subject, schema)
            except IncompatibleSchema as error:
                print(f"  FAIL  {subject}: {error}")
                return 1
            version = registry.lookup(subject, schema)
            status = f"registered version {version['version'] if version else '?'} (id {schema_id})"
        elif not args.dry_run and registry.compatibility_level(subject) != level:
            registry.set_compatibility(subject, level)
        print(f"  ok    {subject}: {status}")
    return 0


def cmd_expand(args: argparse.Namespace, paths: Paths) -> int:
    catalogue, sources = load(paths)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, event in sorted(catalogue.events.items()):
        target = out / f"{event.subject}.avsc"
        target.write_text(json.dumps(sources.expanded(name), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(target)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="kuizi-schemas", description="Kuizi event contracts (T023).")
    parser.add_argument("--root", type=Path, help="repository root (default: this repository)")
    sub = parser.add_subparsers(dest="command", required=True)

    def history_options(p: argparse.ArgumentParser) -> None:
        p.add_argument("--against", default="HEAD", help="git reference whose history is compared (default HEAD)")
        p.add_argument("--level", help="compatibility level (default: the catalogue's)")
        p.add_argument(
            "--require-full-history",
            action="store_true",
            help="fail in a shallow clone (use in CI with fetch-depth: 0)",
        )

    p = sub.add_parser("check", help="run every offline check")
    history_options(p)
    p.add_argument("--no-git", action="store_true", help="skip the compatibility check (no git history)")
    sub.add_parser("docs", help="regenerate docs/data/event-catalogue.md")
    history_options(sub.add_parser("compat", help="compatibility against the committed versions only"))
    p = sub.add_parser("register", help="register the schemas in the schema registry")
    p.add_argument("--url", help="registry URL (default: SCHEMA_REGISTRY_URL from the environment or .env)")
    p.add_argument("--dry-run", action="store_true", help="check compatibility with the registry, register nothing")
    p.add_argument("--subject-prefix", default="", help="prefix every subject (tests and throwaway environments)")
    p = sub.add_parser("expand", help="write self-contained schemas, one per subject")
    p.add_argument("--out", required=True, help="output folder")

    args = parser.parse_args(argv)
    paths = Paths(args.root)
    commands = {
        "check": cmd_check,
        "docs": cmd_docs,
        "compat": cmd_compat,
        "register": cmd_register,
        "expand": cmd_expand,
    }
    try:
        return commands[args.command](args, paths)
    except Failed as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except RegistryError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
