"""The KC graph in memory: one shape for the seed file, the database and the export.

`validate_graph` applies every rule the database enforces (ids, names, chapters, scopes,
cycles), plus the rules that need the whole graph at once (prerequisite closure of each
track, exam-weight totals), so a seed can be checked before it touches PostgreSQL.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field

from kuizi_kc_graph import graph as g

LABEL = r"[a-z][a-z0-9_]*"
SUBJECT_ID = re.compile(rf"^{LABEL}$")
KC_ID = re.compile(rf"^{LABEL}(\.{LABEL})+$")
TRACK_ID = re.compile(rf"^({LABEL})-([1-4])$")
ARABIC_LETTER = re.compile(r"[؀-ۿ]")
MAX_KC_ID_LENGTH = 120

EDGE_TYPES = ("prerequisite", "sub_concept", "related")
ACYCLIC_EDGE_TYPES = ("prerequisite", "sub_concept")
SCOPES = ("core", "prerequisite")
KC_STATUSES = ("to_review", "reviewed", "retired")
EDGE_STATUSES = ("to_review", "reviewed")


@dataclass(frozen=True)
class Subject:
    id: str
    name_fr: str
    name_ar: str


@dataclass(frozen=True)
class Track:
    id: str
    section: str
    year: int
    name_fr: str
    name_ar: str


@dataclass(frozen=True)
class Programme:
    track_id: str
    subject_id: str
    title_fr: str
    title_ar: str
    source_ref: str


@dataclass(frozen=True)
class Chapter:
    track_id: str
    subject_id: str
    number: int
    theme_fr: str
    theme_ar: str
    title_fr: str
    title_ar: str
    source_ref: str


@dataclass(frozen=True)
class KC:
    id: str
    subject_id: str
    path: str
    name_fr: str
    name_ar: str
    description_fr: str | None = None
    description_ar: str | None = None
    difficulty_prior: float | None = None
    status: str = "to_review"


@dataclass(frozen=True)
class Membership:
    track_id: str
    kc_id: str
    subject_id: str
    scope: str
    chapter_no: int | None = None
    exam_weight: float | None = None
    exam_weight_source: str | None = None
    source_ref: str | None = None


@dataclass(frozen=True)
class Edge:
    from_kc: str
    to_kc: str
    edge_type: str
    status: str = "to_review"
    note: str | None = None


@dataclass
class Graph:
    subjects: list[Subject] = field(default_factory=list)
    tracks: list[Track] = field(default_factory=list)
    programmes: list[Programme] = field(default_factory=list)
    chapters: list[Chapter] = field(default_factory=list)
    kcs: list[KC] = field(default_factory=list)
    memberships: list[Membership] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)

    def edge_pairs(self, edge_type: str) -> list[tuple[str, str]]:
        return [(e.from_kc, e.to_kc) for e in self.edges if e.edge_type == edge_type]

    def summary(self) -> str:
        """One line per fact, for the command line."""
        by_type = Counter(e.edge_type for e in self.edges)
        lines = [
            f"{len(self.kcs)} KCs, {len(self.edges)} edges ("
            + ", ".join(f"{by_type.get(t, 0)} {t}" for t in EDGE_TYPES)
            + ")"
        ]
        for track in sorted(self.tracks, key=lambda t: t.id):
            members = [m for m in self.memberships if m.track_id == track.id]
            core = sum(m.scope == "core" for m in members)
            chapters = sum(c.track_id == track.id for c in self.chapters)
            lines.append(
                f"{track.id}: {len(members)} KCs ({core} core,"
                f" {len(members) - core} prerequisite), {chapters} chapters"
            )
        return "\n".join(lines)


def _blank(value: str | None) -> bool:
    return value is None or not value.strip()


def _names(what: str, fr: str | None, ar: str | None) -> list[str]:
    problems = []
    if _blank(fr):
        problems.append(f"{what}: French text is missing")
    if _blank(ar):
        problems.append(f"{what}: Arabic text is missing")
    elif not ARABIC_LETTER.search(ar or ""):
        problems.append(f"{what}: Arabic text has no Arabic letters: {ar!r}")
    return problems


def _duplicates(values: list, what: str) -> list[str]:
    return [f"duplicate {what}: {value}" for value, n in Counter(values).items() if n > 1]


def validate_graph(graph: Graph) -> list[str]:
    """Every problem found, one message each; an empty list means the graph is valid."""
    problems: list[str] = []

    # Subjects and tracks
    problems += _duplicates([s.id for s in graph.subjects], "subject")
    subjects = {s.id for s in graph.subjects}
    for s in graph.subjects:
        if not SUBJECT_ID.match(s.id):
            problems.append(f"subject {s.id!r}: id must be lowercase letters, digits and _")
        problems += _names(f"subject {s.id}", s.name_fr, s.name_ar)

    problems += _duplicates([t.id for t in graph.tracks], "track")
    tracks = {t.id for t in graph.tracks}
    for t in graph.tracks:
        match = TRACK_ID.match(t.id)
        if not match or match.group(1) != t.section or int(match.group(2)) != t.year:
            problems.append(f"track {t.id!r}: id must be <section>-<year> ({t.section}-{t.year})")
        problems += _names(f"track {t.id}", t.name_fr, t.name_ar)

    # Programmes and chapters
    problems += _duplicates([(p.track_id, p.subject_id) for p in graph.programmes], "programme")
    programmes = {(p.track_id, p.subject_id) for p in graph.programmes}
    for p in graph.programmes:
        what = f"programme {p.track_id}/{p.subject_id}"
        if p.track_id not in tracks:
            problems.append(f"{what}: unknown track")
        if p.subject_id not in subjects:
            problems.append(f"{what}: unknown subject")
        problems += _names(what, p.title_fr, p.title_ar)
        if _blank(p.source_ref):
            problems.append(f"{what}: source_ref is missing")

    chapter_keys = [(c.track_id, c.subject_id, c.number) for c in graph.chapters]
    problems += _duplicates(chapter_keys, "chapter")
    chapters = set(chapter_keys)
    for c in graph.chapters:
        what = f"chapter {c.track_id}/{c.subject_id}/{c.number}"
        if (c.track_id, c.subject_id) not in programmes:
            problems.append(f"{what}: no programme for this track and subject")
        if c.number < 1:
            problems.append(f"{what}: number must be 1 or more")
        problems += _names(f"{what} theme", c.theme_fr, c.theme_ar)
        problems += _names(f"{what} title", c.title_fr, c.title_ar)
        if _blank(c.source_ref):
            problems.append(f"{what}: source_ref is missing")

    # KCs
    problems += _duplicates([k.id for k in graph.kcs], "KC id")
    problems += _duplicates([k.path for k in graph.kcs], "KC path")
    kcs = {k.id: k for k in graph.kcs}
    for k in graph.kcs:
        what = f"KC {k.id}"
        if not KC_ID.match(k.id) or len(k.id) > MAX_KC_ID_LENGTH:
            problems.append(
                f"{what}: id must be dotted lowercase labels (at most {MAX_KC_ID_LENGTH} chars)"
            )
        if k.subject_id not in subjects:
            problems.append(f"{what}: unknown subject {k.subject_id!r}")
        if k.id.split(".")[0] != k.subject_id:
            problems.append(f"{what}: id must start with its subject ({k.subject_id})")
        if not KC_ID.match(k.path):
            problems.append(f"{what}: path {k.path!r} must be dotted lowercase labels")
        elif k.path.split(".")[0] != k.subject_id:
            problems.append(f"{what}: path {k.path!r} must start with its subject ({k.subject_id})")
        problems += _names(what, k.name_fr, k.name_ar)
        if (k.description_fr is None) != (k.description_ar is None):
            problems.append(f"{what}: a description needs both French and Arabic")
        elif k.description_fr is not None:
            problems += _names(f"{what} description", k.description_fr, k.description_ar)
        if k.difficulty_prior is not None and not -4 <= k.difficulty_prior <= 4:
            problems.append(f"{what}: difficulty_prior must be between -4 and 4")
        if k.status not in KC_STATUSES:
            problems.append(f"{what}: status must be one of {', '.join(KC_STATUSES)}")

    # Track memberships
    problems += _duplicates([(m.track_id, m.kc_id) for m in graph.memberships], "track membership")
    for m in graph.memberships:
        what = f"KC {m.kc_id} in {m.track_id}"
        kc = kcs.get(m.kc_id)
        if m.track_id not in tracks:
            problems.append(f"{what}: unknown track")
        if kc is None:
            problems.append(f"{what}: unknown KC")
        elif kc.subject_id != m.subject_id:
            problems.append(f"{what}: subject {m.subject_id} is not the KC's ({kc.subject_id})")
        if m.scope not in SCOPES:
            problems.append(f"{what}: scope must be core or prerequisite")
        if (m.scope == "core") != (m.chapter_no is not None):
            problems.append(f"{what}: a core KC needs a chapter and a prerequisite KC has none")
        if m.scope == "prerequisite" and _blank(m.source_ref):
            problems.append(f"{what}: a prerequisite KC needs source_ref (where it is taught)")
        if m.chapter_no is not None and (m.track_id, m.subject_id, m.chapter_no) not in chapters:
            problems.append(
                f"{what}: chapter {m.chapter_no} is not in the {m.subject_id} programme"
                f" of {m.track_id}"
            )
        if m.exam_weight is not None:
            if not 0 <= m.exam_weight <= 1:
                problems.append(f"{what}: exam_weight must be between 0 and 1")
            if m.scope != "core":
                problems.append(f"{what}: only core KCs carry an exam weight")
            if _blank(m.exam_weight_source):
                problems.append(f"{what}: an exam weight needs exam_weight_source")
    members_by_track: dict[str, set[str]] = defaultdict(set)
    for m in graph.memberships:
        members_by_track[m.track_id].add(m.kc_id)
    with_track = {m.kc_id for m in graph.memberships}
    problems += [f"KC {k.id}: belongs to no track" for k in graph.kcs if k.id not in with_track]

    # Edges
    problems += _duplicates([(e.from_kc, e.to_kc, e.edge_type) for e in graph.edges], "edge")
    related = [
        tuple(sorted((e.from_kc, e.to_kc))) for e in graph.edges if e.edge_type == "related"
    ]
    problems += _duplicates(related, "related edge (either direction)")
    for e in graph.edges:
        what = f"{e.edge_type} edge {e.from_kc} -> {e.to_kc}"
        if e.edge_type not in EDGE_TYPES:
            problems.append(f"{what}: type must be one of {', '.join(EDGE_TYPES)}")
        if e.status not in EDGE_STATUSES:
            problems.append(f"{what}: status must be one of {', '.join(EDGE_STATUSES)}")
        for end in (e.from_kc, e.to_kc):
            if end not in kcs:
                problems.append(f"{what}: unknown KC {end}")
        if e.from_kc == e.to_kc:
            problems.append(f"{what}: an edge cannot join a KC to itself")
    for edge_type in ACYCLIC_EDGE_TYPES:
        cycle = g.find_cycle(kcs, graph.edge_pairs(edge_type))
        if cycle:
            problems.append(f"{edge_type} edges form a cycle: " + " -> ".join(cycle))

    # Prerequisite closure: a track holds every prerequisite of its KCs, so routing inside
    # one track can always walk back to the weakest prerequisite.
    pred = g.predecessors(kcs, graph.edge_pairs("prerequisite"))
    for track_id in sorted(members_by_track):
        members = members_by_track[track_id]
        for kc_id in sorted(members):
            for missing in sorted(g.ancestors(kc_id, pred) - members):
                problems.append(
                    f"track {track_id}: {kc_id} needs {missing}, which is not in the track"
                    " (add it, with scope prerequisite if it is not in the programme)"
                )

    # Exam weights of one subject in one track add up to at most 1.
    totals: dict[tuple[str, str], float] = defaultdict(float)
    for m in graph.memberships:
        if m.exam_weight is not None:
            totals[(m.track_id, m.subject_id)] += m.exam_weight
    for (track_id, subject_id), total in sorted(totals.items()):
        if total > 1 + 1e-9:
            problems.append(
                f"track {track_id}: {subject_id} exam weights add up to {total:.3f}, more than 1"
            )

    return problems
