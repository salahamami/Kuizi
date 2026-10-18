"""Read a seed file (YAML, reviewable by a teacher) into a Graph and check it.

The format is described at the top of seed/physics_starter.yaml and in
docs/curriculum/kc-graph.md. Edges are written on the KC they point to:
`requires` lists its prerequisites, `parents` the KCs it is a sub-concept of.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from kuizi_kc_graph.model import (
    KC,
    Chapter,
    Edge,
    Graph,
    Membership,
    Programme,
    Subject,
    Track,
    validate_graph,
)

SEED_FORMAT = "kuizi.kc-graph.seed"
SEED_FORMAT_VERSION = 1
TOP_KEYS = {"format", "format_version", "meta", "subjects", "tracks", "programmes", "kcs"}
KC_KEYS = {
    "id", "name", "path", "description", "difficulty_prior", "status",
    "requires", "parents", "related", "chapters", "prerequisite_in", "source_ref",
}
MEMBERSHIP_KEYS = {"chapter", "exam_weight", "exam_weight_source"}
EDGE_KEYS = (("requires", "prerequisite"), ("parents", "sub_concept"), ("related", "related"))


class SeedError(Exception):
    """The seed file has problems; `problems` lists every one of them."""

    def __init__(self, source: object, problems: list[str]):
        self.source = str(source)
        self.problems = list(problems)
        lines = "\n".join(f"  - {problem}" for problem in self.problems)
        super().__init__(f"{self.source}: {len(self.problems)} problem(s)\n{lines}")


def load_seed(path: Path | str) -> Graph:
    """Parse and validate a seed file; raise SeedError listing every problem."""
    path = Path(path)
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise SeedError(path, [f"cannot read the file: {error}"]) from error
    graph, problems = parse_seed(data)
    problems += validate_graph(graph)
    if problems:
        raise SeedError(path, problems)
    return graph


def parse_seed(data: Any) -> tuple[Graph, list[str]]:
    """Turn the YAML structure into a Graph; returns the shape problems found on the way."""
    problems: list[str] = []
    graph = Graph()
    if not isinstance(data, dict):
        return graph, ["the file must hold a mapping: format, subjects, tracks, programmes, kcs"]
    if data.get("format") != SEED_FORMAT:
        problems.append(f"format must be {SEED_FORMAT!r}")
    if data.get("format_version") != SEED_FORMAT_VERSION:
        problems.append(f"format_version must be {SEED_FORMAT_VERSION}")
    problems += _unknown_keys(data, TOP_KEYS, "the file")
    if "meta" in data and not isinstance(data["meta"], dict):
        problems.append("meta must be a mapping")

    for i, item in enumerate(_items(data, "subjects", problems)):
        where = f"subjects[{i}]"
        problems += _unknown_keys(item, {"id", "name"}, where)
        fr, ar = _bilingual(item.get("name"), f"{where}.name", problems)
        graph.subjects.append(Subject(_text(item, "id", where, problems), fr, ar))

    for i, item in enumerate(_items(data, "tracks", problems)):
        where = f"tracks[{i}]"
        problems += _unknown_keys(item, {"id", "section", "year", "name"}, where)
        fr, ar = _bilingual(item.get("name"), f"{where}.name", problems)
        graph.tracks.append(
            Track(
                _text(item, "id", where, problems),
                _text(item, "section", where, problems),
                _integer(item, "year", where, problems),
                fr,
                ar,
            )
        )

    for i, item in enumerate(_items(data, "programmes", problems)):
        where = f"programmes[{i}]"
        allowed = {"track", "subject", "title", "source_ref", "chapters"}
        problems += _unknown_keys(item, allowed, where)
        track_id = _text(item, "track", where, problems)
        subject_id = _text(item, "subject", where, problems)
        fr, ar = _bilingual(item.get("title"), f"{where}.title", problems)
        source = _text(item, "source_ref", where, problems)
        graph.programmes.append(Programme(track_id, subject_id, fr, ar, source))
        for j, chapter in enumerate(_items(item, "chapters", problems, where)):
            cwhere = f"{where}.chapters[{j}]"
            problems += _unknown_keys(chapter, {"number", "theme", "title", "source_ref"}, cwhere)
            theme_fr, theme_ar = _bilingual(chapter.get("theme"), f"{cwhere}.theme", problems)
            title_fr, title_ar = _bilingual(chapter.get("title"), f"{cwhere}.title", problems)
            graph.chapters.append(
                Chapter(
                    track_id,
                    subject_id,
                    _integer(chapter, "number", cwhere, problems),
                    theme_fr,
                    theme_ar,
                    title_fr,
                    title_ar,
                    _text(chapter, "source_ref", cwhere, problems),
                )
            )

    for i, item in enumerate(_items(data, "kcs", problems)):
        _parse_kc(item, i, graph, problems)

    return graph, problems


def _parse_kc(item: dict, index: int, graph: Graph, problems: list[str]) -> None:
    kc_id = item.get("id")
    if not isinstance(kc_id, str) or not kc_id:
        problems.append(f"kcs[{index}]: id is missing")
        return
    where = f"KC {kc_id}"
    problems += _unknown_keys(item, KC_KEYS, where)
    subject_id = kc_id.split(".")[0]
    path = item.get("path", kc_id)
    if not isinstance(path, str):
        problems.append(f"{where}: path must be text")
        path = kc_id
    name_fr, name_ar = _bilingual(item.get("name"), f"{where} name", problems)
    description_fr = description_ar = None
    if item.get("description") is not None:
        description_fr, description_ar = _bilingual(
            item["description"], f"{where} description", problems
        )
    prior = item.get("difficulty_prior")
    if prior is not None and not _is_number(prior):
        problems.append(f"{where}: difficulty_prior must be a number or null")
        prior = None
    status = item.get("status", "to_review")
    graph.kcs.append(
        KC(
            kc_id,
            subject_id,
            path,
            name_fr,
            name_ar,
            description_fr,
            description_ar,
            None if prior is None else float(prior),
            status,
        )
    )

    source_ref = item.get("source_ref")
    if source_ref is not None and not isinstance(source_ref, str):
        problems.append(f"{where}: source_ref must be text")
        source_ref = None

    chapters = item.get("chapters") or {}
    if not isinstance(chapters, dict):
        problems.append(f"{where}: chapters must map a track id to a chapter number")
        chapters = {}
    for track_id, value in chapters.items():
        weight = weight_source = None
        if isinstance(value, dict):
            problems += _unknown_keys(value, MEMBERSHIP_KEYS, f"{where} chapters.{track_id}")
            weight, weight_source = value.get("exam_weight"), value.get("exam_weight_source")
            value = value.get("chapter")
        if isinstance(value, bool) or not isinstance(value, int):
            problems.append(f"{where}: chapters.{track_id} must be a chapter number")
            continue
        if weight is not None and not _is_number(weight):
            problems.append(f"{where}: chapters.{track_id}.exam_weight must be a number or null")
            weight = None
        if weight_source is not None and not isinstance(weight_source, str):
            problems.append(f"{where}: chapters.{track_id}.exam_weight_source must be text")
            weight_source = None
        graph.memberships.append(
            Membership(
                str(track_id),
                kc_id,
                subject_id,
                "core",
                value,
                None if weight is None else float(weight),
                weight_source,
                source_ref,
            )
        )

    for track_id in _id_list(item, "prerequisite_in", where, problems):
        graph.memberships.append(
            Membership(track_id, kc_id, subject_id, "prerequisite", source_ref=source_ref)
        )

    for key, edge_type in EDGE_KEYS:
        for other in _id_list(item, key, where, problems):
            if edge_type == "related":
                graph.edges.append(Edge(kc_id, other, edge_type))
            else:  # written on the KC the edge points to
                graph.edges.append(Edge(other, kc_id, edge_type))


def _is_number(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def _unknown_keys(item: dict, allowed: set[str], where: str) -> list[str]:
    return [f"{where}: unknown key {key!r}" for key in sorted(set(item) - allowed, key=str)]


def _items(data: dict, key: str, problems: list[str], where: str = "the file") -> list[dict]:
    value = data.get(key)
    if not isinstance(value, list) or not all(isinstance(v, dict) for v in value):
        problems.append(f"{where}: {key} must be a list of mappings")
        return []
    return value


def _text(item: dict, key: str, where: str, problems: list[str]) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        problems.append(f"{where}: {key} is missing")
        return ""
    return value


def _integer(item: dict, key: str, where: str, problems: list[str]) -> int:
    value = item.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        problems.append(f"{where}: {key} must be a whole number")
        return 0
    return value


def _bilingual(value: Any, where: str, problems: list[str]) -> tuple[str, str]:
    if not isinstance(value, dict) or set(value) != {"fr", "ar"}:
        problems.append(f"{where}: must be a mapping with exactly fr and ar")
        return "", ""
    fr, ar = value["fr"], value["ar"]
    if not isinstance(fr, str) or not isinstance(ar, str):
        problems.append(f"{where}: fr and ar must be text")
        return "", ""
    return fr, ar


def _id_list(item: dict, key: str, where: str, problems: list[str]) -> list[str]:
    value = item.get(key) or []
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        problems.append(f"{where}: {key} must be a list of ids")
        return []
    return value
