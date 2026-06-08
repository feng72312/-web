from __future__ import annotations

from app.core.fengshui import bazhai

# Luo Shu fly order (Shun): center -> Qian -> Dui -> Gen -> Li -> Kan -> Kun -> Zhen -> Xun
FLY_PALACES = ["中", "乾", "兑", "艮", "离", "坎", "坤", "震", "巽"]

STAR_YIN_YANG: dict[int, str] = {
    1: "阳",
    2: "阴",
    3: "阳",
    4: "阴",
    5: "阳",
    6: "阳",
    7: "阴",
    8: "阴",
    9: "阳",
}

STAR_NAMES: dict[int, str] = {
    1: "一白贪狼",
    2: "二黑巨门",
    3: "三碧禄存",
    4: "四绿文曲",
    5: "五黄廉贞",
    6: "六白武曲",
    7: "七赤破军",
    8: "八白左辅",
    9: "九紫右弼",
}

PERIOD_RANGES: list[tuple[int, int, int, str]] = [
    (1864, 1883, 1, "上元"),
    (1884, 1903, 2, "上元"),
    (1904, 1923, 3, "上元"),
    (1924, 1943, 4, "中元"),
    (1944, 1963, 5, "中元"),
    (1964, 1983, 6, "中元"),
    (1984, 2003, 7, "下元"),
    (2004, 2023, 8, "下元"),
    (2024, 2043, 9, "下元"),
]

# Shen Shi Yuan Long grouping by period yuan.
YUAN_DRAGONS: dict[str, dict[str, tuple[str, ...]]] = {
    "上元": {
        "天": ("丑", "辰", "未", "戌"),
        "地": ("子", "午", "卯", "酉"),
        "人": ("寅", "申", "巳", "亥"),
    },
    "中元": {
        "天": ("子", "午", "卯", "酉"),
        "地": ("丑", "辰", "未", "戌"),
        "人": ("寅", "申", "巳", "亥"),
    },
    "下元": {
        "天": ("寅", "申", "巳", "亥"),
        "地": ("丑", "辰", "未", "戌"),
        "人": ("子", "午", "卯", "酉"),
    },
}

DRAGON_YIN_YANG = {"天": "阳", "地": "阴", "人": "阳"}

# Trigram group to Luo Shu center number for sitting/facing.
TRIGRAM_STAR_NUM = {
    "坎": 1,
    "坤": 2,
    "震": 3,
    "巽": 4,
    "乾": 6,
    "兑": 7,
    "艮": 8,
    "离": 9,
}


def calc_period(build_year: int) -> dict[str, object]:
    if build_year < 1864 or build_year > 2043:
        raise ValueError("buildYear must be between 1864 and 2043 for period lookup")
    for start, end, number, yuan in PERIOD_RANGES:
        if start <= build_year <= end:
            return {
                "number": number,
                "label": f"{number}运",
                "yuan": yuan,
                "rangeStart": start,
                "rangeEnd": end,
            }
    raise ValueError(f"no period found for year {build_year}")


def mountain_star_number(mountain_id: str) -> int:
    mountain = bazhai.resolve_mountain(mountain_id)
    return TRIGRAM_STAR_NUM[mountain["trigram"]]


def dragon_for_mountain(mountain_name: str, yuan: str) -> str:
    groups = YUAN_DRAGONS[yuan]
    for dragon, names in groups.items():
        if mountain_name in names:
            return dragon
    raise ValueError(f"mountain {mountain_name} not in yuan {yuan}")


def is_forward(center_star: int, dragon: str) -> bool:
    star_yy = STAR_YIN_YANG[center_star]
    dragon_yy = DRAGON_YIN_YANG[dragon]
    return star_yy == dragon_yy


def fly_plate(center_star: int, forward: bool) -> dict[str, int]:
    plate: dict[str, int] = {}
    star = center_star
    for palace in FLY_PALACES:
        plate[palace] = star
        if forward:
            star = star - 1 if star > 1 else 9
        else:
            star = star + 1 if star < 9 else 1
    return plate


def plate_to_cells(plate: dict[str, int], *, kind: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for palace in FLY_PALACES:
        star = plate[palace]
        rows.append(
            {
                "palace": palace,
                "star": star,
                "starName": STAR_NAMES[star],
                "kind": kind,
            }
        )
    return rows


def build_combined_cells(
    yun: dict[str, int],
    shan: dict[str, int],
    xiang: dict[str, int],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for palace in FLY_PALACES:
        ys, ss, xs = yun[palace], shan[palace], xiang[palace]
        rows.append(
            {
                "palace": palace,
                "yunStar": ys,
                "shanStar": ss,
                "xiangStar": xs,
                "label": f"{ys}-{ss}-{xs}",
                "yunName": STAR_NAMES[ys],
                "shanName": STAR_NAMES[ss],
                "xiangName": STAR_NAMES[xs],
            }
        )
    return rows


def build_xuankong_chart(
    *,
    sitting_mountain: str,
    build_year: int,
    flow_year: int | None = None,
) -> dict[str, object]:
    mountain = bazhai.resolve_mountain(sitting_mountain)
    facing_name = mountain["facing"]
    period = calc_period(build_year)
    yuan = str(period["yuan"])
    period_num = int(period["number"])

    sitting_num = mountain_star_number(sitting_mountain)
    facing_num = mountain_star_number(facing_name)

    sitting_dragon = dragon_for_mountain(mountain["name"], yuan)
    facing_dragon = dragon_for_mountain(facing_name, yuan)

    shan_forward = is_forward(sitting_num, sitting_dragon)
    xiang_forward = is_forward(facing_num, facing_dragon)

    yun_plate = fly_plate(period_num, True)
    shan_plate = fly_plate(sitting_num, shan_forward)
    xiang_plate = fly_plate(facing_num, xiang_forward)

    result: dict[str, object] = {
        "period": period,
        "sitting": mountain["name"],
        "facing": facing_name,
        "label": f"坐{mountain['name']}向{facing_name}",
        "sittingStarCenter": sitting_num,
        "facingStarCenter": facing_num,
        "shanFly": "顺飞" if shan_forward else "逆飞",
        "xiangFly": "顺飞" if xiang_forward else "逆飞",
        "yunPan": plate_to_cells(yun_plate, kind="yun"),
        "shanPan": plate_to_cells(shan_plate, kind="shan"),
        "xiangPan": plate_to_cells(xiang_plate, kind="xiang"),
        "combinedPan": build_combined_cells(yun_plate, shan_plate, xiang_plate),
    }

    if flow_year is not None:
        flow_period = calc_period(flow_year)
        flow_num = int(flow_period["number"])
        flow_plate = fly_plate(flow_num, True)
        result["flowYear"] = flow_year
        result["flowPan"] = plate_to_cells(flow_plate, kind="flow")
        result["flowCombinedPan"] = build_combined_cells(flow_plate, shan_plate, xiang_plate)

    return result
