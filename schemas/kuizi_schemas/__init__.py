"""Kuizi event contracts (T023): load, check, document and register the Avro schemas in schemas/events.

Layout of schemas/events:
  catalogue.yaml          one entry per event: topic, owner, producer, consumers, retention, privacy rules
  common/<fullname>.avsc  shared named types (Envelope, ItemContext, AccommodationContext, enums)
  <event>.avsc            one record per event, for example item.answered.avsc
  examples/<event>.json   synthetic example events, validated and round-tripped by the tests

Every event schema is expanded into a self-contained schema (shared types inlined) before it is
checked or registered, so each registry subject can be read and checked on its own.
"""

from pathlib import Path

__all__ = ["Paths"]


class Paths:
    """Where things live, relative to a repository root (the real one, or a copy in tests)."""

    EVENTS_REL = "schemas/events"
    DOC_REL = "docs/data/event-catalogue.md"

    def __init__(self, root: Path | None = None):
        self.root = Path(root) if root else Path(__file__).resolve().parents[2]

    @property
    def events(self) -> Path:
        return self.root / self.EVENTS_REL

    @property
    def catalogue(self) -> Path:
        return self.events / "catalogue.yaml"

    @property
    def common(self) -> Path:
        return self.events / "common"

    @property
    def examples(self) -> Path:
        return self.events / "examples"

    @property
    def doc(self) -> Path:
        return self.root / self.DOC_REL

    @property
    def agents(self) -> Path:
        return self.root / ".claude" / "agents"

    @property
    def backlog(self) -> Path:
        return self.root / "docs" / "backlog" / "apl_backlog.json"

    @property
    def env_file(self) -> Path:
        return self.root / ".env"
