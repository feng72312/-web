from __future__ import annotations

from typing import Any

from app.core.ziwei.calendar_bridge import ZiweiCalendarContext
from app.core.ziwei.chart_enrich import enrich_chart
from app.core.ziwei.feixing import compute_flying_mutagens
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

BRANCH_GRID_POSITIONS: dict[str, dict[str, int | str]] = {
    "巳": {"row": 1, "col": 1, "branch": "巳"},
    "午": {"row": 1, "col": 2, "branch": "午"},
    "未": {"row": 1, "col": 3, "branch": "未"},
    "申": {"row": 1, "col": 4, "branch": "申"},
    "辰": {"row": 2, "col": 1, "branch": "辰"},
    "酉": {"row": 2, "col": 4, "branch": "酉"},
    "卯": {"row": 3, "col": 1, "branch": "卯"},
    "戌": {"row": 3, "col": 4, "branch": "戌"},
    "寅": {"row": 4, "col": 1, "branch": "寅"},
    "丑": {"row": 4, "col": 2, "branch": "丑"},
    "子": {"row": 4, "col": 3, "branch": "子"},
    "亥": {"row": 4, "col": 4, "branch": "亥"},
}

TRIAD_GROUPS: list[tuple[str, ...]] = [
    ("申", "子", "辰"),
    ("寅", "午", "戌"),
    ("巳", "酉", "丑"),
    ("亥", "卯", "未"),
]

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

MALEFIC_STAR_NAMES: frozenset[str] = frozenset(
    {
        "擎羊",
        "陀罗",
        "火星",
        "铃星",
        "地空",
        "地劫",
        "天空",
        "天刑",
        "大耗",
        "劫煞",
        "灾煞",
        "天姚",
        "天哭",
        "天虚",
        "阴煞",
        "白虎",
        "贯索",
    }
)

MUTAGEN_LABELS: tuple[str, ...] = ("禄", "权", "科", "忌")


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


def _translate_star_name(raw: str) -> str:
    if not raw:
        return raw
    try:
        from iztro_py.i18n import t

        return t(raw) if isinstance(raw, str) else str(raw)
    except ImportError:
        return str(raw)


def _palace_position(branch: str) -> dict[str, int | str]:
    if not branch:
        return {}
    return dict(BRANCH_GRID_POSITIONS.get(branch, {}))


def _opposite_branch(branch: str) -> str:
    if not branch:
        return ""
    return OPPOSITE_BRANCHES.get(branch, "")


def _triad_branches(branch: str) -> list[str]:
    if not branch:
        return []
    for group in TRIAD_GROUPS:
        if branch in group:
            return [item for item in group if item != branch]
    return []


def _star_row(star: dict[str, Any], group: str = "") -> dict[str, Any]:
    row = {
        "name": star.get("name", ""),
        "type": star.get("type", ""),
        "brightness": star.get("brightness"),
        "mutagen": star.get("mutagen"),
    }
    if group:
        row["group"] = group
    return row


def _star_groups(palace: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return {
        "major": [_star_row(s, "major") for s in palace.get("majorStars") or []],
        "minor": [_star_row(s, "minor") for s in palace.get("minorStars") or []],
        "adj": [_star_row(s, "adj") for s in palace.get("adjectiveStars") or []],
    }


def _mutagen_stars_from_groups(groups: dict[str, list[dict[str, Any]]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for group_name, stars in groups.items():
        for star in stars:
            mutagen = star.get("mutagen")
            if mutagen:
                rows.append(
                    {
                        "name": str(star.get("name", "")),
                        "mutagen": str(mutagen),
                        "group": group_name,
                    }
                )
    return rows


def _has_malefic(groups: dict[str, list[dict[str, Any]]]) -> bool:
    for stars in groups.values():
        for star in stars:
            name = str(star.get("name", ""))
            if name in MALEFIC_STAR_NAMES:
                return True
    return False


def _brightness_summary(groups: dict[str, list[dict[str, Any]]]) -> str:
    parts: list[str] = []
    for star in groups.get("major") or []:
        brightness = star.get("brightness")
        if brightness:
            parts.append(f"{star.get('name', '')}{brightness}")
    return " ".join(parts)


def _scope_mutagen_stars(scope: dict[str, Any] | None) -> list[dict[str, str]]:
    if not scope:
        return []
    raw_mutagens = scope.get("mutagen") or []
    rows: list[dict[str, str]] = []
    for index, raw in enumerate(raw_mutagens):
        label = MUTAGEN_LABELS[index] if index < len(MUTAGEN_LABELS) else str(index + 1)
        rows.append({"name": _translate_star_name(str(raw)), "mutagen": label, "group": "scope"})
    return rows


def _normalize_palaces(
    raw_palaces: list[dict[str, Any]],
    *,
    soul_palace_branch: str = "",
    body_palace_branch: str = "",
    detail_level: str = "simple",
    flying_by_name: dict[str, dict[str, list[dict[str, str]]]] | None = None,
) -> list[dict[str, Any]]:
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
        branch = str(palace.get("earthlyBranch", ""))
        groups = _star_groups(palace)
        is_body = bool(palace.get("isBodyPalace")) or (
            bool(body_palace_branch) and branch == body_palace_branch
        )
        is_soul = palace.get("name") == "命宫" or (
            bool(soul_palace_branch) and branch == soul_palace_branch
        )
        if detail_level == "simple":
            out.append(
                {
                    "index": i,
                    "name": palace.get("name", ""),
                    "stemBranch": f"{palace.get('heavenlyStem', '')}{branch}",
                    "heavenlyStem": palace.get("heavenlyStem", ""),
                    "earthlyBranch": branch,
                    "isBody": is_body,
                    "isSoul": is_soul,
                    "position": _palace_position(branch),
                    "majorStars": groups["major"],
                    "minorStars": [],
                    "adjStars": [],
                    "decadalRange": age_label,
                    "minorAges": [],
                }
            )
        else:
            palace_name = str(palace.get("name", ""))
            flying = (flying_by_name or {}).get(palace_name)
            row = {
                "index": i,
                "name": palace_name,
                "stemBranch": f"{palace.get('heavenlyStem', '')}{branch}",
                "heavenlyStem": palace.get("heavenlyStem", ""),
                "earthlyBranch": branch,
                "isBody": is_body,
                "isSoul": is_soul,
                "position": _palace_position(branch),
                "oppositeBranch": _opposite_branch(branch),
                "triadBranches": _triad_branches(branch),
                "majorStars": groups["major"],
                "minorStars": groups["minor"],
                "adjStars": groups["adj"],
                "starGroups": groups,
                "mutagenStars": _mutagen_stars_from_groups(groups),
                "hasMalefic": _has_malefic(groups),
                "brightnessSummary": _brightness_summary(groups),
                "decadalRange": age_label,
                "minorAges": palace.get("ages") or [],
            }
            if flying:
                row["flyingMutagens"] = flying
            out.append(row)
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


def _horoscope_scope(
    scope: dict[str, Any] | None,
    target_year: int,
    *,
    layer: str,
) -> dict[str, Any]:
    if not scope:
        return {
            "layer": layer,
            "available": False,
            "reason": "当前运限层暂无数据",
            "targetYear": target_year,
        }
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
        "layer": layer,
        "available": True,
        "targetYear": target_year,
        "name": scope.get("name", ""),
        "heavenlyStem": stem,
        "earthlyBranch": branch,
        "stemBranch": f"{stem}{branch}",
        "palaceNames": palace_names,
        "palaceBranches": [],
        "mutagens": mutagen_labels,
        "mutagenStars": _scope_mutagen_stars(scope),
    }


def _unavailable_limit_layer(layer: str, target_year: int, reason: str = "请切换专业排盘查看") -> dict[str, Any]:
    return {
        "layer": layer,
        "available": False,
        "reason": reason,
        "targetYear": target_year,
    }


def _build_active_limits(hdump: dict[str, Any], target_year: int) -> dict[str, Any]:
    decadal_scope = _horoscope_scope(hdump.get("decadal"), target_year, layer="decadal")
    yearly_scope = _horoscope_scope(hdump.get("yearly"), target_year, layer="yearly")
    monthly_scope = _horoscope_scope(hdump.get("monthly"), target_year, layer="monthly")
    daily_scope = _horoscope_scope(hdump.get("daily"), target_year, layer="daily")
    hourly_scope = _horoscope_scope(hdump.get("hourly"), target_year, layer="hourly")
    return {
        "decadal": decadal_scope,
        "yearly": yearly_scope,
        "monthly": monthly_scope,
        "daily": daily_scope,
        "hourly": hourly_scope,
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
    horoscope: Any | None,
    ctx: ZiweiCalendarContext,
    data_dict: dict[str, Any],
    rules: ZiweiRules,
    target_year: int,
    *,
    detail_level: str = "simple",
) -> dict[str, Any]:
    iztro_dict = raw_chart.to_iztro_dict()
    soul_branch = str(iztro_dict.get("earthlyBranchOfSoulPalace", ""))
    body_branch = str(iztro_dict.get("earthlyBranchOfBodyPalace", ""))
    flying_by_name: dict[str, dict[str, list[dict[str, str]]]] = {}
    if rules.chart_school == "feixing" and detail_level == "pro":
        flying_by_name = compute_flying_mutagens(raw_chart, rules.mutagen_table)
    palaces = _normalize_palaces(
        _palaces_from_chart(raw_chart),
        soul_palace_branch=soul_branch,
        body_palace_branch=body_branch,
        detail_level=detail_level,
        flying_by_name=flying_by_name,
    )
    warnings = rules.warnings()
    decadal_list = _build_decadal_list(palaces)
    minor_list = _build_minor_list(palaces)
    if horoscope is None:
        yearly_scope = _unavailable_limit_layer("yearly", target_year)
        active = {
            "decadal": _unavailable_limit_layer("decadal", target_year),
            "yearly": yearly_scope,
            "monthly": _unavailable_limit_layer("monthly", target_year),
            "daily": _unavailable_limit_layer("daily", target_year),
            "hourly": _unavailable_limit_layer("hourly", target_year),
        }
        limits = {
            "decadal": decadal_list,
            "minor": minor_list,
            "yearly": yearly_scope,
            "current": {
                "decadal": _unavailable_limit_layer("decadal", target_year),
                "minor": _unavailable_limit_layer("minor", target_year),
                "nominalAge": None,
            },
            "active": active,
        }
    else:
        hdump = horoscope.model_dump() if hasattr(horoscope, "model_dump") else {}
        active = _build_active_limits(hdump, target_year)
        limits = {
            "decadal": decadal_list,
            "minor": minor_list,
            "yearly": _horoscope_scope(hdump.get("yearly"), target_year, layer="yearly"),
            "current": {
                "decadal": _horoscope_scope(hdump.get("decadal"), target_year, layer="decadal"),
                "minor": _horoscope_scope(hdump.get("age"), target_year, layer="minor"),
                "nominalAge": hdump.get("nominal_age"),
            },
            "active": active,
        }
    payload = {
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
            "soulPalaceBranch": soul_branch,
            "bodyPalaceBranch": body_branch,
            "gender": iztro_dict.get("gender", ""),
            "zodiac": iztro_dict.get("zodiac", ""),
            "sign": iztro_dict.get("sign", ""),
            "chineseDate": iztro_dict.get("chineseDate", ""),
            "time": iztro_dict.get("time", ""),
            "timeRange": iztro_dict.get("timeRange", ""),
            "detailLevel": detail_level,
            "chartSchool": rules.chart_school,
        },
        "palaces": palaces,
        "limits": limits,
    }
    if detail_level == "pro":
        return enrich_chart(payload)
    return payload
