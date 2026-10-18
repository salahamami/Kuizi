"""PostgreSQL access: settings, connections, migrations, loading a graph and reading it back.

Settings follow ADR 0006: DATABASE_URL from the environment, else from the repository's
.env (created by `make up` from .env.example). The graph lives in its own schema
(default `curriculum`); tests use throwaway schemas so they never touch real data.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import psycopg
from psycopg import sql

from kuizi_kc_graph import MIGRATIONS_DIR
from kuizi_kc_graph.model import KC, Chapter, Edge, Graph, Membership, Programme, Subject, Track

DEFAULT_SCHEMA = "curriculum"
SCHEMA_NAME = re.compile(r"^[a-z_][a-z0-9_]{0,62}$")
MIGRATION_FILE = re.compile(r"^\d{3}_[a-z0-9_]+\.sql$")
GRAPH_TABLES = ("kc_edge", "kc_track", "kc", "chapter", "programme", "track", "subject")


class SettingsError(Exception):
    """A setting is missing or invalid."""


class LoadError(Exception):
    """The graph cannot be loaded as asked."""


def read_env_file(path: Path) -> dict[str, str]:
    """KEY=VALUE lines of a .env file (comments and blank lines skipped, quotes removed)."""
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.removeprefix("export ").strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        values[key] = value
    return values


def find_env_file(start: Path | None = None) -> Path | None:
    """The nearest .env from `start` (default: the working directory) up to the repository root."""
    here = (start or Path.cwd()).resolve()
    for folder in (here, *here.parents):
        if (folder / ".env").is_file():
            return folder / ".env"
        if (folder / ".git").exists():  # repository root (a file in a git worktree)
            return None
    return None


def database_url() -> str:
    """DATABASE_URL from the environment, else from the repository .env."""
    url = os.environ.get("DATABASE_URL")
    if url:
        return url
    env_file = find_env_file()
    if env_file is not None:
        url = read_env_file(env_file).get("DATABASE_URL")
        if url:
            return url
    raise SettingsError(
        "DATABASE_URL is not set: export it, or run `make up` at the repository root,"
        " which creates .env from .env.example"
    )


def redact(url: str) -> str:
    """The URL without its password, for messages and logs."""
    return re.sub(r"(://[^:/@]+):[^@]*@", r"\1:***@", url)


def check_schema_name(schema: str) -> str:
    if not SCHEMA_NAME.match(schema):
        raise SettingsError(f"invalid schema name {schema!r}: lowercase letters, digits and _")
    return schema


def connect(url: str | None = None, *, schema: str = DEFAULT_SCHEMA, autocommit: bool = True) -> psycopg.Connection:
    """A connection whose search_path is `schema, public` for the whole session.

    The search_path is a connection option, so a rolled-back transaction cannot reset it.
    """
    check_schema_name(schema)
    return psycopg.connect(
        url or database_url(),
        autocommit=autocommit,
        connect_timeout=5,
        options=f"-c search_path={schema},public",
    )


def migration_files() -> list[Path]:
    """The numbered migrations NNN_description.sql, in order."""
    return sorted(p for p in MIGRATIONS_DIR.iterdir() if MIGRATION_FILE.match(p.name))


def migrate(conn: psycopg.Connection, schema: str = DEFAULT_SCHEMA) -> list[str]:
    """Create `schema` if needed and apply the migrations it lacks; returns those applied."""
    check_schema_name(schema)
    applied: list[str] = []
    with conn.transaction():
        conn.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(schema)))
        conn.execute(sql.SQL("SET LOCAL search_path TO {}, public").format(sql.Identifier(schema)))
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            " version text PRIMARY KEY,"
            " applied_at timestamptz NOT NULL DEFAULT now())"
        )
        done = {row[0] for row in conn.execute("SELECT version FROM schema_migrations")}
        for path in migration_files():
            if path.stem in done:
                continue
            # No parameters, so psycopg sends the whole file as one multi-statement query.
            conn.execute(path.read_text(encoding="utf-8"))
            conn.execute("INSERT INTO schema_migrations (version) VALUES (%s)", (path.stem,))
            applied.append(path.stem)
    return applied


def graph_is_empty(conn: psycopg.Connection) -> bool:
    row = conn.execute(
        "SELECT (SELECT count(*) FROM subject) + (SELECT count(*) FROM track) + (SELECT count(*) FROM kc)"
    ).fetchone()
    return row is not None and row[0] == 0


def load_graph(conn: psycopg.Connection, graph: Graph, *, replace: bool = False) -> None:
    """Write a validated graph in one transaction.

    The schema must hold no graph yet, unless `replace` is set: then the existing graph is
    deleted first. Every edge goes through the cycle trigger.
    """
    with conn.transaction():
        if not graph_is_empty(conn):
            if not replace:
                raise LoadError("the schema already holds a KC graph; --replace overwrites it")
            for table in GRAPH_TABLES:  # children first
                conn.execute(sql.SQL("DELETE FROM {}").format(sql.Identifier(table)))
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO subject (id, name_fr, name_ar) VALUES (%s, %s, %s)",
                [(s.id, s.name_fr, s.name_ar) for s in graph.subjects],
            )
            cur.executemany(
                "INSERT INTO track (id, section, year, name_fr, name_ar) VALUES (%s, %s, %s, %s, %s)",
                [(t.id, t.section, t.year, t.name_fr, t.name_ar) for t in graph.tracks],
            )
            cur.executemany(
                "INSERT INTO programme (track_id, subject_id, title_fr, title_ar, source_ref)"
                " VALUES (%s, %s, %s, %s, %s)",
                [(p.track_id, p.subject_id, p.title_fr, p.title_ar, p.source_ref) for p in graph.programmes],
            )
            cur.executemany(
                "INSERT INTO chapter (track_id, subject_id, number, theme_fr, theme_ar,"
                " title_fr, title_ar, source_ref) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                [
                    (c.track_id, c.subject_id, c.number, c.theme_fr, c.theme_ar, c.title_fr, c.title_ar, c.source_ref)
                    for c in graph.chapters
                ],
            )
            cur.executemany(
                "INSERT INTO kc (id, subject_id, path, name_fr, name_ar, description_fr,"
                " description_ar, difficulty_prior, status)"
                " VALUES (%s, %s, %s::ltree, %s, %s, %s, %s, %s, %s)",
                [
                    (
                        k.id,
                        k.subject_id,
                        k.path,
                        k.name_fr,
                        k.name_ar,
                        k.description_fr,
                        k.description_ar,
                        k.difficulty_prior,
                        k.status,
                    )
                    for k in graph.kcs
                ],
            )
            cur.executemany(
                "INSERT INTO kc_track (track_id, kc_id, subject_id, scope, chapter_no,"
                " exam_weight, exam_weight_source, source_ref)"
                " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                [
                    (
                        m.track_id,
                        m.kc_id,
                        m.subject_id,
                        m.scope,
                        m.chapter_no,
                        m.exam_weight,
                        m.exam_weight_source,
                        m.source_ref,
                    )
                    for m in graph.memberships
                ],
            )
            cur.executemany(
                "INSERT INTO kc_edge (from_kc_id, to_kc_id, edge_type, status, note) VALUES (%s, %s, %s, %s, %s)",
                [(e.from_kc, e.to_kc, e.edge_type, e.status, e.note) for e in graph.edges],
            )


def fetch_graph(conn: psycopg.Connection) -> Graph:
    """Read the whole graph back, in a stable order."""

    def rows(query: str) -> list[tuple]:
        return conn.execute(query).fetchall()

    return Graph(
        subjects=[Subject(*r) for r in rows("SELECT id, name_fr, name_ar FROM subject ORDER BY id")],
        tracks=[Track(*r) for r in rows("SELECT id, section, year, name_fr, name_ar FROM track ORDER BY id")],
        programmes=[
            Programme(*r)
            for r in rows(
                "SELECT track_id, subject_id, title_fr, title_ar, source_ref"
                " FROM programme ORDER BY track_id, subject_id"
            )
        ],
        chapters=[
            Chapter(*r)
            for r in rows(
                "SELECT track_id, subject_id, number, theme_fr, theme_ar, title_fr, title_ar,"
                " source_ref FROM chapter ORDER BY track_id, subject_id, number"
            )
        ],
        kcs=[
            KC(*r)
            for r in rows(
                "SELECT id, subject_id, ltree2text(path), name_fr, name_ar, description_fr,"
                " description_ar, difficulty_prior, status FROM kc ORDER BY id"
            )
        ],
        memberships=[
            Membership(*r)
            for r in rows(
                "SELECT track_id, kc_id, subject_id, scope, chapter_no, exam_weight,"
                " exam_weight_source, source_ref FROM kc_track ORDER BY track_id, kc_id"
            )
        ],
        edges=[
            Edge(*r)
            for r in rows(
                "SELECT from_kc_id, to_kc_id, edge_type, status, note FROM kc_edge"
                " ORDER BY edge_type, from_kc_id, to_kc_id"
            )
        ],
    )
