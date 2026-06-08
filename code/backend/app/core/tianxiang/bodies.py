from __future__ import annotations

from datetime import datetime

from app.core.tianxiang import ephemeris, si_yu
from app.core.tianxiang.mansions import longitude_to_mansion
from app.core.tianxiang.models import BodyPosition

def _swe_body_map() -> dict[str, int]:
    swe = ephemeris._load_swe()
    return {
        "sun": swe.SUN,
        "moon": swe.MOON,
        "mercury": swe.MERCURY,
        "venus": swe.VENUS,
        "mars": swe.MARS,
        "jupiter": swe.JUPITER,
        "saturn": swe.SATURN,
    }


def compute_all_bodies(
    julian_day: float,
    dt: datetime,
    *,
    mansion_table: str = "guolao_v1",
    si_yu_model: str = si_yu.SI_YU_MODEL,
    body_ids: list[str] | None = None,
) -> list[BodyPosition]:
    swe_map = _swe_body_map()
    wanted = body_ids or list(swe_map.keys()) + ["rahu", "ketu", "yuebei", "ziqi"]
    positions: list[BodyPosition] = []

    for bid in wanted:
        if bid in swe_map:
            lon, retro = ephemeris.sidereal_longitude(julian_day, swe_map[bid])
            label = ephemeris.BODY_LABELS.get(bid, bid)
        elif bid == "ketu":
            lon, _ = ephemeris.sidereal_longitude(julian_day, ephemeris._load_swe().MEAN_APOG)  # type: ignore[attr-defined]
            label = "\u8ba1\u90fd"
            retro = None
        elif bid == "rahu":
            ketu_lon, _ = ephemeris.sidereal_longitude(
                julian_day, ephemeris._load_swe().MEAN_APOG  # type: ignore[attr-defined]
            )
            lon = si_yu.rahu_from_ketu(ketu_lon)
            label = "\u7f57\u55e3"
            retro = None
        elif bid == "yuebei":
            lon = si_yu.yue_bei_longitude(dt, model=si_yu_model)
            label = "\u6708\u5b5a"
            retro = None
        elif bid == "ziqi":
            lon = si_yu.purple_qi_longitude(dt, model=si_yu_model)
            label = "\u7d2b\u6c14"
            retro = None
        else:
            continue
        mansion = longitude_to_mansion(lon, mansion_table=mansion_table)
        positions.append(
            BodyPosition(
                id=bid,
                label=label,
                ecliptic_longitude=round(lon, 4),
                mansion=mansion.mansion,
                mansion_degree=mansion.degree_in_mansion,
                retrograde=retro,
            )
        )
    return positions
