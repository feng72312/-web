from __future__ import annotations

from app.core.liuyao.trigrams import PALACE_ELEMENT

TRIGRAM_NA_JIA: dict[str, dict[str, list[tuple[str, str]]]] = {
    "乾": {
        "inner": [("甲", "子"), ("甲", "寅"), ("甲", "辰")],
        "outer": [("壬", "午"), ("壬", "申"), ("壬", "戌")],
    },
    "坤": {
        "inner": [("乙", "未"), ("乙", "巳"), ("乙", "卯")],
        "outer": [("癸", "丑"), ("癸", "亥"), ("癸", "酉")],
    },
    "震": {
        "inner": [("庚", "子"), ("庚", "寅"), ("庚", "辰")],
        "outer": [("庚", "午"), ("庚", "申"), ("庚", "戌")],
    },
    "巽": {
        "inner": [("辛", "丑"), ("辛", "亥"), ("辛", "酉")],
        "outer": [("辛", "未"), ("辛", "巳"), ("辛", "卯")],
    },
    "坎": {
        "inner": [("戊", "寅"), ("戊", "辰"), ("戊", "午")],
        "outer": [("戊", "申"), ("戊", "戌"), ("戊", "子")],
    },
    "离": {
        "inner": [("己", "卯"), ("己", "丑"), ("己", "亥")],
        "outer": [("己", "酉"), ("己", "未"), ("己", "巳")],
    },
    "艮": {
        "inner": [("丙", "辰"), ("丙", "午"), ("丙", "申")],
        "outer": [("丙", "戌"), ("丙", "子"), ("丙", "寅")],
    },
    "兑": {
        "inner": [("丁", "巳"), ("丁", "卯"), ("丁", "丑")],
        "outer": [("丁", "亥"), ("丁", "酉"), ("丁", "未")],
    },
}

GENERATES = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
CONTROLS = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

BRANCH_ELEMENT = {
    "子": "水",
    "丑": "土",
    "寅": "木",
    "卯": "木",
    "辰": "土",
    "巳": "火",
    "午": "火",
    "未": "土",
    "申": "金",
    "酉": "金",
    "戌": "土",
    "亥": "水",
}


def _generates(source: str, target: str) -> bool:
    return GENERATES.get(source) == target


def _controls(source: str, target: str) -> bool:
    return CONTROLS.get(source) == target


def liuqin_for_branch(palace: str, branch: str) -> str:
    palace_elem = PALACE_ELEMENT[palace]
    line_elem = BRANCH_ELEMENT[branch]
    if palace_elem == line_elem:
        return "兄弟"
    if _generates(line_elem, palace_elem):
        return "父母"
    if _generates(palace_elem, line_elem):
        return "子孙"
    if _controls(line_elem, palace_elem):
        return "官鬼"
    if _controls(palace_elem, line_elem):
        return "妻财"
    return "兄弟"


def najia_stems_branches(lower: str, upper: str) -> list[tuple[str, str]]:
    inner = TRIGRAM_NA_JIA[lower]["inner"]
    outer = TRIGRAM_NA_JIA[upper]["outer"]
    return inner + outer


def build_palace_liuqin_map(palace: str) -> dict[str, str]:
    pure_inner = TRIGRAM_NA_JIA[palace]["inner"]
    pure_outer = TRIGRAM_NA_JIA[palace]["outer"]
    mapping: dict[str, str] = {}
    for _, branch in pure_inner + pure_outer:
        mapping[liuqin_for_branch(palace, branch)] = branch
    return mapping


def resolve_fu_shen(
    palace: str,
    present: dict[str, str],
) -> dict[int, dict[str, str]]:
    full = build_palace_liuqin_map(palace)
    missing = [name for name in ("父母", "兄弟", "子孙", "妻财", "官鬼") if name not in present]
    if not missing:
        return {}
    # MVP: attach missing liuqin as fuShen note on shi line only when single missing
    return {}
