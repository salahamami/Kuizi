# Knowledge-component graph (T032)

The concept graph of the Tunisian Bac: which knowledge components (KCs) each programme track contains, in which chapter, and which KC must be known before which. It is stored in PostgreSQL (ltree paths and an edge table, with a trigger that rejects prerequisite cycles) and exported as JSON for the routing service (T052, T053) and the tutor RAG (T039, T061).

Full guide: [`docs/curriculum/kc-graph.md`](../../docs/curriculum/kc-graph.md): model, KC naming rules, how to add a KC, the export, sources of the starter seed.

| Path | What |
| --- | --- |
| `migrations/001_kc_graph.sql` | The store: subjects, tracks, programmes, chapters, KCs, track membership, typed edges, cycle trigger |
| `seed/physics_starter.yaml` | Starter Physics graph for 4e année Mathématiques, Sciences expérimentales, Sciences techniques. **To review**; completed in T035 |
| `export.schema.json` | JSON Schema (2020-12) of the export |
| `kuizi_kc_graph/` | Python tooling: `migrate`, `validate`, `load`, `export` |
| `tests/` | pytest; database tests use throwaway schemas and skip when PostgreSQL is not running |

## Commands

From the repository root, with the local stack running (`make up`):

```bash
make graph-setup    # once: uv sync
make graph-load     # create the tables in schema "curriculum" and load the starter seed
make graph-export   # write curriculum/graph/out/kc_graph.json
make graph-test     # run the tests
```

Or directly, in `curriculum/graph/`:

```bash
uv run kuizi-kc-graph validate seed/physics_starter.yaml        # no database needed
uv run kuizi-kc-graph migrate
uv run kuizi-kc-graph load seed/physics_starter.yaml --replace
uv run kuizi-kc-graph export --track sexp-4 --out out/sexp-4.json
uv run kuizi-kc-graph export --reviewed-only --out out/reviewed.json  # what students may see
```

The database is `DATABASE_URL` from the environment or the repository `.env` (ADR 0006). Set `KUIZI_REQUIRE_POSTGRES=1` to make the database tests fail instead of skipping when PostgreSQL is not reachable (for CI with a database service).
