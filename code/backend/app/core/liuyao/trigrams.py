from __future__ import annotations

TRIGRAM_IDS: dict[int, str] = {
    1: "乾",
    2: "兑",
    3: "离",
    4: "震",
    5: "巽",
    6: "坎",
    7: "艮",
    8: "坤",
}

TRIGRAM_TO_ID: dict[str, int] = {name: idx for idx, name in TRIGRAM_IDS.items()}

# bits bottom -> top: yang=1 yin=0
BIT_TO_TRIGRAM: dict[tuple[int, int, int], str] = {
    (1, 1, 1): "乾",
    (1, 1, 0): "兑",
    (1, 0, 1): "离",
    (1, 0, 0): "震",
    (0, 1, 1): "巽",
    (0, 1, 0): "坎",
    (0, 0, 1): "艮",
    (0, 0, 0): "坤",
}

PALACE_ELEMENT: dict[str, str] = {
    "乾": "金",
    "兑": "金",
    "离": "火",
    "震": "木",
    "巽": "木",
    "坎": "水",
    "坤": "土",
    "艮": "土",
}


def mod8(value: int) -> int:
    remainder = value % 8
    return 8 if remainder == 0 else remainder


def mod6(value: int) -> int:
    remainder = value % 6
    return 6 if remainder == 0 else remainder


def trigram_id(name: str) -> int:
    return TRIGRAM_TO_ID[name]


def lines_to_trigram(line_values: list[int]) -> str:
    bits: list[int] = []
    for value in line_values:
        bits.append(1 if value in (7, 9) else 0)
    return BIT_TO_TRIGRAM[(bits[0], bits[1], bits[2])]


def trigram_to_yao_values(trigram: str) -> list[int]:
    for bits, name in BIT_TO_TRIGRAM.items():
        if name == trigram:
            return [7 if bit == 1 else 8 for bit in bits]
    raise KeyError(f"unknown trigram: {trigram}")
