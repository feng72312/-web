from __future__ import annotations

from app.core.liuyao.hexagram import (
    HEXAGRAM_NAMES,
    apply_moving_lines,
    hexagram_from_lines,
    moving_line_positions,
)
from app.core.liuyao.trigrams import PALACE_ELEMENT, lines_to_trigram, trigram_id
from app.core.meihua.models import BenGuaInfo, MeihuaLine, TrigramInfo

GENERATES = {
    "木": "火",
    "火": "土",
    "土": "金",
    "金": "水",
    "水": "木",
}

CONTROLS = {
    "木": "土",
    "土": "水",
    "水": "火",
    "火": "金",
    "金": "木",
}


def _trigram_info(name: str) -> TrigramInfo:
    return TrigramInfo(name=name, element=PALACE_ELEMENT[name])


def _ben_from_lines(line_values: list[int]) -> BenGuaInfo:
    name, lower, upper, _, _, _ = hexagram_from_lines(line_values)
    return BenGuaInfo(
        name=name,
        lower=lower,
        upper=upper,
        lower_element=PALACE_ELEMENT[lower],
        upper_element=PALACE_ELEMENT[upper],
    )


def _relation(ti_element: str, yong_element: str) -> str:
    if ti_element == yong_element:
        return "比和"
    if GENERATES.get(ti_element) == yong_element:
        return "体生用"
    if GENERATES.get(yong_element) == ti_element:
        return "用生体"
    if CONTROLS.get(ti_element) == yong_element:
        return "体克用"
    if CONTROLS.get(yong_element) == ti_element:
        return "用克体"
    return "体用关系待辨"


def _build_lines(line_values: list[int]) -> list[MeihuaLine]:
    rows: list[MeihuaLine] = []
    for idx, value in enumerate(line_values):
        position = idx + 1
        rows.append(
            MeihuaLine(
                position=position,
                value=value,
                is_moving=value in (6, 9),
                is_yang=value in (7, 9),
                in_lower=position <= 3,
            )
        )
    return rows


def _mutual_gua(line_values: list[int]) -> BenGuaInfo | None:
    if len(line_values) != 6:
        return None
    lower_bits = line_values[1:4]
    upper_bits = line_values[2:5]
    lower = lines_to_trigram(lower_bits)
    upper = lines_to_trigram(upper_bits)
    lower_id = trigram_id(lower)
    upper_id = trigram_id(upper)
    name = HEXAGRAM_NAMES.get((lower_id, upper_id), f"{upper}{lower}")
    return BenGuaInfo(
        name=name,
        lower=lower,
        upper=upper,
        lower_element=PALACE_ELEMENT[lower],
        upper_element=PALACE_ELEMENT[upper],
    )


def resolve_ti_yong(
    line_values: list[int],
    *,
    moving_override: int | None = None,
) -> tuple[TrigramInfo, TrigramInfo, list[int], bool, dict[str, object]]:
    moving = moving_line_positions(line_values)
    meta: dict[str, object] = {}

    if moving_override is not None:
        if moving_override < 1 or moving_override > 6:
            raise ValueError("movingPositionOverride must be 1-6")
        moving = [moving_override]
        meta["movingOverride"] = moving_override

    _, lower_name, upper_name, _, _, _ = hexagram_from_lines(line_values)

    if not moving:
        meta["staticRule"] = "lower_ti_upper_yong"
        return (
            _trigram_info(lower_name),
            _trigram_info(upper_name),
            [],
            True,
            meta,
        )

    if len(moving) > 1:
        meta["multiMoving"] = True
    primary = min(moving)
    meta["primaryMoving"] = primary

    if primary <= 3:
        meta["rule"] = "moving_in_lower"
        return _trigram_info(upper_name), _trigram_info(lower_name), moving, False, meta

    meta["rule"] = "moving_in_upper"
    return _trigram_info(lower_name), _trigram_info(upper_name), moving, False, meta


def build_chart_parts(
    line_values: list[int],
    *,
    moving_override: int | None = None,
) -> dict:
    ti, yong, moving, is_static, ti_meta = resolve_ti_yong(
        line_values, moving_override=moving_override
    )
    ben = _ben_from_lines(line_values)
    bian = None
    if moving:
        changed = apply_moving_lines(line_values)
        bian = _ben_from_lines(changed)

    relation = _relation(ti.element, yong.element)
    return {
        "ben": ben,
        "bian": bian,
        "lines": _build_lines(line_values),
        "moving": moving,
        "ti": ti,
        "yong": yong,
        "relation": relation,
        "hu": _mutual_gua(line_values),
        "is_static": is_static,
        "ti_meta": ti_meta,
    }
