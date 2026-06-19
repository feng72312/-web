from __future__ import annotations

from typing import Any

from app.core.paipan.interactions import PILLAR_KEYS, build_interaction_notes

INTERACTION_PATTERNS = (
    "stem_he",
    "branch_chong",
    "branch_he",
    "branch_hai",
    "shensha",
)


def _pillar_maps(chart: dict[str, Any]) -> tuple[dict[str, str], dict[str, str]]:
    pillars = chart.get("pillars") or {}
    gans = {key: str(pillars.get(key, {}).get("gan") or "") for key in PILLAR_KEYS}
    zhis = {key: str(pillars.get(key, {}).get("zhi") or "") for key in PILLAR_KEYS}
    return gans, zhis


def resolve_interaction_notes(chart: dict[str, Any]) -> tuple[str, str]:
    detail = chart.get("pillarDetail") or {}
    stem_notes = detail.get("stemNotes")
    branch_notes = detail.get("branchNotes")
    if stem_notes is not None and branch_notes is not None:
        return str(stem_notes), str(branch_notes)
    pillars = chart.get("pillars") or {}
    if not pillars:
        return "暂无", "暂无"
    payload = {
        key: {"gan": pillars.get(key, {}).get("gan"), "zhi": pillars.get(key, {}).get("zhi")}
        for key in PILLAR_KEYS
    }
    notes = build_interaction_notes(payload)
    return notes["stemNotes"], notes["branchNotes"]


def collect_shensha_labels(chart: dict[str, Any]) -> list[str]:
    detail = chart.get("pillarDetail") or {}
    labels: list[str] = []
    for column in detail.get("columns") or []:
        for item in column.get("shenSha") or []:
            name = str(item.get("name") or item) if isinstance(item, dict) else str(item)
            name = name.strip()
            if name and name not in labels:
                labels.append(name)
    return labels


def detect_interaction_patterns(chart: dict[str, Any]) -> list[str]:
    stem_notes, branch_notes = resolve_interaction_notes(chart)
    patterns: list[str] = []
    if stem_notes and stem_notes != "暂无":
        patterns.append("stem_he")
    if branch_notes and branch_notes != "暂无":
        if "冲" in branch_notes:
            patterns.append("branch_chong")
        if "合" in branch_notes:
            patterns.append("branch_he")
        if "害" in branch_notes:
            patterns.append("branch_hai")
        if "刑" in branch_notes:
            patterns.append("branch_xing")
    if collect_shensha_labels(chart):
        patterns.append("shensha")
    return patterns


def build_interaction_key(pattern: str) -> dict[str, str]:
    return {"pattern": pattern, "category": "pillar_interaction"}


def build_interaction_keys(chart: dict[str, Any]) -> list[dict[str, str]]:
    return [build_interaction_key(pattern) for pattern in detect_interaction_patterns(chart)]
