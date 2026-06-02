from __future__ import annotations

from typing import Any

from app.core.ziwei.calendar_bridge import ZiweiCalendarContext
from app.core.ziwei.rules import ZiweiRules

_PALACE_KEY_TO_ZH: dict[str, str] = {
    "soulPalace": "命宫",
    "parentsPalace": "父母",
    "spiritPalace": "福德",
    "propertyPalace": "田宅",
    "careerPalace": "官禄",
    "friendsPalace": "交友",
    "surfacePalace": "迁移",
    "healthPalace": "疾厄",
    "wealthPalace": "财帛",
    "childrenPalace": "子女",
    "spousePalace": "夫妻",
    "siblingsPalace": "兄弟",
}


def _translate_palace_key(key: str) -> str:
    if key in _PALACE_KEY_TO_ZH:
        return _PALACE_KEY_TO_ZH[key]
    if key.endswith("Palace"):
        return _PALACE_KEY_TO_ZH.get(key, key)
    return key


def _translate_stem_branch(raw: str) -> str:
    if not raw:
        return raw
    if len(raw) == 1:
        return raw
    try:
        from iztro_py.i18n import t
    except ImportError:
        return raw
    if "Heavenly" in raw:
        return t(f"heavenlyStem.{raw}")
    if "Earthly" in raw:
        return t(f"earthlyBranch.{raw}")
    return t(raw)


def _star_row(star: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": star.get("name", ""),
        "type": star.get("type", ""),
        "brightness": star.get("brightness"),
        "mutagen": star.get("mutagen"),
    }


def _normalize_palaces(raw_palaces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    soul_idx = 0
    for idx, palace in enumerate(raw_palaces):
        if palace.get("name") == "命宫" or "命" in str(palace.get("name", "")):
            soul_idx = idx
            break
    ordered = raw_palaces[soul_idx:] + raw_palaces[:soul_idx]
    out: list[dict[str, Any]] = []
    for i, palace in enumerate(ordered):
        decadal = palace.get("decadal") or {}
        age_range = decadal.get("range")
        if isinstance(age_range, (list, tuple)) and len(age_range) == 2:
            age_label = f"{age_range[0]}-{age_range[1]}"
        else:
            age_label = ""
        out.append(
            {
                "index": i,
                "name": palace.get("name", ""),
                "stemBranch": f"{palace.get('heavenlyStem', '')}{palace.get('earthlyBranch', '')}",
                "heavenlyStem": palace.get("heavenlyStem", ""),
                "earthlyBranch": palace.get("earthlyBranch", ""),
                "isBody": bool(palace.get("isBodyPalace")),
                "majorStars": [_star_row(s) for s in palace.get("majorStars") or []],
                "minorStars": [_star_row(s) for s in palace.get("minorStars") or []],
                "adjStars": [_star_row(s) for s in palace.get("adjectiveStars") or []],
                "decadalRange": age_label,
                "minorAges": palace.get("ages") or [],
            }
        )
    return out


def _build_decadal_list(palaces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    for palace in palaces:
        label = palace.get("decadalRange") or ""
        if not label or label in seen:
            continue
        seen.add(label)
        parts = label.split("-")
        start = int(parts[0]) if parts and parts[0].isdigit() else 0
        rows.append(
            {
                "ageRange": label,
                "palace": palace.get("name", ""),
                "stemBranch": palace.get("stemBranch", ""),
                "startAge": start,
            }
        )
    rows.sort(key=lambda r: r.get("startAge", 0))
    for i, row in enumerate(rows):
        row["index"] = i
    return rows


def _build_minor_list(palaces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    age_map: dict[int, dict[str, Any]] = {}
    for palace in palaces:
        for age in palace.get("minorAges") or []:
            if isinstance(age, int) and age not in age_map:
                age_map[age] = {
                    "age": age,
                    "palace": palace.get("name", ""),
                    "stemBranch": palace.get("stemBranch", ""),
                }
    return [age_map[k] for k in sorted(age_map)]


def _horoscope_scope(scope: dict[str, Any] | None, target_year: int) -> dict[str, Any]:
    if not scope:
        return {"targetYear": target_year}
    palace_names = [
        _translate_palace_key(name) for name in (scope.get("palace_names") or [])
    ]
    mutagens = scope.get("mutagen") or []
    try:
        from iztro_py.i18n import t

        mutagen_labels = [t(m) if isinstance(m, str) else str(m) for m in mutagens]
    except ImportError:
        mutagen_labels = [str(m) for m in mutagens]
    stem = _translate_stem_branch(str(scope.get("heavenly_stem", "")))
    branch = _translate_stem_branch(str(scope.get("earthly_branch", "")))
    return {
        "targetYear": target_year,
        "name": scope.get("name", ""),
        "heavenlyStem": stem,
        "earthlyBranch": branch,
        "stemBranch": f"{stem}{branch}",
        "palaceNames": palace_names,
        "mutagens": mutagen_labels,
    }


def _palaces_from_chart(raw_chart: Any) -> list[dict[str, Any]]:
    iztro_dict = raw_chart.to_iztro_dict()
    zh_list = iztro_dict.get("palaces") or []
    merged: list[dict[str, Any]] = []
    for idx, palace_obj in enumerate(raw_chart.palaces):
        row = palace_obj.model_dump() if hasattr(palace_obj, "model_dump") else {}
        zh = zh_list[idx] if idx < len(zh_list) else {}
        decadal = row.get("decadal") or {}
        merged.append(
            {
                "name": zh.get("name", _translate_palace_key(str(row.get("name", "")))),
                "heavenlyStem": zh.get("heavenlyStem", ""),
                "earthlyBranch": zh.get("earthlyBranch", ""),
                "isBodyPalace": zh.get("isBodyPalace", row.get("is_body_palace")),
                "majorStars": zh.get("majorStars") or [],
                "minorStars": zh.get("minorStars") or [],
                "adjectiveStars": zh.get("adjectiveStars") or [],
                "decadal": decadal,
                "ages": row.get("ages") or [],
            }
        )
    return merged


def normalize_chart(
    raw_chart: Any,
    horoscope: Any,
    ctx: ZiweiCalendarContext,
    data_dict: dict[str, Any],
    rules: ZiweiRules,
    target_year: int,
) -> dict[str, Any]:
    iztro_dict = raw_chart.to_iztro_dict()
    palaces = _normalize_palaces(_palaces_from_chart(raw_chart))
    hdump = horoscope.model_dump() if hasattr(horoscope, "model_dump") else {}

    warnings = rules.warnings()
    return {
        "input": data_dict,
        "rulesMeta": {**rules.as_meta(), "warnings": warnings, **ctx.rules_applied},
        "trueSolarTime": ctx.true_solar_time,
        "solarLabel": ctx.solar_label,
        "lunarLabel": ctx.lunar_label,
        "fourPillars": ctx.four_pillars,
        "meta": {
            "bureau": iztro_dict.get("fiveElementsClass", ""),
            "soul": iztro_dict.get("soul", ""),
            "body": iztro_dict.get("body", ""),
            "soulPalaceBranch": iztro_dict.get("earthlyBranchOfSoulPalace", ""),
            "bodyPalaceBranch": iztro_dict.get("earthlyBranchOfBodyPalace", ""),
            "gender": iztro_dict.get("gender", ""),
            "zodiac": iztro_dict.get("zodiac", ""),
            "sign": iztro_dict.get("sign", ""),
            "chineseDate": iztro_dict.get("chineseDate", ""),
            "time": iztro_dict.get("time", ""),
            "timeRange": iztro_dict.get("timeRange", ""),
        },
        "palaces": palaces,
        "limits": {
            "decadal": _build_decadal_list(palaces),
            "minor": _build_minor_list(palaces),
            "yearly": _horoscope_scope(hdump.get("yearly"), target_year),
            "current": {
                "decadal": _horoscope_scope(hdump.get("decadal"), target_year),
                "minor": _horoscope_scope(hdump.get("age"), target_year),
                "nominalAge": hdump.get("nominal_age"),
            },
        },
    }
