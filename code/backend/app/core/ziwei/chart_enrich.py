from __future__ import annotations

from typing import Any

OPPOSITE_BRANCHES: dict[str, str] = {
    "子": "午",
    "丑": "未",
    "寅": "申",
    "卯": "酉",
    "辰": "戌",
    "巳": "亥",
    "午": "子",
    "未": "丑",
    "申": "寅",
    "酉": "卯",
    "戌": "辰",
    "亥": "巳",
}


def _palace_by_branch(palaces: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    mapping: dict[str, dict[str, Any]] = {}
    for palace in palaces:
        branch = str(palace.get("earthlyBranch") or "")
        if branch:
            mapping[branch] = palace
    return mapping


def _major_star_names(palace: dict[str, Any]) -> list[str]:
    return [str(star.get("name") or "") for star in palace.get("majorStars") or [] if star.get("name")]


def _summarize_palace(palace: dict[str, Any]) -> dict[str, Any]:
    majors = palace.get("majorStars") or []
    minors = palace.get("minorStars") or []
    return {
        "name": palace.get("name", ""),
        "stemBranch": palace.get("stemBranch", ""),
        "majorStars": _major_star_names(palace),
        "brightnessSummary": palace.get("brightnessSummary") or "",
        "hasMalefic": bool(palace.get("hasMalefic")),
        "mutagenStars": palace.get("mutagenStars") or [],
    }


def _palace_strength(palace: dict[str, Any], *, borrowed: bool = False) -> str:
    majors = palace.get("majorStars") or []
    if not majors:
        return "borrowed" if borrowed else "empty"
    brightness = " ".join(str(star.get("brightness") or "") for star in majors)
    if any(token in brightness for token in ("庙", "旺")):
        return "strong"
    if any(token in brightness for token in ("陷", "落")):
        return "weak"
    if palace.get("hasMalefic"):
        return "mixed"
    return "balanced"


def _risk_flags(palace: dict[str, Any], *, borrowed: bool = False) -> list[str]:
    flags: list[str] = []
    if not _major_star_names(palace):
        flags.append("empty_major")
    if borrowed:
        flags.append("borrowed_from_opposite")
    if palace.get("hasMalefic"):
        flags.append("malefic_present")
    mutagens = palace.get("mutagenStars") or []
    if any(str(row.get("mutagen")) == "忌" for row in mutagens):
        flags.append("mutagen_ji")
    return flags


def enrich_palaces(palaces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_branch = _palace_by_branch(palaces)
    enriched: list[dict[str, Any]] = []
    for palace in palaces:
        row = dict(palace)
        branch = str(row.get("earthlyBranch") or "")
        opposite_branch = OPPOSITE_BRANCHES.get(branch, "")
        opposite = by_branch.get(opposite_branch) or {}
        triad_branches = list(row.get("triadBranches") or [])
        triad_palaces = [by_branch[item] for item in triad_branches if item in by_branch]

        borrowed = False
        borrowed_stars: list[str] = []
        if not _major_star_names(row) and opposite:
            borrowed_stars = _major_star_names(opposite)
            borrowed = bool(borrowed_stars)

        row["oppositeEvidence"] = _summarize_palace(opposite) if opposite else {}
        row["triadEvidence"] = [_summarize_palace(item) for item in triad_palaces]
        row["borrowedFromOpposite"] = borrowed
        row["borrowedMajorStars"] = borrowed_stars
        row["palaceStrength"] = _palace_strength(row, borrowed=borrowed)
        row["riskFlags"] = _risk_flags(row, borrowed=borrowed)
        enriched.append(row)
    return enriched


def enrich_chart(chart: dict[str, Any]) -> dict[str, Any]:
    palaces = chart.get("palaces") or []
    if not palaces:
        return chart
    out = dict(chart)
    out["palaces"] = enrich_palaces(palaces)
    return out


def compare_rule_change(
    before: dict[str, Any],
    after: dict[str, Any],
) -> list[str]:
    warnings: list[str] = []
    before_meta = before.get("rulesMeta") or {}
    after_meta = after.get("rulesMeta") or {}
    for key in ("leapMonthRule", "ziHourRule", "mutagenTable", "chartSchool"):
        if before_meta.get(key) != after_meta.get(key):
            warnings.append(f"{key} changed: {before_meta.get(key)} -> {after_meta.get(key)}")

    before_soul = str((before.get("meta") or {}).get("soulPalaceBranch") or "")
    after_soul = str((after.get("meta") or {}).get("soulPalaceBranch") or "")
    if before_soul and after_soul and before_soul != after_soul:
        warnings.append(f"soulPalaceBranch changed: {before_soul} -> {after_soul}")

    before_palaces = before.get("palaces") or []
    after_palaces = after.get("palaces") or []
    if before_palaces and after_palaces:
        before_mutagen = {
            str(star.get("name")): str(star.get("mutagen"))
            for palace in before_palaces
            for star in palace.get("mutagenStars") or []
            if star.get("name") and star.get("mutagen")
        }
        after_mutagen = {
            str(star.get("name")): str(star.get("mutagen"))
            for palace in after_palaces
            for star in palace.get("mutagenStars") or []
            if star.get("name") and star.get("mutagen")
        }
        if before_mutagen != after_mutagen:
            warnings.append("natal mutagen mapping changed under new rules")

    return warnings
