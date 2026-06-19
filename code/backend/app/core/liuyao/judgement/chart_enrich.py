from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.core.liuyao.hexagram import (
    build_changed_lines,
    hexagram_from_lines,
    moving_line_positions,
)
from app.core.liuyao.judgement.wuxing import (
    branch_element,
    element_relation,
    is_in_xun_kong,
    is_liu_chong_hexagram,
    is_yue_po,
)
from app.core.liuyao.liushen import liushen_for_day
from app.core.liuyao.najia import liuqin_for_branch, najia_stems_branches
from app.core.liuyao.trigrams import PALACE_ELEMENT


def _line_by_position(chart: dict[str, Any], position: int) -> dict[str, Any] | None:
    for line in chart.get("lines") or []:
        if int(line.get("position", 0)) == position:
            return line
    return None


def _build_bian_lines(chart: dict[str, Any]) -> list[dict[str, Any]] | None:
    line_values = (chart.get("meta") or {}).get("lineValues")
    if not line_values or len(line_values) != 6:
        return None
    changed_values = build_changed_lines(line_values)
    if not changed_values:
        return None
    name, lower, upper, palace, shi, ying = hexagram_from_lines(changed_values)
    stems_branches = najia_stems_branches(lower, upper)
    day_gan = str(chart.get("dayGan") or "")
    liushen = liushen_for_day(day_gan)
    rows: list[dict[str, Any]] = []
    for idx, value in enumerate(changed_values):
        stem, branch = stems_branches[idx]
        rows.append(
            {
                "position": idx + 1,
                "value": value,
                "isMoving": False,
                "isYang": value in (7, 9),
                "branch": branch,
                "stem": stem,
                "liuqin": liuqin_for_branch(palace, branch),
                "liushen": liushen[idx],
                "isShi": idx + 1 == shi,
                "isYing": idx + 1 == ying,
            }
        )
    return rows


def _dong_bian_target(
    line: dict[str, Any],
    bian_lines: list[dict[str, Any]] | None,
) -> dict[str, Any] | None:
    if not line.get("isMoving") or not bian_lines:
        return None
    pos = int(line.get("position", 0))
    target = _line_by_position({"lines": bian_lines}, pos)
    if not target:
        return None
    ben_elem = branch_element(str(line.get("branch") or ""))
    bian_elem = branch_element(str(target.get("branch") or ""))
    relation = element_relation(ben_elem, bian_elem)
    huitou = ""
    if relation == "generates":
        huitou = "化回头生"
    elif relation == "controls":
        huitou = "化回头克"
    elif relation == "generated_by":
        huitou = "化回头泄"
    elif relation == "controlled_by":
        huitou = "化回头耗"
    elif relation == "same":
        huitou = "化进退同气"
    return {
        "position": pos,
        "branch": target.get("branch"),
        "liuqin": target.get("liuqin"),
        "relation": relation,
        "huitou": huitou,
    }


def enrich_line(
    line: dict[str, Any],
    chart: dict[str, Any],
    *,
    bian_lines: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    month_jian = str(chart.get("monthJian") or "")
    day_gan = str(chart.get("dayGan") or "")
    day_chen = str(chart.get("dayChen") or "")
    branch = str(line.get("branch") or "")
    line_elem = branch_element(branch)
    month_elem = branch_element(month_jian)
    day_elem = branch_element(day_chen)
    month_rel = element_relation(month_elem, line_elem)
    day_rel = element_relation(day_elem, line_elem)
    strength = "neutral"
    if month_rel in {"same", "generates"}:
        strength = "strong"
    elif month_rel == "generated_by":
        strength = "medium"
    elif month_rel in {"controls", "controlled_by"}:
        strength = "weak"
    yue_po = is_yue_po(branch, month_jian)
    xun_kong = is_in_xun_kong(branch, day_gan, day_chen)
    if yue_po:
        strength = "weak"
    if xun_kong:
        strength = "weak" if strength != "strong" else "medium"
    dong_bian = _dong_bian_target(line, bian_lines)
    risk_flags: list[str] = []
    if yue_po:
        risk_flags.append("yue_po")
    if xun_kong:
        risk_flags.append("xun_kong")
    if dong_bian and dong_bian.get("huitou") == "化回头克":
        risk_flags.append("huitou_ke")
    return {
        **line,
        "lineStrength": strength,
        "monthRelation": month_rel,
        "dayRelation": day_rel,
        "kongPoState": {
            "xunKong": xun_kong,
            "yuePo": yue_po,
        },
        "dongBianTarget": dong_bian,
        "riskFlags": risk_flags,
    }


def enrich_chart_for_judgement(chart: dict[str, Any]) -> dict[str, Any]:
    payload = deepcopy(chart)
    bian_lines = _build_bian_lines(payload)
    if bian_lines:
        payload["bianLines"] = bian_lines
    enriched_lines = [
        enrich_line(line, payload, bian_lines=bian_lines)
        for line in payload.get("lines") or []
    ]
    payload["lines"] = enriched_lines
    ben = payload.get("benGua") or {}
    bian = payload.get("bianGua") or {}
    payload["riskFlags"] = {
        "benLiuChong": is_liu_chong_hexagram(
            str(ben.get("lower") or ""),
            str(ben.get("upper") or ""),
            str(ben.get("name") or ""),
        ),
        "bianLiuChong": is_liu_chong_hexagram(
            str(bian.get("lower") or ""),
            str(bian.get("upper") or ""),
            str(bian.get("name") or ""),
        )
        if bian
        else False,
        "movingCount": len(payload.get("movingLines") or []),
    }
    payload["palaceElement"] = str(ben.get("palaceElement") or PALACE_ELEMENT.get(str(ben.get("palace") or ""), ""))
    line_values = (payload.get("meta") or {}).get("lineValues")
    if line_values:
        payload.setdefault("meta", {})["movingPositions"] = moving_line_positions(line_values)
    return payload
