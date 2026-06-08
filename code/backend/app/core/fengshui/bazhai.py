from __future__ import annotations

TRIGRAMS: dict[int, dict[str, str]] = {
    1: {"name": "坎", "alias": "坎卦", "direction": "北", "group": "dongsi"},
    2: {"name": "坤", "alias": "坤卦", "direction": "西南", "group": "xisi"},
    3: {"name": "震", "alias": "震卦", "direction": "东", "group": "dongsi"},
    4: {"name": "巽", "alias": "巽卦", "direction": "东南", "group": "dongsi"},
    6: {"name": "乾", "alias": "乾卦", "direction": "西北", "group": "xisi"},
    7: {"name": "兑", "alias": "兑卦", "direction": "西", "group": "xisi"},
    8: {"name": "艮", "alias": "艮卦", "direction": "东北", "group": "xisi"},
    9: {"name": "离", "alias": "离卦", "direction": "南", "group": "dongsi"},
}

DIRECTION_TYPES: dict[str, str] = {
    "fuWei": "伏位",
    "shengQi": "生气",
    "yanNian": "延年",
    "tianYi": "天医",
    "jueMing": "绝命",
    "wuGui": "五鬼",
    "liuSha": "六煞",
    "huoHai": "祸害",
}

# Ming gua direction layout (trigram numbers).
MING_GUA_DIRECTIONS: dict[int, dict[str, int]] = {
    1: {
        "fuWei": 1,
        "shengQi": 4,
        "yanNian": 9,
        "tianYi": 3,
        "jueMing": 2,
        "wuGui": 8,
        "liuSha": 7,
        "huoHai": 6,
    },
    2: {
        "fuWei": 2,
        "shengQi": 7,
        "yanNian": 6,
        "tianYi": 8,
        "jueMing": 3,
        "wuGui": 4,
        "liuSha": 9,
        "huoHai": 1,
    },
    3: {
        "fuWei": 3,
        "shengQi": 9,
        "yanNian": 1,
        "tianYi": 4,
        "jueMing": 7,
        "wuGui": 2,
        "liuSha": 8,
        "huoHai": 6,
    },
    4: {
        "fuWei": 4,
        "shengQi": 1,
        "yanNian": 9,
        "tianYi": 3,
        "jueMing": 8,
        "wuGui": 6,
        "liuSha": 2,
        "huoHai": 7,
    },
    6: {
        "fuWei": 6,
        "shengQi": 2,
        "yanNian": 8,
        "tianYi": 7,
        "jueMing": 9,
        "wuGui": 3,
        "liuSha": 1,
        "huoHai": 4,
    },
    7: {
        "fuWei": 7,
        "shengQi": 8,
        "yanNian": 2,
        "tianYi": 6,
        "jueMing": 4,
        "wuGui": 1,
        "liuSha": 9,
        "huoHai": 3,
    },
    8: {
        "fuWei": 8,
        "shengQi": 6,
        "yanNian": 7,
        "tianYi": 2,
        "jueMing": 1,
        "wuGui": 9,
        "liuSha": 3,
        "huoHai": 4,
    },
    9: {
        "fuWei": 9,
        "shengQi": 3,
        "yanNian": 1,
        "tianYi": 4,
        "jueMing": 6,
        "wuGui": 7,
        "liuSha": 2,
        "huoHai": 8,
    },
}

MOUNTAINS: list[dict[str, str]] = [
    {"id": "ren", "name": "壬", "trigram": "坎", "facing": "丙"},
    {"id": "zi", "name": "子", "trigram": "坎", "facing": "午"},
    {"id": "gui", "name": "癸", "trigram": "坎", "facing": "丁"},
    {"id": "chou", "name": "丑", "trigram": "艮", "facing": "未"},
    {"id": "gen", "name": "艮", "trigram": "艮", "facing": "坤"},
    {"id": "yin", "name": "寅", "trigram": "艮", "facing": "申"},
    {"id": "jia", "name": "甲", "trigram": "震", "facing": "庚"},
    {"id": "mao", "name": "卯", "trigram": "震", "facing": "酉"},
    {"id": "yi", "name": "乙", "trigram": "震", "facing": "辛"},
    {"id": "chen", "name": "辰", "trigram": "巽", "facing": "戌"},
    {"id": "xun", "name": "巽", "trigram": "巽", "facing": "乾"},
    {"id": "si", "name": "巳", "trigram": "巽", "facing": "亥"},
    {"id": "bing", "name": "丙", "trigram": "离", "facing": "壬"},
    {"id": "wu", "name": "午", "trigram": "离", "facing": "子"},
    {"id": "ding", "name": "丁", "trigram": "离", "facing": "癸"},
    {"id": "wei", "name": "未", "trigram": "坤", "facing": "丑"},
    {"id": "kun", "name": "坤", "trigram": "坤", "facing": "艮"},
    {"id": "shen", "name": "申", "trigram": "坤", "facing": "寅"},
    {"id": "geng", "name": "庚", "trigram": "兑", "facing": "甲"},
    {"id": "you", "name": "酉", "trigram": "兑", "facing": "卯"},
    {"id": "xin", "name": "辛", "trigram": "兑", "facing": "乙"},
    {"id": "xu", "name": "戌", "trigram": "乾", "facing": "辰"},
    {"id": "qian", "name": "乾", "trigram": "乾", "facing": "巽"},
    {"id": "hai", "name": "亥", "trigram": "乾", "facing": "巳"},
]

TRIGRAM_NAME_TO_NUMBER = {info["name"]: num for num, info in TRIGRAMS.items()}

AUSPICIOUS_TYPES = frozenset({"fuWei", "shengQi", "yanNian", "tianYi"})


def _digit_root(value: int) -> int:
    total = value
    while total > 9:
        total = sum(int(ch) for ch in str(total))
    return total


def calc_ming_gua_number(birth_year: int, gender: int) -> int:
    """BaZhai Ming Gua from birth year and gender (1=male, 0=female)."""
    if birth_year < 1000 or birth_year > 9999:
        raise ValueError("birthYear must be a four-digit year")
    root = _digit_root(birth_year)
    if gender == 1:
        value = 11 - root
        while value > 9:
            value -= 9
        if value == 5:
            return 2
        return value
    value = 4 + root
    while value > 9:
        value -= 9
    if value == 5:
        return 8
    return value


def resolve_mountain(mountain_id: str) -> dict[str, str]:
    key = mountain_id.strip().lower()
    for item in MOUNTAINS:
        if item["id"] == key or item["name"] == mountain_id.strip():
            return item
    raise ValueError(f"unknown sitting mountain: {mountain_id}")


def calc_zhai_gua_number(sitting_mountain: str) -> int:
    mountain = resolve_mountain(sitting_mountain)
    return TRIGRAM_NAME_TO_NUMBER[mountain["trigram"]]


def build_directions(ming_gua_number: int) -> list[dict[str, object]]:
    layout = MING_GUA_DIRECTIONS[ming_gua_number]
    rows: list[dict[str, object]] = []
    for key, label in DIRECTION_TYPES.items():
        trigram_number = layout[key]
        trigram = TRIGRAMS[trigram_number]
        rows.append(
            {
                "type": key,
                "label": label,
                "auspicious": key in AUSPICIOUS_TYPES,
                "trigram": trigram["name"],
                "direction": trigram["direction"],
            }
        )
    return rows


def build_palace_grid(ming_gua_number: int) -> list[dict[str, object]]:
    layout = MING_GUA_DIRECTIONS[ming_gua_number]
    by_trigram: dict[str, dict[str, object]] = {}
    for key, trigram_number in layout.items():
        trigram = TRIGRAMS[trigram_number]
        name = trigram["name"]
        entry = by_trigram.setdefault(
            name,
            {
                "name": name,
                "direction": trigram["direction"],
                "labels": [],
                "auspicious": True,
            },
        )
        entry["labels"].append(DIRECTION_TYPES[key])
        if key not in AUSPICIOUS_TYPES:
            entry["auspicious"] = False
    return list(by_trigram.values())


def is_compatible(ming_group: str, zhai_group: str) -> bool:
    return ming_group == zhai_group


def build_advice(
    *,
    compatible: bool,
    directions: list[dict[str, object]],
) -> list[str]:
    tips: list[str] = []
    if compatible:
        tips.append("命卦与宅卦同属东四或西四, 人宅相配, 宜按吉方布局。")
    else:
        tips.append("命卦与宅卦分属东四、西四, 人宅不配, 宜优先用命卦吉方调整床位与常用活动区。")

    by_label = {row["label"]: row for row in directions}
    door = by_label.get("生气") or by_label.get("延年")
    bed = by_label.get("天医") or by_label.get("伏位")
    stove = by_label.get("延年") or by_label.get("生气")
    if door:
        tips.append(
            f"大门或主入口宜朝{door['direction']}({door['label']}/{door['trigram']})取气。"
        )
    if bed:
        tips.append(
            f"卧室床头宜靠{bed['direction']}({bed['label']}/{bed['trigram']})方。"
        )
    if stove:
        tips.append(
            f"厨房灶位宜在{stove['direction']}({stove['label']}/{stove['trigram']})方。"
        )
    return tips


def list_mountains() -> list[dict[str, str]]:
    return [
        {
            "id": item["id"],
            "name": item["name"],
            "trigram": item["trigram"],
            "facing": item["facing"],
            "label": f"坐{item['name']}向{item['facing']}",
        }
        for item in MOUNTAINS
    ]
