"""Kuizi knowledge-component (KC) graph tooling (T032): schema, seed loader and JSON export."""

from pathlib import Path

__version__ = "0.1.0"

PROJECT_DIR = Path(__file__).resolve().parent.parent
MIGRATIONS_DIR = PROJECT_DIR / "migrations"
EXPORT_SCHEMA_PATH = PROJECT_DIR / "export.schema.json"
STARTER_SEED = PROJECT_DIR / "seed" / "physics_starter.yaml"
