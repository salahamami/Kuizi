"""Shared fixtures.

Tests marked `postgres` get a throwaway schema each (kc_test_<random>), dropped afterwards,
so they never touch the real `curriculum` schema. Without a reachable PostgreSQL they are
skipped, unless KUIZI_REQUIRE_POSTGRES=1 (for CI with a database), which makes them fail.
"""

from __future__ import annotations

import os
import uuid
from collections.abc import Iterator
from typing import NoReturn

import psycopg
import pytest
from psycopg import sql

from kuizi_kc_graph import STARTER_SEED, db
from kuizi_kc_graph.model import Graph
from kuizi_kc_graph.seed import load_seed

REQUIRE_POSTGRES = os.environ.get("KUIZI_REQUIRE_POSTGRES") == "1"


@pytest.fixture(scope="session")
def starter() -> Graph:
    """The starter Physics seed, parsed and validated."""
    return load_seed(STARTER_SEED)


def _unavailable(message: str) -> NoReturn:
    if REQUIRE_POSTGRES:
        pytest.fail(message)
    pytest.skip(message)


@pytest.fixture(scope="session")
def database_url() -> str:
    try:
        url = db.database_url()
    except db.SettingsError as error:
        _unavailable(f"PostgreSQL tests skipped: {error}")
    try:
        with psycopg.connect(url, connect_timeout=3) as conn:
            conn.execute("SELECT 1")
    except psycopg.OperationalError as error:
        _unavailable(f"PostgreSQL not reachable at {db.redact(url)} (run make up): {error}")
    return url


@pytest.fixture
def schema(database_url: str) -> Iterator[str]:
    """A new schema with the migrations applied; dropped after the test."""
    name = f"kc_test_{uuid.uuid4().hex[:12]}"
    try:
        with db.connect(database_url, schema=name) as conn:
            db.migrate(conn, name)
        yield name
    finally:
        with psycopg.connect(database_url, autocommit=True) as admin:
            admin.execute(sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(name)))


@pytest.fixture
def conn(database_url: str, schema: str) -> Iterator[psycopg.Connection]:
    """An autocommit connection on the test schema: each statement is its own transaction."""
    with db.connect(database_url, schema=schema) as connection:
        yield connection
