"""Shishen / liuqin lookup helpers for ShiShenJudge."""

from __future__ import annotations

from typing import Any

SHISHEN_ALIASES: dict[str, str] = {
    "印绶": "正印",
    "印綬": "正印",
    "偏官": "七杀",
    "枭神": "偏印",
    "梟神": "偏印",
    "败财": "劫财",
}

LIUQIN_ASPECTS_BY_GENDER: dict[str, tuple[str, ...]] = {
    "male": ("general", "male_spouse", "male_parent", "children", "sibling"),
    "female": ("general", "female_spouse", "female_parent", "children", "sibling"),
}


def normalize_shishen_label(label: str) -> str:
    text = str(label or "").strip()
    if not text:
        return ""
    return SHISHEN_ALIASES.get(text, text)


def _chart_gender(chart: dict[str, Any]) -> str:
    raw = str(chart.get("gender") or chart.get("sex") or "").strip().lower()
    if raw in {"m", "male", "男", "1"}:
        return "male"
    if raw in {"f", "female", "女", "2"}:
        return "female"
    return ""


def build_shishen_lookup_keys(chart: dict[str, Any]) -> list[dict[str, str]]:
    pillars = chart.get("pillars") or {}
    day_gan = str(pillars.get("day", {}).get("gan") or chart.get("dayMaster") or "")
    month_ss = normalize_shishen_label(str(pillars.get("month", {}).get("shishenGan") or ""))
    keys: list[dict[str, str]] = []
    seen: set[tuple[str, ...]] = set()

    def _add(key: dict[str, str]) -> None:
        frozen = tuple(sorted(key.items()))
        if frozen not in seen:
            seen.add(frozen)
            keys.append(key)

    if month_ss:
        if day_gan:
            _add({"dayGan": day_gan, "shishen": month_ss})
        _add({"shishen": month_ss, "role": month_ss})

    for pillar in ("year", "hour"):
        ss = normalize_shishen_label(str(pillars.get(pillar, {}).get("shishenGan") or ""))
        if ss and day_gan:
            _add({"dayGan": day_gan, "shishen": ss})

    gender = _chart_gender(chart)
    aspects = LIUQIN_ASPECTS_BY_GENDER.get(gender, ("general", "children", "sibling"))
    for aspect in aspects:
        _add({"category": "liuqin", "aspect": aspect})

    return keys


def lookup_shishen_rows(store, chart: dict[str, Any]) -> list[dict]:
    if not store.enabled:
        return []
    rows: list[dict] = []
    seen_ids: set[str] = set()
    for key in build_shishen_lookup_keys(chart):
        for row in store.lookup("shishen", key):
            node_id = str(row.get("id") or "")
            if node_id and node_id not in seen_ids:
                seen_ids.add(node_id)
                rows.append(row)
    return rows
