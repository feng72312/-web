from __future__ import annotations

from typing import Any

from app.core.ziwei.mutagen_tables import MUTAGEN_TYPES, get_mutagen_stars


def _translate_star_name(raw: str) -> str:
    try:
        from iztro_py.i18n import t

        return t(raw) if raw else raw
    except ImportError:
        return raw


def _translate_stem(raw: str) -> str:
    if not raw:
        return raw
    try:
        from iztro_py.i18n import t

        return t(raw)
    except ImportError:
        return raw


def _palace_rows(raw_chart: Any) -> list[dict[str, Any]]:
    iztro_dict = raw_chart.to_iztro_dict()
    zh_list = iztro_dict.get("palaces") or []
    rows: list[dict[str, Any]] = []
    for idx, palace_obj in enumerate(raw_chart.palaces):
        row = palace_obj.model_dump() if hasattr(palace_obj, "model_dump") else {}
        zh = zh_list[idx] if idx < len(zh_list) else {}
        rows.append(
            {
                "name": zh.get("name", ""),
                "heavenlyStemKey": row.get("heavenly_stem", ""),
                "heavenlyStem": zh.get("heavenlyStem", ""),
                "earthlyBranch": zh.get("earthlyBranch", ""),
                "majorStars": palace_obj.major_stars,
                "minorStars": palace_obj.minor_stars,
            }
        )
    return rows


def _star_palace_map(rows: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    mapping: dict[str, dict[str, str]] = {}
    for row in rows:
        palace_name = str(row.get("name", ""))
        branch = str(row.get("earthlyBranch", ""))
        for star in row.get("majorStars", []) + row.get("minorStars", []):
            name = getattr(star, "name", None)
            if name and name not in mapping:
                mapping[name] = {"palaceName": palace_name, "palaceBranch": branch}
    return mapping


def compute_flying_mutagens(raw_chart: Any, table_id: str) -> dict[str, dict[str, list[dict[str, str]]]]:
    rows = _palace_rows(raw_chart)
    star_map = _star_palace_map(rows)
    by_palace_name: dict[str, dict[str, list[dict[str, str]]]] = {
        str(row.get("name", "")): {"outbound": [], "inbound": []} for row in rows
    }

    for row in rows:
        source_name = str(row.get("name", ""))
        source_stem_key = str(row.get("heavenlyStemKey", ""))
        source_stem = _translate_stem(source_stem_key)
        source_branch = str(row.get("earthlyBranch", ""))
        if not source_stem_key:
            continue
        mutagen_stars = get_mutagen_stars(table_id, source_stem_key)
        outbound = by_palace_name[source_name]["outbound"]
        for index, star_key in enumerate(mutagen_stars):
            if index >= len(MUTAGEN_TYPES):
                break
            target = star_map.get(star_key)
            if not target:
                continue
            item = {
                "mutagen": MUTAGEN_TYPES[index],
                "star": _translate_star_name(star_key),
                "targetPalace": target["palaceName"],
                "targetBranch": target["palaceBranch"],
            }
            outbound.append(item)
            target_name = target["palaceName"]
            if target_name in by_palace_name:
                by_palace_name[target_name]["inbound"].append(
                    {
                        "mutagen": MUTAGEN_TYPES[index],
                        "star": _translate_star_name(star_key),
                        "sourcePalace": source_name,
                        "sourceStem": source_stem,
                        "sourceBranch": source_branch,
                    }
                )
    return by_palace_name
