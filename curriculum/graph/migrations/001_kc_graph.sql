-- 001_kc_graph.sql: the knowledge-component (KC) graph store (T032, Jira KK-52).
--
-- The file names no schema. Run it with search_path set to the target schema first and
-- public second (public holds the ltree extension). The tooling does this for you:
--
--     cd curriculum/graph && uv run kuizi-kc-graph migrate            # schema "curriculum"
--
-- By hand with psql (one session, so the SET applies to the file):
--
--     psql "$DATABASE_URL" -v ON_ERROR_STOP=1 \
--          -c 'CREATE SCHEMA IF NOT EXISTS curriculum' \
--          -c 'SET search_path TO curriculum, public' \
--          -f curriculum/graph/migrations/001_kc_graph.sql
--
-- Model (full description in docs/curriculum/kc-graph.md):
--   subject    physics, maths, ... (T033 makes subject first-class everywhere)
--   track      a Bac section in one school year: sexp-4 = 4e année Sciences expérimentales
--   programme  the official programme of one subject in one track, with its source
--   chapter    a chapter of that programme, numbered as in the programme
--   kc         a knowledge component: stable id, ltree path in its subject, FR and AR names
--   kc_track   the tracks a KC belongs to, with the track's own chapter and exam weight;
--              one KC is shared by several tracks
--   kc_edge    typed edges between KCs:
--                prerequisite  from_kc must be known before to_kc     (acyclic)
--                sub_concept   from_kc contains to_kc                  (acyclic)
--                related       symmetric, stored once in either direction
--
-- Cycles. A trigger rejects any prerequisite or sub_concept edge that would close a cycle
-- (recursive CTE from the new edge's target back to its source); self-loops are rejected by
-- a check constraint. Concurrency: two transactions could each add one half of a cycle
-- (a -> b and b -> a) without seeing the other's uncommitted row. The trigger therefore
-- first updates this edge type's row in kc_graph_lock, so writers of one edge type take
-- turns, and only then looks for a cycle:
--   READ COMMITTED (the default): the second writer waits for the first to commit; the
--     trigger function is VOLATILE, so its cycle query takes a fresh snapshot after the
--     wait and sees the committed edge.
--   REPEATABLE READ or SERIALIZABLE: the second writer fails with SQLSTATE 40001
--     (serialization failure) on the lock row and must retry; the retry sees the edge.
-- Authoring traffic is low, so serialising edge writes per type costs nothing noticeable.

DO $$
BEGIN
    IF current_schema() IS NULL OR current_schema() = 'public' THEN
        RAISE EXCEPTION 'KC graph migration: set search_path to the target schema first, for example: SET search_path TO curriculum, public';
    END IF;
END
$$;

CREATE EXTENSION IF NOT EXISTS ltree WITH SCHEMA public;

-- Subjects -------------------------------------------------------------------------------

CREATE TABLE subject (
    id      text PRIMARY KEY,
    name_fr text NOT NULL,
    name_ar text NOT NULL,
    CONSTRAINT subject_id_format CHECK (id ~ '^[a-z][a-z0-9_]*$'),
    CONSTRAINT subject_names CHECK (btrim(name_fr) <> '' AND btrim(name_ar) <> '')
);

COMMENT ON TABLE subject IS 'Bac subjects (physics, maths, sciences, technique, eco_gestion); T033 adds subject_id to every curriculum table.';

-- Tracks: a Bac section in one school year -----------------------------------------------

CREATE TABLE track (
    id      text PRIMARY KEY,
    section text NOT NULL,
    year    smallint NOT NULL,
    name_fr text NOT NULL,
    name_ar text NOT NULL,
    CONSTRAINT track_section_format CHECK (section ~ '^[a-z][a-z0-9_]*$'),
    CONSTRAINT track_year_range CHECK (year BETWEEN 1 AND 4),
    CONSTRAINT track_id_is_section_year CHECK (id = section || '-' || year::text),
    CONSTRAINT track_names CHECK (btrim(name_fr) <> '' AND btrim(name_ar) <> '')
);

COMMENT ON TABLE track IS 'A programme track: Bac section and school year, id <section>-<year> (math-4, sexp-4, tech-4).';

-- Official programmes and their chapters -------------------------------------------------

CREATE TABLE programme (
    track_id   text NOT NULL REFERENCES track (id) ON DELETE CASCADE,
    subject_id text NOT NULL REFERENCES subject (id),
    title_fr   text NOT NULL,
    title_ar   text NOT NULL,
    source_ref text NOT NULL,
    PRIMARY KEY (track_id, subject_id),
    CONSTRAINT programme_titles CHECK (btrim(title_fr) <> '' AND btrim(title_ar) <> ''),
    CONSTRAINT programme_source CHECK (btrim(source_ref) <> '')
);

COMMENT ON TABLE programme IS 'The official programme of one subject in one track.';
COMMENT ON COLUMN programme.source_ref IS 'Where the programme was read: official text or the CNP textbook that states it follows it.';

CREATE TABLE chapter (
    track_id   text NOT NULL,
    subject_id text NOT NULL,
    number     smallint NOT NULL,
    theme_fr   text NOT NULL,
    theme_ar   text NOT NULL,
    title_fr   text NOT NULL,
    title_ar   text NOT NULL,
    source_ref text NOT NULL,
    PRIMARY KEY (track_id, subject_id, number),
    FOREIGN KEY (track_id, subject_id) REFERENCES programme (track_id, subject_id) ON DELETE CASCADE,
    CONSTRAINT chapter_number_positive CHECK (number >= 1),
    CONSTRAINT chapter_texts CHECK (btrim(theme_fr) <> '' AND btrim(theme_ar) <> ''
                                    AND btrim(title_fr) <> '' AND btrim(title_ar) <> ''),
    CONSTRAINT chapter_source CHECK (btrim(source_ref) <> '')
);

COMMENT ON TABLE chapter IS 'Chapters of an official programme, numbered as in the programme of that track.';

-- Knowledge components -------------------------------------------------------------------

CREATE TABLE kc (
    id               text PRIMARY KEY,
    subject_id       text NOT NULL REFERENCES subject (id),
    path             ltree NOT NULL,
    name_fr          text NOT NULL,
    name_ar          text NOT NULL,
    description_fr   text,
    description_ar   text,
    difficulty_prior double precision,
    status           text NOT NULL DEFAULT 'to_review',
    created_at       timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT kc_path_unique UNIQUE (path),
    CONSTRAINT kc_id_subject_unique UNIQUE (id, subject_id),
    CONSTRAINT kc_id_format CHECK (id ~ '^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$' AND length(id) <= 120),
    CONSTRAINT kc_id_in_subject CHECK (split_part(id, '.', 1) = subject_id),
    CONSTRAINT kc_path_format CHECK (ltree2text(path) ~ '^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$'),
    CONSTRAINT kc_path_in_subject CHECK (ltree2text(subpath(path, 0, 1)) = subject_id),
    CONSTRAINT kc_names CHECK (btrim(name_fr) <> '' AND btrim(name_ar) <> ''),
    CONSTRAINT kc_description_bilingual CHECK ((description_fr IS NULL) = (description_ar IS NULL)),
    CONSTRAINT kc_difficulty_range CHECK (difficulty_prior BETWEEN -4 AND 4),
    CONSTRAINT kc_status CHECK (status IN ('to_review', 'reviewed', 'retired'))
);

CREATE INDEX kc_path_gist ON kc USING gist (path);

COMMENT ON TABLE kc IS 'Knowledge components. The id never changes once items or mastery records use it; the path may move in the taxonomy.';
COMMENT ON COLUMN kc.path IS 'Position in the subject taxonomy (ltree), first label = subject; query subtrees with path <@ ''physics.elec''.';
COMMENT ON COLUMN kc.difficulty_prior IS 'Expected IRT difficulty b (logit scale, about -3 easy to +3 hard) of a typical item on this KC before calibration; NULL = unknown.';
COMMENT ON COLUMN kc.status IS 'to_review until a Tunisian subject teacher has checked it (ADR 0005); retired KCs stay for history and are not exported.';

-- Track membership: one KC, several tracks, track-specific chapter and exam weight -------

CREATE TABLE kc_track (
    track_id           text NOT NULL REFERENCES track (id) ON DELETE CASCADE,
    kc_id              text NOT NULL,
    subject_id         text NOT NULL,
    scope              text NOT NULL,
    chapter_no         smallint,
    exam_weight        double precision,
    exam_weight_source text,
    source_ref         text,
    PRIMARY KEY (track_id, kc_id),
    FOREIGN KEY (kc_id, subject_id) REFERENCES kc (id, subject_id) ON DELETE CASCADE,
    FOREIGN KEY (track_id, subject_id, chapter_no) REFERENCES chapter (track_id, subject_id, number),
    CONSTRAINT kc_track_scope CHECK (scope IN ('core', 'prerequisite')),
    CONSTRAINT kc_track_core_has_chapter CHECK ((scope = 'core') = (chapter_no IS NOT NULL)),
    CONSTRAINT kc_track_prerequisite_sourced CHECK (scope = 'core' OR btrim(coalesce(source_ref, '')) <> ''),
    CONSTRAINT kc_track_weight_range CHECK (exam_weight BETWEEN 0 AND 1),
    CONSTRAINT kc_track_weight_core_only CHECK (exam_weight IS NULL OR scope = 'core'),
    CONSTRAINT kc_track_weight_sourced CHECK (exam_weight IS NULL OR btrim(coalesce(exam_weight_source, '')) <> '')
);

CREATE INDEX kc_track_kc ON kc_track (kc_id);

COMMENT ON TABLE kc_track IS 'Which tracks a KC belongs to. core = in that track''s programme (chapter required); prerequisite = needed by a core KC but taught in an earlier year or another subject.';
COMMENT ON COLUMN kc_track.exam_weight IS 'Share (0..1) of the track''s Bac points in this subject tagged with this KC over past papers; NULL = not measured yet (T035).';

-- Edges ----------------------------------------------------------------------------------

CREATE TABLE kc_edge (
    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    from_kc_id text NOT NULL REFERENCES kc (id) ON DELETE CASCADE,
    to_kc_id   text NOT NULL REFERENCES kc (id) ON DELETE CASCADE,
    edge_type  text NOT NULL,
    status     text NOT NULL DEFAULT 'to_review',
    note       text,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT kc_edge_type CHECK (edge_type IN ('prerequisite', 'sub_concept', 'related')),
    CONSTRAINT kc_edge_status CHECK (status IN ('to_review', 'reviewed')),
    CONSTRAINT kc_edge_no_self_loop CHECK (from_kc_id <> to_kc_id),
    CONSTRAINT kc_edge_unique UNIQUE (from_kc_id, to_kc_id, edge_type)
);

-- A related edge is symmetric: a-b and b-a are the same edge.
CREATE UNIQUE INDEX kc_edge_related_once
    ON kc_edge (LEAST(from_kc_id, to_kc_id), GREATEST(from_kc_id, to_kc_id))
    WHERE edge_type = 'related';

CREATE INDEX kc_edge_to ON kc_edge (to_kc_id, edge_type);

COMMENT ON TABLE kc_edge IS 'Typed KC edges. prerequisite: from must be known before to. sub_concept: from contains to. related: symmetric. prerequisite and sub_concept are acyclic (trigger kc_edge_acyclic).';

-- One row per acyclic edge type; writers update it to take turns (see the header).
CREATE TABLE kc_graph_lock (
    edge_type  text PRIMARY KEY,
    version    bigint NOT NULL DEFAULT 0,
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT kc_graph_lock_type CHECK (edge_type IN ('prerequisite', 'sub_concept'))
);

INSERT INTO kc_graph_lock (edge_type) VALUES ('prerequisite'), ('sub_concept');

COMMENT ON TABLE kc_graph_lock IS 'Serialises writers of acyclic edge types so concurrent inserts cannot close a cycle; version counts edge writes.';

-- Cycle detection ------------------------------------------------------------------------

CREATE FUNCTION kc_edge_reject_cycle() RETURNS trigger
LANGUAGE plpgsql
SET search_path FROM CURRENT
AS $$
DECLARE
    closes_cycle boolean;
    cycle_path   text[];
BEGIN
    -- A self-loop is left to the kc_edge_no_self_loop check constraint, which names it.
    IF NEW.from_kc_id = NEW.to_kc_id THEN
        RETURN NEW;
    END IF;

    -- Take this edge type's turn (row lock held until the end of the transaction).
    UPDATE kc_graph_lock
       SET version = version + 1, updated_at = now()
     WHERE edge_type = NEW.edge_type;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'kc_graph_lock has no row for edge type %', NEW.edge_type;
    END IF;

    -- Does a path of the same type already lead from the new target back to the new source?
    -- UNION visits each KC once, so this is linear in the size of the graph.
    closes_cycle := EXISTS (
        WITH RECURSIVE reach(node) AS (
            SELECT NEW.to_kc_id
            UNION
            SELECT e.to_kc_id
              FROM reach r
              JOIN kc_edge e ON e.from_kc_id = r.node
             WHERE e.edge_type = NEW.edge_type
               AND e.id IS DISTINCT FROM NEW.id      -- on UPDATE, ignore the row being replaced
        )
        SELECT 1 FROM reach WHERE node = NEW.from_kc_id
    );

    IF closes_cycle THEN
        -- Only on rejection: find one such path to name the cycle in the error.
        cycle_path := (
            WITH RECURSIVE walk(node, trail) AS (
                SELECT NEW.to_kc_id, ARRAY[NEW.to_kc_id]
                UNION ALL
                SELECT e.to_kc_id, w.trail || e.to_kc_id
                  FROM walk w
                  JOIN kc_edge e ON e.from_kc_id = w.node
                 WHERE e.edge_type = NEW.edge_type
                   AND e.id IS DISTINCT FROM NEW.id
                   AND w.node <> NEW.from_kc_id
                   AND e.to_kc_id <> ALL (w.trail)
            )
            SELECT trail FROM walk WHERE node = NEW.from_kc_id LIMIT 1
        );

        RAISE EXCEPTION USING
            MESSAGE = format('%s edge %s -> %s would create a cycle',
                             NEW.edge_type, NEW.from_kc_id, NEW.to_kc_id),
            DETAIL = format('Cycle: %s', array_to_string(array_prepend(NEW.from_kc_id, cycle_path), ' -> ')),
            HINT = 'prerequisite and sub_concept edges must form a directed acyclic graph; remove one edge of the cycle.',
            ERRCODE = 'check_violation',
            CONSTRAINT = 'kc_edge_acyclic',
            SCHEMA = TG_TABLE_SCHEMA,
            TABLE = TG_TABLE_NAME;
    END IF;

    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION kc_edge_reject_cycle() IS 'Rejects a prerequisite or sub_concept edge that would close a cycle (SQLSTATE 23514, constraint kc_edge_acyclic).';

CREATE TRIGGER kc_edge_acyclic
    BEFORE INSERT OR UPDATE OF from_kc_id, to_kc_id, edge_type ON kc_edge
    FOR EACH ROW
    WHEN (NEW.edge_type IN ('prerequisite', 'sub_concept'))
    EXECUTE FUNCTION kc_edge_reject_cycle();
