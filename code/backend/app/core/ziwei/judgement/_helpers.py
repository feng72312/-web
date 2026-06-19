from __future__ import annotations

from typing import Any

PALACE_ALIASES: dict[str, list[str]] = {
    "命宫": ["命宫"],
    "兄弟": ["兄弟"],
    "夫妻": ["夫妻"],
    "子女": ["子女"],
    "财帛": ["财帛"],
    "疾厄": ["疾厄"],
    "迁移": ["迁移"],
    "奴仆": ["奴仆", "交友"],
    "官禄": ["官禄", "事业"],
    "田宅": ["田宅"],
    "福德": ["福德"],
    "父母": ["父母"],
}

MAJOR_STAR_NAMES = (
    "紫微",
    "天机",
    "太阳",
    "武曲",
    "天同",
    "廉贞",
    "天府",
    "太阴",
    "贪狼",
    "巨门",
    "天相",
    "天梁",
    "七杀",
    "破军",
)

TRIAD_BY_PALACE: dict[str, list[str]] = {
    "命宫": ["命宫", "财帛", "官禄", "迁移"],
    "兄弟": ["兄弟", "疾厄", "田宅", "奴仆"],
    "夫妻": ["夫妻", "迁移", "福德", "官禄"],
    "子女": ["子女", "奴仆", "父母", "田宅"],
    "财帛": ["财帛", "命宫", "官禄", "迁移"],
    "疾厄": ["疾厄", "兄弟", "田宅", "奴仆"],
    "迁移": ["迁移", "命宫", "财帛", "官禄"],
    "奴仆": ["奴仆", "兄弟", "疾厄", "田宅"],
    "交友": ["奴仆", "兄弟", "疾厄", "田宅"],
    "官禄": ["官禄", "命宫", "财帛", "迁移"],
    "田宅": ["田宅", "兄弟", "疾厄", "奴仆"],
    "福德": ["福德", "夫妻", "迁移", "官禄"],
    "父母": ["父母", "子女", "奴仆", "田宅"],
}


def palace_map(chart: dict[str, Any]) -> dict[str, dict[str, Any]]:
    mapping: dict[str, dict[str, Any]] = {}
    for palace in chart.get("palaces") or []:
        name = str(palace.get("name") or "")
        if name:
            mapping[name] = palace
    return mapping


def resolve_palace(pmap: dict[str, dict[str, Any]], canonical: str) -> dict[str, Any] | None:
    for alias in PALACE_ALIASES.get(canonical, [canonical]):
        row = pmap.get(alias)
        if row:
            return row
    return None


def major_star_names(palace: dict[str, Any] | None) -> list[str]:
    if not palace:
        return []
    borrowed = palace.get("borrowedMajorStars") or []
    if borrowed:
        return [str(item) for item in borrowed]
    return [
        str(star.get("name") or "")
        for star in palace.get("majorStars") or []
        if star.get("name")
    ]


def all_major_positions(pmap: dict[str, dict[str, Any]]) -> dict[str, str]:
    positions: dict[str, str] = {}
    for palace_name, palace in pmap.items():
        for star in major_star_names(palace):
            positions.setdefault(star, palace_name)
    return positions


def stars_in_palaces(
    pmap: dict[str, dict[str, Any]],
    palace_names: list[str],
) -> set[str]:
    found: set[str] = set()
    for canonical in palace_names:
        palace = resolve_palace(pmap, canonical)
        found.update(major_star_names(palace))
    return found


def soul_palace(chart: dict[str, Any]) -> dict[str, Any] | None:
    meta = chart.get("meta") or {}
    soul_branch = str(meta.get("soulPalaceBranch") or meta.get("soulBranch") or "")
    for palace in chart.get("palaces") or []:
        if str(palace.get("earthlyBranch") or "") == soul_branch:
            return palace
    palaces = chart.get("palaces") or []
    return palaces[0] if palaces else None


def body_palace_name(chart: dict[str, Any]) -> str:
    meta = chart.get("meta") or {}
    body_branch = str(meta.get("bodyBranch") or "")
    for palace in chart.get("palaces") or []:
        if str(palace.get("earthlyBranch") or "") == body_branch:
            return str(palace.get("name") or "")
    return ""


def chart_school(chart: dict[str, Any]) -> str:
    rules_meta = chart.get("rulesMeta") or {}
    return str(rules_meta.get("chartSchool") or "sanhe")
