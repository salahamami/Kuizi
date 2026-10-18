# Event contracts (`schemas/`)

The learner event schemas (T023, [ADR 0009](../docs/architecture/decisions/0009-learner-event-contracts.md)) and the Python tooling that checks, documents and registers them. Readable catalogue of every event, its owner, producer, consumers, privacy and retention: [`docs/data/event-catalogue.md`](../docs/data/event-catalogue.md).

```
schemas/
  events/
    catalogue.yaml          owner, producer, consumers, retention, privacy rules, model-input map
    common/*.avsc           shared types: Envelope, ItemContext, AccommodationContext, enums
    <event>.avsc            one Avro record per event (item.answered.avsc, focus.start.avsc, ...)
    examples/<event>.json   synthetic example events
  kuizi_schemas/            the tooling (Python 3.12, uv)
  tests/                    pytest
```

## Commands

From the repository root (they need [uv](../docs/dev/local-setup.md)):

| Command | What it does |
| --- | --- |
| `make schemas-check` | Every offline check: schemas parse (fastavro and Apache Avro), house rules, catalogue and schemas match both ways, examples are valid and synthetic, the generated page is current, and every schema stays compatible (BACKWARD_TRANSITIVE) with every version committed before |
| `make schemas-test` | The tests. Those marked `registry` use the local schema registry (`make up`) on throwaway subjects and delete them afterwards; without the stack they are skipped (set `KUIZI_REQUIRE_REGISTRY=1` to make that an error) |
| `make schemas-docs` | Regenerate `docs/data/event-catalogue.md` |
| `make schemas-register` | Set BACKWARD_TRANSITIVE on each subject and register every schema in the registry at `SCHEMA_REGISTRY_URL` (from `.env`). Checks all subjects first and registers nothing if one is incompatible; running it again changes nothing |

Inside `schemas/`, the same commands are `uv run kuizi-schemas check | docs | register [--dry-run] | compat [--against REF] | expand --out DIR` and `uv run pytest`. `expand` writes the self-contained schema of each subject, for code generators (T024).

## Add or change an event

1. **Ask first** if the change touches an event other services read, or adds a personal or sensitive field: the product owner approves, and the DPO too for personal or sensitive data (working agreement, review gates).
2. Edit or add `events/<event>.avsc`:
   - the record is `kuizi.events.<PascalCaseEventName>` and its first field is `envelope` (`kuizi.events.common.Envelope`);
   - every field has a `doc` and a `privacy` label (`none`, `pseudonymous`, `personal`, `sensitive`); sensitive fields only inside `AccommodationContext`;
   - optional fields are `["null", T]` with `"default": null`; every field added to an existing event needs a default;
   - enums start with `UNKNOWN` and declare `"default": "UNKNOWN"`, so new values never break older readers;
   - never a name, email, phone number, national ID, IP address, location, device identifier, raw keystroke or free text from a learner.
3. Add or update the entry in `events/catalogue.yaml` (topic `learner.<event>.v1`, owner, producer, consumers with tickets, retention, envelope fields the producer must fill) and synthetic examples in `events/examples/<event>.json`.
4. Run `make schemas-docs`, then `make schemas-check` and `make schemas-test`.
5. A change the compatibility check refuses is a new major version: a new file and topic `learner.<event>.v2`, both published during a migration period. Schemas already committed are never deleted; deprecate the event in the catalogue instead.

After the merge, `make schemas-register` (locally) or the cloud pipeline (T021) registers the new versions; the registry refuses anything incompatible.

## Rules every producer follows

The rules Avro cannot express are in `kuizi_schemas/examples.py` and are the reference for ingestion (T025) and the synthetic data generator (T219): UUIDs where the schema says `uuid`, timestamps in UTC milliseconds, at least one knowledge component per item, confidence 1 to 5, hint levels 1 to 4, score 0 to 1 (1 when correct), Focus sessions of 15, 25 or 45 minutes, hesitation above 3 seconds, the envelope fields the catalogue requires per event, and no value that looks like an email address, a Tunisian phone number or a national ID.
