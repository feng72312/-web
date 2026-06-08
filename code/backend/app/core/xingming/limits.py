from __future__ import annotations

from lunar_python import Solar

from app.core.xingming.palaces import EARTHLY_BRANCHES, palace_index_for_longitude, palace_name


def _year_pillar_branch(target_year: int) -> str:
    solar = Solar.fromYmd(target_year, 6, 1)
    pillar = solar.getLunar().getEightChar().getYear()
    return pillar[1] if len(pillar) >= 2 else "\u5b50"


def build_limits(
    ascendant: float,
    target_year: int,
) -> dict:
    branch = _year_pillar_branch(target_year)
    try:
        branch_index = EARTHLY_BRANCHES.index(branch)
    except ValueError:
        branch_index = 0
    asc_index = int(ascendant // 30.0) % 12
    offset = (branch_index - asc_index) % 12
    palace_idx = offset
    return {
        "targetYear": target_year,
        "taiSui": {
            "branch": branch,
            "palace": palace_name(palace_idx),
            "palaceIndex": palace_idx,
        },
        "xian": {
            "note": "V1: xian yun full fill-en table in phase 2",
            "palace": None,
        },
    }


def is_day_chart(sun_longitude: float, ascendant: float) -> bool:
    """Sun above horizon approximation via ecliptic arc distance."""
    diff = abs((sun_longitude - ascendant + 180) % 360 - 180)
    return diff < 90
