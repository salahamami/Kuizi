"""The JSON export read by the routing service (T052, T053) and the tutor RAG (T039, T061).

The format is export.schema.json (JSON Schema 2020-12), documented in
docs/curriculum/kc-graph.md. `build_export` works on a Graph, so the same code exports
from PostgreSQL (`db.fetch_graph`) and, in tests, straight from a seed file.
"""

from __future__ import annotations

import functools
import hashlib
import json
from collections import defaultdict
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from kuizi_kc_graph import EXPORT_SCHEMA_PATH
from kuizi_kc_graph import graph as g
from kuizi_kc_graph.model import Graph

EXPORT_FORMAT = "kuizi.kc-graph"
EXPORT_FORMAT_VERSION = "1.0"
UNHASHED_KEYS = ("generated_at", "graph_hash")


class ExportError(Exception):
    """The export cannot be built, or is not valid."""


def _bilingual(fr: str, ar: str) -> dict[str, str]:
    return {"fr": fr, "ar": ar}


def _timestamp(moment: datetime | None) -> str:
    moment = (moment or datetime.now(UTC)).astimezone(UTC)
    return moment.isoformat(timespec="seconds").replace("+00:00", "Z")


def content_hash(doc: dict[str, Any]) -> str:
    """sha256 of the export without its timestamp: equal hashes mean an unchanged graph."""
    content = {key: value for key, value in doc.items() if key not in UNHASHED_KEYS}
    blob = json.dumps(content, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


def build_export(
    graph: Graph,
    *,
    tracks: Sequence[str] | None = None,
    reviewed_only: bool = False,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    """The export of the given tracks (default: all), optionally limited to reviewed content.

    A track holds every prerequisite of its KCs (checked when a seed is validated), so the
    edges among the exported KCs are enough for routing inside each track.
    """
    all_tracks = {t.id: t for t in graph.tracks}
    if tracks:
        unknown = sorted(set(tracks) - set(all_tracks))
        if unknown:
            known = ", ".join(sorted(all_tracks)) or "none"
            raise ExportError(f"unknown track(s): {', '.join(unknown)} (known: {known})")
        selected = sorted(set(tracks))
    else:
        selected = sorted(all_tracks)

    def visible(status: str) -> bool:
        return status == "reviewed" if reviewed_only else status != "retired"

    candidates = {k.id: k for k in graph.kcs if visible(k.status)}
    memberships = [m for m in graph.memberships if m.track_id in selected and m.kc_id in candidates]
    exported = {m.kc_id for m in memberships}
    kcs = {kc_id: candidates[kc_id] for kc_id in sorted(exported)}
    edges = sorted(
        (
            e
            for e in graph.edges
            if e.from_kc in kcs and e.to_kc in kcs and (e.status == "reviewed" or not reviewed_only)
        ),
        key=lambda e: (e.edge_type, e.from_kc, e.to_kc),
    )

    prerequisite_pairs = [(e.from_kc, e.to_kc) for e in edges if e.edge_type == "prerequisite"]
    sub_concept_pairs = [(e.from_kc, e.to_kc) for e in edges if e.edge_type == "sub_concept"]
    related: dict[str, set[str]] = defaultdict(set)
    for e in edges:
        if e.edge_type == "related":
            related[e.from_kc].add(e.to_kc)
            related[e.to_kc].add(e.from_kc)
    try:
        depth = g.depths(kcs, prerequisite_pairs)
    except ValueError as error:
        raise ExportError(str(error)) from error
    prerequisites = g.predecessors(kcs, prerequisite_pairs)
    dependents = g.successors(kcs, prerequisite_pairs)
    parents = g.predecessors(kcs, sub_concept_pairs)
    children = g.successors(kcs, sub_concept_pairs)

    memberships_of: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for m in sorted(memberships, key=lambda m: (m.kc_id, m.track_id)):
        memberships_of[m.kc_id].append(
            {
                "track": m.track_id,
                "scope": m.scope,
                "chapter": m.chapter_no,
                "exam_weight": m.exam_weight,
                "exam_weight_source": m.exam_weight_source,
                "source_ref": m.source_ref,
            }
        )

    track_docs = []
    for track_id in selected:
        track = all_tracks[track_id]
        programmes = []
        for p in sorted((p for p in graph.programmes if p.track_id == track_id), key=lambda p: p.subject_id):
            chapters = sorted(
                (c for c in graph.chapters if c.track_id == track_id and c.subject_id == p.subject_id),
                key=lambda c: c.number,
            )
            programmes.append(
                {
                    "subject": p.subject_id,
                    "title": _bilingual(p.title_fr, p.title_ar),
                    "source_ref": p.source_ref,
                    "chapters": [
                        {
                            "number": c.number,
                            "theme": _bilingual(c.theme_fr, c.theme_ar),
                            "title": _bilingual(c.title_fr, c.title_ar),
                            "source_ref": c.source_ref,
                        }
                        for c in chapters
                    ],
                }
            )
        members = sorted(m.kc_id for m in memberships if m.track_id == track_id)
        track_docs.append(
            {
                "id": track.id,
                "section": track.section,
                "year": track.year,
                "name": _bilingual(track.name_fr, track.name_ar),
                "programmes": programmes,
                "topological_order": g.topological_order(members, prerequisite_pairs),
            }
        )

    used_subjects = {k.subject_id for k in kcs.values()}
    used_subjects |= {p["subject"] for t in track_docs for p in t["programmes"]}
    doc: dict[str, Any] = {
        "format": EXPORT_FORMAT,
        "format_version": EXPORT_FORMAT_VERSION,
        "generated_at": _timestamp(generated_at),
        "graph_hash": "",
        "filter": {
            "tracks": sorted(set(tracks)) if tracks else None,
            "reviewed_only": reviewed_only,
        },
        "subjects": [
            {"id": s.id, "name": _bilingual(s.name_fr, s.name_ar)}
            for s in sorted(graph.subjects, key=lambda s: s.id)
            if s.id in used_subjects
        ],
        "tracks": track_docs,
        "kcs": [
            {
                "id": k.id,
                "subject": k.subject_id,
                "path": k.path,
                "name": _bilingual(k.name_fr, k.name_ar),
                "description": (
                    None
                    if k.description_fr is None or k.description_ar is None
                    else _bilingual(k.description_fr, k.description_ar)
                ),
                "difficulty_prior": k.difficulty_prior,
                "review_status": k.status,
                "depth": depth[k.id],
                "prerequisites": sorted(prerequisites[k.id]),
                "dependents": sorted(dependents[k.id]),
                "parents": sorted(parents[k.id]),
                "children": sorted(children[k.id]),
                "related": sorted(related[k.id]),
                "memberships": memberships_of[k.id],
            }
            for k in kcs.values()
        ],
        "edges": [{"from": e.from_kc, "to": e.to_kc, "type": e.edge_type, "review_status": e.status} for e in edges],
    }
    doc["graph_hash"] = content_hash(doc)
    return doc


@functools.cache
def load_export_schema() -> dict[str, Any]:
    return json.loads(EXPORT_SCHEMA_PATH.read_text(encoding="utf-8"))


def check_export(doc: dict[str, Any]) -> list[str]:
    """Problems with an export: JSON Schema first, then the references the schema cannot see."""
    validator = Draft202012Validator(load_export_schema())
    errors = sorted(validator.iter_errors(doc), key=lambda e: [str(p) for p in e.absolute_path])
    problems = [f"{'/'.join(str(p) for p in error.absolute_path) or '(root)'}: {error.message}" for error in errors]
    if problems:
        return problems

    ids = {k["id"] for k in doc["kcs"]}
    for k in doc["kcs"]:
        for key in ("prerequisites", "dependents", "parents", "children", "related"):
            problems += [f"KC {k['id']}: {key} names unknown KC {o}" for o in k[key] if o not in ids]
    for e in doc["edges"]:
        problems += [
            f"edge {e['from']} -> {e['to']}: unknown KC {end}" for end in (e["from"], e["to"]) if end not in ids
        ]
    for t in doc["tracks"]:
        members = sorted(k["id"] for k in doc["kcs"] if any(m["track"] == t["id"] for m in k["memberships"]))
        order = t["topological_order"]
        if sorted(order) != members:
            problems.append(f"track {t['id']}: topological_order must list exactly its KCs")
            continue
        position = {kc_id: i for i, kc_id in enumerate(order)}
        for k in doc["kcs"]:
            if k["id"] in position:
                problems += [
                    f"track {t['id']}: {p} must come before {k['id']} in topological_order"
                    for p in k["prerequisites"]
                    if p in position and position[p] > position[k["id"]]
                ]
    if content_hash(doc) != doc["graph_hash"]:
        problems.append("graph_hash does not match the content")
    return problems


def validate_export(doc: dict[str, Any]) -> None:
    """Raise ExportError listing what is wrong with the export."""
    problems = check_export(doc)
    if problems:
        shown = "\n".join(f"  - {p}" for p in problems[:50])
        more = f"\n  ... and {len(problems) - 50} more" if len(problems) > 50 else ""
        raise ExportError(f"the export is not valid ({len(problems)} problem(s)):\n{shown}{more}")


def dumps(doc: dict[str, Any]) -> str:
    """The export as UTF-8 JSON text (Arabic kept readable)."""
    return json.dumps(doc, ensure_ascii=False, indent=2) + "\n"


def write_export(doc: dict[str, Any], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(dumps(doc), encoding="utf-8")
