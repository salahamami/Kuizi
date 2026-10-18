"""Command line: kuizi-kc-graph migrate | validate | load | export (T032).

    uv run kuizi-kc-graph migrate
    uv run kuizi-kc-graph validate seed/physics_starter.yaml
    uv run kuizi-kc-graph load seed/physics_starter.yaml --replace
    uv run kuizi-kc-graph export --track sexp-4 --out out/sexp-4.json

The database is DATABASE_URL (environment, else the repository .env); the graph lives in
the schema given by --schema (default: curriculum).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import psycopg

from kuizi_kc_graph import db
from kuizi_kc_graph.export import ExportError, build_export, dumps, validate_export, write_export
from kuizi_kc_graph.seed import SeedError, load_seed


def _connect(args: argparse.Namespace) -> psycopg.Connection:
    url = args.database_url or db.database_url()
    args.redacted_url = db.redact(url)
    return db.connect(url, schema=args.schema)


def cmd_migrate(args: argparse.Namespace) -> int:
    with _connect(args) as conn:
        applied = db.migrate(conn, args.schema)
    if applied:
        print(f"schema {args.schema}: applied {', '.join(applied)}")
    else:
        print(f"schema {args.schema}: up to date")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    graph = load_seed(args.seed)
    print(f"ok: {args.seed}")
    print(graph.summary())
    return 0


def cmd_load(args: argparse.Namespace) -> int:
    graph = load_seed(args.seed)
    with _connect(args) as conn:
        db.load_graph(conn, graph, replace=args.replace)
    print(f"loaded {args.seed} into schema {args.schema}")
    print(graph.summary())
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    with _connect(args) as conn:
        graph = db.fetch_graph(conn)
    doc = build_export(graph, tracks=args.tracks, reviewed_only=args.reviewed_only)
    validate_export(doc)
    if args.out == "-":
        sys.stdout.write(dumps(doc))
    else:
        write_export(doc, Path(args.out))
        print(
            f"wrote {args.out}: {len(doc['tracks'])} track(s), {len(doc['kcs'])} KCs,"
            f" {len(doc['edges'])} edges, {doc['graph_hash']}",
            file=sys.stderr,
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kuizi-kc-graph",
        description="Kuizi knowledge-component graph: create the store, load a seed, export JSON.",
    )
    parser.add_argument(
        "--database-url",
        help="PostgreSQL URL (default: DATABASE_URL from the environment or the repository .env)",
    )
    parser.add_argument(
        "--schema",
        default=db.DEFAULT_SCHEMA,
        help=f"database schema that holds the graph (default: {db.DEFAULT_SCHEMA})",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    migrate = commands.add_parser("migrate", help="create the schema and apply the SQL migrations")
    migrate.set_defaults(handler=cmd_migrate)

    validate = commands.add_parser("validate", help="check a seed file without a database")
    validate.add_argument("seed", type=Path)
    validate.set_defaults(handler=cmd_validate)

    load = commands.add_parser("load", help="validate a seed file and write it to the database")
    load.add_argument("seed", type=Path)
    load.add_argument(
        "--replace", action="store_true", help="delete the graph already in the schema first"
    )
    load.set_defaults(handler=cmd_load)

    export = commands.add_parser("export", help="write the graph as JSON (export.schema.json)")
    export.add_argument(
        "--track",
        dest="tracks",
        action="append",
        metavar="TRACK",
        help="track to export, for example sexp-4 (repeat for several; default: every track)",
    )
    export.add_argument(
        "--reviewed-only",
        action="store_true",
        help="only teacher-reviewed KCs and edges (required for anything students see)",
    )
    export.add_argument("--out", default="-", help="output file (default: - for stdout)")
    export.set_defaults(handler=cmd_export)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    args.redacted_url = "DATABASE_URL"
    try:
        return args.handler(args)
    except (SeedError, ExportError, db.LoadError, db.SettingsError) as error:
        print(f"error: {error}", file=sys.stderr)
    except psycopg.OperationalError as error:
        where = args.redacted_url
        print(f"error: PostgreSQL at {where} failed (is `make up` running?): {error}", file=sys.stderr)
    except psycopg.Error as error:
        diag = error.diag
        lines = [diag.message_primary or str(error), diag.message_detail, diag.message_hint]
        print("error: " + "\n".join(line for line in lines if line), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
