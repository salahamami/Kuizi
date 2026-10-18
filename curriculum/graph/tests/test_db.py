"""The PostgreSQL store: migration, constraints, cycle trigger, concurrency, load and export.

Every test runs in its own throwaway schema (see conftest.py) and is skipped when the local
PostgreSQL is not reachable (`make up` starts it).
"""

from __future__ import annotations

import json
import threading
import time

import psycopg
import pytest
from psycopg import errors

from kuizi_kc_graph import STARTER_SEED, db
from kuizi_kc_graph.cli import main
from kuizi_kc_graph.export import build_export, check_export

pytestmark = pytest.mark.postgres

GRAPH_TABLES = {"subject", "track", "programme", "chapter", "kc", "kc_track", "kc_edge"}


# --- helpers ---------------------------------------------------------------------------


def add_subject(conn: psycopg.Connection, subject: str = "physics") -> None:
    conn.execute(
        "INSERT INTO subject (id, name_fr, name_ar) VALUES (%s, %s, %s)",
        (subject, subject.capitalize(), "مادة"),
    )


def add_track(conn: psycopg.Connection, track: str, chapters: dict[int, str]) -> None:
    section, year = track.rsplit("-", 1)
    conn.execute(
        "INSERT INTO track (id, section, year, name_fr, name_ar) VALUES (%s, %s, %s, %s, %s)",
        (track, section, int(year), f"Section {section}", "شعبة"),
    )
    conn.execute(
        "INSERT INTO programme (track_id, subject_id, title_fr, title_ar, source_ref)"
        " VALUES (%s, 'physics', %s, %s, 'test programme')",
        (track, f"Physique {track}", "الفيزياء"),
    )
    for number, title in chapters.items():
        conn.execute(
            "INSERT INTO chapter (track_id, subject_id, number, theme_fr, theme_ar, title_fr,"
            " title_ar, source_ref) VALUES (%s, 'physics', %s, 'Thème', 'محور', %s, 'باب', 'test')",
            (track, number, title),
        )


def add_kc(conn: psycopg.Connection, kc_id: str, subject: str = "physics") -> None:
    conn.execute(
        "INSERT INTO kc (id, subject_id, path, name_fr, name_ar)"
        " VALUES (%s, %s, %s::ltree, %s, %s)",
        (kc_id, subject, kc_id, f"Notion {kc_id}", "مفهوم"),
    )


def add_edge(conn: psycopg.Connection, a: str, b: str, edge_type: str = "prerequisite") -> None:
    conn.execute(
        "INSERT INTO kc_edge (from_kc_id, to_kc_id, edge_type) VALUES (%s, %s, %s)",
        (a, b, edge_type),
    )


def edge_count(conn: psycopg.Connection) -> int:
    return conn.execute("SELECT count(*) FROM kc_edge").fetchone()[0]


def chain(conn: psycopg.Connection, *kc_ids: str) -> None:
    """KCs a, b, c, ... with prerequisite edges a -> b -> c -> ..."""
    add_subject(conn)
    for kc_id in kc_ids:
        add_kc(conn, kc_id)
    for a, b in zip(kc_ids, kc_ids[1:], strict=False):
        add_edge(conn, a, b)


# --- migration -------------------------------------------------------------------------


def test_migration_creates_the_store(conn, schema):
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = %s", (schema,)
        )
    }
    assert GRAPH_TABLES | {"kc_graph_lock", "schema_migrations"} <= tables
    ltree_schema = conn.execute(
        "SELECT extnamespace::regnamespace::text FROM pg_extension WHERE extname = 'ltree'"
    ).fetchone()
    assert ltree_schema == ("public",)
    versions = [r[0] for r in conn.execute("SELECT version FROM schema_migrations")]
    assert versions == ["001_kc_graph"]
    trigger = conn.execute(
        "SELECT tgname FROM pg_trigger WHERE tgrelid = 'kc_edge'::regclass AND NOT tgisinternal"
    ).fetchall()
    assert trigger == [("kc_edge_acyclic",)]
    assert db.migrate(conn, schema) == []  # idempotent


def test_migration_refuses_to_run_in_public(database_url):
    sql_text = db.migration_files()[0].read_text(encoding="utf-8")
    with psycopg.connect(database_url, autocommit=True, options="-c search_path=public") as conn:
        with pytest.raises(errors.RaiseException, match="set search_path"):
            with conn.transaction():
                conn.execute(sql_text)


# --- tracks share KCs (acceptance criterion 1) -----------------------------------------


def test_tracks_share_a_kc_with_their_own_chapter_and_exam_weight(conn):
    add_subject(conn)
    add_track(conn, "sexp-4", {7: "Ondes mécaniques progressives"})
    add_track(conn, "tech-4", {9: "Ondes mécaniques progressives"})
    add_kc(conn, "physics.waves.mechanical")
    conn.execute(
        "INSERT INTO kc_track (track_id, kc_id, subject_id, scope, chapter_no, exam_weight,"
        " exam_weight_source) VALUES ('sexp-4', 'physics.waves.mechanical', 'physics', 'core',"
        " 7, 0.125, 'test: share of points in sample papers')"
    )
    conn.execute(
        "INSERT INTO kc_track (track_id, kc_id, subject_id, scope, chapter_no)"
        " VALUES ('tech-4', 'physics.waves.mechanical', 'physics', 'core', 9)"
    )
    rows = conn.execute(
        "SELECT track_id, chapter_no, exam_weight FROM kc_track"
        " WHERE kc_id = %s ORDER BY track_id",
        ("physics.waves.mechanical",),
    ).fetchall()
    assert rows == [("sexp-4", 7, 0.125), ("tech-4", 9, None)]

    doc = build_export(db.fetch_graph(conn))
    assert check_export(doc) == []
    (kc,) = doc["kcs"]
    assert [(m["track"], m["chapter"], m["exam_weight"]) for m in kc["memberships"]] == [
        ("sexp-4", 7, 0.125),
        ("tech-4", 9, None),
    ]
    assert all(t["topological_order"] == ["physics.waves.mechanical"] for t in doc["tracks"])


def test_membership_rules(conn):
    add_subject(conn)
    add_subject(conn, "maths")
    add_track(conn, "sexp-4", {1: "Le condensateur ; le dipôle RC"})
    add_kc(conn, "physics.elec.rc")
    add_kc(conn, "maths.analysis.derivative", subject="maths")
    insert = (
        "INSERT INTO kc_track (track_id, kc_id, subject_id, scope, chapter_no, exam_weight,"
        " exam_weight_source, source_ref) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    )
    cases = [
        # core needs a chapter
        (("sexp-4", "physics.elec.rc", "physics", "core", None, None, None, None),
         errors.CheckViolation, "kc_track_core_has_chapter"),
        # the chapter must exist in that track's programme
        (("sexp-4", "physics.elec.rc", "physics", "core", 9, None, None, None),
         errors.ForeignKeyViolation, None),
        # an exam weight needs its source
        (("sexp-4", "physics.elec.rc", "physics", "core", 1, 0.2, None, None),
         errors.CheckViolation, "kc_track_weight_sourced"),
        # the membership's subject is the KC's subject
        (("sexp-4", "maths.analysis.derivative", "physics", "prerequisite", None, None, None,
          "maths"), errors.ForeignKeyViolation, None),
        # a prerequisite-scope KC says where it is taught
        (("sexp-4", "maths.analysis.derivative", "maths", "prerequisite", None, None, None, None),
         errors.CheckViolation, "kc_track_prerequisite_sourced"),
    ]
    for values, error_class, constraint in cases:
        with pytest.raises(error_class) as caught:
            conn.execute(insert, values)
        if constraint:
            assert caught.value.diag.constraint_name == constraint
    conn.execute(insert, ("sexp-4", "physics.elec.rc", "physics", "core", 1, None, None, None))
    conn.execute(
        insert,
        ("sexp-4", "maths.analysis.derivative", "maths", "prerequisite", None, None, None,
         "Mathematics programme"),
    )
    assert conn.execute("SELECT count(*) FROM kc_track").fetchone() == (2,)


def test_kc_rules_and_ltree_subtrees(conn):
    add_subject(conn)
    for kc_id in (
        "physics.elec.rlc.free",
        "physics.elec.rlc.forced.resonance",
        "physics.mech.hooke",
    ):
        add_kc(conn, kc_id)
    subtree = conn.execute(
        "SELECT id FROM kc WHERE path <@ 'physics.elec.rlc'::ltree ORDER BY id"
    ).fetchall()
    assert subtree == [("physics.elec.rlc.forced.resonance",), ("physics.elec.rlc.free",)]
    with pytest.raises(errors.CheckViolation) as caught:
        conn.execute(
            "INSERT INTO kc (id, subject_id, path, name_fr, name_ar)"
            " VALUES ('physics.x', 'physics', 'maths.x', 'x', 'س')"
        )
    assert caught.value.diag.constraint_name == "kc_path_in_subject"
    with pytest.raises(errors.CheckViolation) as caught:
        add_kc(conn, "physics.elec.no_arabic")
        conn.execute("UPDATE kc SET name_ar = ' ' WHERE id = 'physics.elec.no_arabic'")
    assert caught.value.diag.constraint_name == "kc_names"


# --- cycles (acceptance criterion 2) ---------------------------------------------------


def test_a_prerequisite_cycle_is_rejected_with_a_clear_error(conn):
    a, b, c = "physics.t.a", "physics.t.b", "physics.t.c"
    chain(conn, a, b, c)
    with pytest.raises(errors.CheckViolation) as caught:
        add_edge(conn, c, a)
    diag = caught.value.diag
    assert diag.constraint_name == "kc_edge_acyclic"
    assert diag.message_primary == f"prerequisite edge {c} -> {a} would create a cycle"
    assert diag.message_detail == f"Cycle: {c} -> {a} -> {b} -> {c}"
    assert edge_count(conn) == 2


def test_an_update_that_closes_a_cycle_is_rejected(conn):
    a, b, c, d = "physics.t.a", "physics.t.b", "physics.t.c", "physics.t.d"
    chain(conn, a, b, c, d)
    with pytest.raises(errors.CheckViolation):
        conn.execute(
            "UPDATE kc_edge SET to_kc_id = %s WHERE from_kc_id = %s AND to_kc_id = %s", (a, c, d)
        )
    # Moving an edge without closing a cycle is fine.
    conn.execute(
        "UPDATE kc_edge SET from_kc_id = %s WHERE from_kc_id = %s AND to_kc_id = %s", (a, c, d)
    )


def test_sub_concept_edges_are_acyclic_and_types_are_checked_separately(conn):
    a, b = "physics.t.a", "physics.t.b"
    chain(conn, a, b)  # prerequisite a -> b
    add_edge(conn, b, a, "sub_concept")  # another type: no cycle
    with pytest.raises(errors.CheckViolation) as caught:
        add_edge(conn, a, b, "sub_concept")
    assert caught.value.diag.constraint_name == "kc_edge_acyclic"


def test_related_edges_are_symmetric_and_stored_once(conn):
    a, b = "physics.t.a", "physics.t.b"
    chain(conn, a)
    add_kc(conn, b)
    add_edge(conn, a, b, "related")
    with pytest.raises(errors.UniqueViolation):
        add_edge(conn, b, a, "related")
    with pytest.raises(errors.UniqueViolation):
        add_edge(conn, a, b, "related")


def test_a_self_loop_is_rejected(conn):
    chain(conn, "physics.t.a")
    for edge_type in ("prerequisite", "sub_concept", "related"):
        with pytest.raises(errors.CheckViolation) as caught:
            add_edge(conn, "physics.t.a", "physics.t.a", edge_type)
        assert caught.value.diag.constraint_name == "kc_edge_no_self_loop"


def test_a_duplicate_edge_is_rejected(conn):
    chain(conn, "physics.t.a", "physics.t.b")
    with pytest.raises(errors.UniqueViolation):
        add_edge(conn, "physics.t.a", "physics.t.b")


def _wait_until_waiting_for_a_lock(url: str, pid: int, timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    with psycopg.connect(url, autocommit=True) as observer:
        while time.monotonic() < deadline:
            row = observer.execute(
                "SELECT wait_event_type FROM pg_stat_activity WHERE pid = %s", (pid,)
            ).fetchone()
            if row and row[0] == "Lock":
                return
            time.sleep(0.05)
    raise AssertionError(f"backend {pid} never waited for the lock")


@pytest.mark.parametrize(
    ("isolation", "expected"),
    [
        (psycopg.IsolationLevel.READ_COMMITTED, errors.CheckViolation),
        (psycopg.IsolationLevel.REPEATABLE_READ, errors.SerializationFailure),
    ],
)
def test_concurrent_writers_cannot_close_a_cycle(database_url, schema, conn, isolation, expected):
    a, b = "physics.t.a", "physics.t.b"
    chain(conn, a)
    add_kc(conn, b)
    options = f"-c search_path={schema},public -c lock_timeout=20s"
    first = psycopg.connect(database_url, options=options)
    second = psycopg.connect(database_url, options=options)
    second.isolation_level = isolation
    outcome: dict[str, object] = {}

    def write_reverse_edge() -> None:
        try:
            add_edge(second, b, a)
            second.commit()
            outcome["result"] = "committed"
        except psycopg.Error as error:
            second.rollback()
            outcome["result"] = error

    second_pid = second.info.backend_pid
    try:
        add_edge(first, a, b)  # open transaction: holds the prerequisite lock row
        worker = threading.Thread(target=write_reverse_edge)
        worker.start()
        _wait_until_waiting_for_a_lock(database_url, second_pid)
        first.commit()
        worker.join(timeout=20)
        assert not worker.is_alive()
        assert isinstance(outcome.get("result"), expected), outcome
    finally:
        first.close()
        second.close()
    edges = conn.execute("SELECT from_kc_id, to_kc_id FROM kc_edge").fetchall()
    assert edges == [(a, b)]


# --- load, read back and export (acceptance criterion 3) -------------------------------


def test_starter_seed_round_trips_through_postgresql(conn, starter):
    db.load_graph(conn, starter)
    fetched = db.fetch_graph(conn)
    for part in ("subjects", "tracks", "programmes", "chapters", "kcs", "memberships", "edges"):
        assert set(getattr(fetched, part)) == set(getattr(starter, part)), part
    from_db = build_export(fetched)
    assert check_export(from_db) == []
    assert from_db["graph_hash"] == build_export(starter)["graph_hash"]


def test_loading_twice_needs_replace(conn, starter):
    db.load_graph(conn, starter)
    with pytest.raises(db.LoadError, match="--replace"):
        db.load_graph(conn, starter)
    db.load_graph(conn, starter, replace=True)
    assert conn.execute("SELECT count(*) FROM kc").fetchone() == (len(starter.kcs),)
    assert edge_count(conn) == len(starter.edges)


def test_command_line_migrate_load_export(database_url, schema, tmp_path, capsys):
    common = ["--database-url", database_url, "--schema", schema]
    assert main([*common, "migrate"]) == 0
    assert "up to date" in capsys.readouterr().out
    assert main([*common, "load", str(STARTER_SEED)]) == 0
    out = tmp_path / "sexp-4.json"
    assert main([*common, "export", "--track", "sexp-4", "--out", str(out)]) == 0
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert check_export(doc) == []
    assert doc["filter"]["tracks"] == ["sexp-4"]
    assert "الفيزياء" in out.read_text(encoding="utf-8")  # Arabic written as text, not \u escapes
    assert main([*common, "load", str(STARTER_SEED)]) == 1  # refuses to overwrite
    assert "--replace" in capsys.readouterr().err
