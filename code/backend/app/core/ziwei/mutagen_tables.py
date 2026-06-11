from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from iztro_py.data.types import HeavenlyStemName, Mutagen, StarName

MUTAGEN_TYPES: tuple[str, ...] = ("禄", "权", "科", "忌")

STEM_KEYS: tuple[str, ...] = (
    "jiaHeavenly",
    "yiHeavenly",
    "bingHeavenly",
    "dingHeavenly",
    "wuHeavenly",
    "jiHeavenly",
    "gengHeavenly",
    "xinHeavenly",
    "renHeavenly",
    "guiHeavenly",
)

# Per-table overrides for disputed stems. Unlisted stems use iztro default config.
TABLE_OVERRIDES: dict[str, dict[str, list[str]]] = {
    "nan_pai": {
        # 南派三合: 庚阳武同阴
        "gengHeavenly": ["taiyangMaj", "wuquMaj", "tiantongMaj", "taiyinMaj"],
    },
    "geng_beipai": {
        # 北派庚干: 庚阳武同相
        "gengHeavenly": ["taiyangMaj", "wuquMaj", "tiantongMaj", "tianxiangMaj"],
    },
    "wu_pai": {
        # 王亭之戊干: 戊贪阴阳机
        "wuHeavenly": ["tanlangMaj", "taiyinMaj", "taiyangMaj", "tianjiMaj"],
    },
    "ren_pai": {
        # 壬干: 壬梁紫府武
        "renHeavenly": ["tianliangMaj", "ziweiMaj", "tianfuMaj", "wuquMaj"],
    },
}


def get_mutagen_stars(table_id: str, stem_key: str) -> list[str]:
    from iztro_py.data.heavenly_stems import HEAVENLY_STEMS_CONFIG

    overrides = TABLE_OVERRIDES.get(table_id, {}).get(stem_key)
    if overrides:
        return list(overrides)
    return list(HEAVENLY_STEMS_CONFIG[stem_key].mutagen)  # type: ignore[index]


def get_mutagen_type_for_star(table_id: str, stem_key: str, star_name: str) -> str | None:
    stars = get_mutagen_stars(table_id, stem_key)
    for index, name in enumerate(stars):
        if name == star_name and index < len(MUTAGEN_TYPES):
            return MUTAGEN_TYPES[index]
    return None


def apply_mutagen_table_to_chart(chart: object, table_id: str) -> None:
    raw_date = getattr(chart, "raw_chinese_date", None)
    if raw_date is None:
        return
    year_stem = raw_date.year_stem
    for palace in chart.palaces:
        for stars in (palace.major_stars, palace.minor_stars):
            for star in stars:
                star.mutagen = None
    star_types = {
        star_name: MUTAGEN_TYPES[index]
        for index, star_name in enumerate(get_mutagen_stars(table_id, year_stem))
        if index < len(MUTAGEN_TYPES)
    }
    for palace in chart.palaces:
        for stars in (palace.major_stars, palace.minor_stars):
            for star in stars:
                mutagen = star_types.get(star.name)
                if mutagen:
                    star.mutagen = mutagen
