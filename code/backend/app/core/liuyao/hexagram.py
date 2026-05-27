from __future__ import annotations

from app.core.liuyao.trigrams import lines_to_trigram, trigram_id

# (lower_trigram_id, upper_trigram_id) -> hexagram name
HEXAGRAM_NAMES: dict[tuple[int, int], str] = {
    (1, 1): "乾为天",
    (1, 2): "天泽履",
    (1, 3): "天火同人",
    (1, 4): "天雷无妄",
    (1, 5): "天风姤",
    (1, 6): "天水讼",
    (1, 7): "天山遁",
    (1, 8): "天地否",
    (2, 1): "泽天夬",
    (2, 2): "兑为泽",
    (2, 3): "泽火革",
    (2, 4): "泽雷随",
    (2, 5): "泽风大过",
    (2, 6): "泽水困",
    (2, 7): "泽山咸",
    (2, 8): "泽地萃",
    (3, 1): "火天大有",
    (3, 2): "火泽睽",
    (3, 3): "离为火",
    (3, 4): "火雷噬嗑",
    (3, 5): "火风鼎",
    (3, 6): "火水未济",
    (3, 7): "火山旅",
    (3, 8): "火地晋",
    (4, 1): "雷天大壮",
    (4, 2): "雷泽归妹",
    (4, 3): "雷火丰",
    (4, 4): "震为雷",
    (4, 5): "雷风恒",
    (4, 6): "雷水解",
    (4, 7): "雷山小过",
    (4, 8): "雷地豫",
    (5, 1): "风天小畜",
    (5, 2): "风泽中孚",
    (5, 3): "风火家人",
    (5, 4): "风雷益",
    (5, 5): "巽为风",
    (5, 6): "风水涣",
    (5, 7): "风山渐",
    (5, 8): "风地观",
    (6, 1): "水天需",
    (6, 2): "水泽节",
    (6, 3): "水火既济",
    (6, 4): "水雷屯",
    (6, 5): "水风井",
    (6, 6): "坎为水",
    (6, 7): "水山蹇",
    (6, 8): "水地比",
    (7, 1): "山天大畜",
    (7, 2): "山泽损",
    (7, 3): "山火贲",
    (7, 4): "山雷颐",
    (7, 5): "山风蛊",
    (7, 6): "山水蒙",
    (7, 7): "艮为山",
    (7, 8): "山地剥",
    (8, 1): "地天泰",
    (8, 2): "地泽临",
    (8, 3): "地火明夷",
    (8, 4): "地雷复",
    (8, 5): "地风升",
    (8, 6): "地水师",
    (8, 7): "地山谦",
    (8, 8): "坤为地",
}

# palace sequence index -> shi position (卜筮正宗 / 京房八宫)
PALACE_SHI: list[int] = [6, 1, 2, 3, 4, 5, 4, 3]

PALACE_HEXAGRAMS: dict[str, list[str]] = {
    "乾": ["乾为天", "天风姤", "天山遁", "天地否", "风地观", "山地剥", "火地晋", "火天大有"],
    "兑": ["兑为泽", "泽水困", "泽地萃", "泽山咸", "水山蹇", "地山谦", "雷山小过", "雷泽归妹"],
    "离": ["离为火", "火山旅", "火风鼎", "火水未济", "山水蒙", "风水涣", "天水讼", "天火同人"],
    "震": ["震为雷", "雷地豫", "雷水解", "雷风恒", "地风升", "水风井", "泽风大过", "泽雷随"],
    "巽": ["巽为风", "风天小畜", "风火家人", "风雷益", "天雷无妄", "火雷噬嗑", "山雷颐", "山风蛊"],
    "坎": ["坎为水", "水泽节", "水雷屯", "水火既济", "泽火革", "雷火丰", "地火明夷", "地水师"],
    "艮": ["艮为山", "山火贲", "山天大畜", "山泽损", "火泽睽", "天泽履", "风泽中孚", "风山渐"],
    "坤": ["坤为地", "地雷复", "地泽临", "地天泰", "雷天大壮", "泽天夬", "水天需", "水地比"],
}

NAME_TO_PALACE: dict[str, tuple[str, int]] = {}
for palace, names in PALACE_HEXAGRAMS.items():
    for idx, name in enumerate(names):
        NAME_TO_PALACE[name] = (palace, idx)


def apply_moving_lines(line_values: list[int]) -> list[int]:
    result: list[int] = []
    for value in line_values:
        if value == 9:
            result.append(8)
        elif value == 6:
            result.append(7)
        else:
            result.append(value)
    return result


def moving_line_positions(line_values: list[int]) -> list[int]:
    return [idx + 1 for idx, value in enumerate(line_values) if value in (6, 9)]


def hexagram_from_lines(line_values: list[int]) -> tuple[str, str, str, str, int, int]:
    if len(line_values) != 6:
        raise ValueError("hexagram requires 6 lines")
    lower = lines_to_trigram(line_values[:3])
    upper = lines_to_trigram(line_values[3:])
    lower_id = trigram_id(lower)
    upper_id = trigram_id(upper)
    name = HEXAGRAM_NAMES[(lower_id, upper_id)]
    palace, seq_idx = NAME_TO_PALACE[name]
    shi = PALACE_SHI[seq_idx]
    ying = shi + 3 if shi + 3 <= 6 else shi - 3
    return name, lower, upper, palace, shi, ying


def build_changed_lines(line_values: list[int]) -> list[int] | None:
    if not moving_line_positions(line_values):
        return None
    return apply_moving_lines(line_values)
