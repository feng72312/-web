from __future__ import annotations

import calendar
from datetime import datetime
from typing import Any

from lunar_python import Solar
from lunar_python.util import LunarUtil

from app.core.paipan.shensha import pillar_shen_sha
from app.core.paipan.wuxing_map import gan_wuxing, zhi_wuxing

PILLAR_KEYS = ("year", "month", "day", "hour")


def split_ganzhi(ganzhi: str) -> tuple[str, str]:
    return ganzhi[0], ganzhi[1]


def stem_shishen(day_gan: str, gan: str) -> str:
    return LunarUtil.SHI_SHEN.get(day_gan + gan, "")


def branch_hide_stems(day_gan: str, zhi: str) -> list[str]:
    hide_gan = LunarUtil.ZHI_HIDE_GAN.get(zhi, [])
    rows: list[str] = []
    for gan in hide_gan:
        label = stem_shishen(day_gan, gan)
        rows.append(f"{gan}({label})" if label else gan)
    return rows


def flow_pillar(day_gan: str, ganzhi: str, year_zhi: str = "") -> dict[str, Any]:
    if not ganzhi or len(ganzhi) < 2:
        return {}
    gan, zhi = split_ganzhi(ganzhi)
    return {
        "gan": gan,
        "zhi": zhi,
        "ganzhi": ganzhi,
        "shishenGan": stem_shishen(day_gan, gan),
        "hideStems": branch_hide_stems(day_gan, zhi),
        "xunkong": LunarUtil.getXunKong(ganzhi),
        "ganWuxing": gan_wuxing(gan),
        "zhiWuxing": zhi_wuxing(zhi),
        "shenSha": pillar_shen_sha(day_gan, year_zhi, gan, zhi) if year_zhi else [],
    }


def birth_flow_pillars(day_gan: str, year_zhi: str, pillars: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key in PILLAR_KEYS:
        p = pillars[key]
        result[key] = {
            "gan": p["gan"],
            "zhi": p["zhi"],
            "ganzhi": p["ganzhi"],
            "shishenGan": p.get("shishenGan", ""),
            "hideStems": [
                f"{g}({s})" if s else g
                for g, s in zip(p.get("hideGan", []), p.get("shishenZhi", []))
            ],
            "xunkong": p.get("xunkong", ""),
            "ganWuxing": p.get("ganWuxing", ""),
            "zhiWuxing": p.get("zhiWuxing", ""),
            "shenSha": pillar_shen_sha(day_gan, year_zhi, p["gan"], p["zhi"]),
        }
    return result


def build_liuri_by_year(year: int, day_gan: str) -> dict[str, list[dict[str, Any]]]:
    by_month: dict[str, list[dict[str, Any]]] = {}
    for month in range(1, 13):
        days = calendar.monthrange(year, month)[1]
        key = f"{year}-{month:02d}"
        items: list[dict[str, Any]] = []
        for day in range(1, days + 1):
            solar = Solar.fromYmd(year, month, day)
            lunar = solar.getLunar()
            ganzhi = lunar.getDayInGanZhi()
            gan, zhi = split_ganzhi(ganzhi)
            items.append(
                {
                    "date": solar.toYmd(),
                    "day": day,
                    "ganzhi": ganzhi,
                    "gan": gan,
                    "zhi": zhi,
                    "shishenGan": stem_shishen(day_gan, gan),
                    "hideStems": branch_hide_stems(day_gan, zhi),
                    "xunkong": LunarUtil.getXunKong(ganzhi),
                    "ganWuxing": gan_wuxing(gan),
                    "zhiWuxing": zhi_wuxing(zhi),
                }
            )
        by_month[key] = items
    return by_month


def build_luck_timeline(
    ec,
    gender: int,
    birth_year: int,
    pillars_dict: dict[str, Any],
) -> dict[str, Any]:
    now = datetime.now()
    today = now.date()
    day_gan = pillars_dict["day"]["gan"]
    year_zhi = pillars_dict["year"]["zhi"]
    gender_role = "\u5143\u7537" if gender == 1 else "\u5143\u5973"

    yun = ec.getYun(gender)
    dayun_rows: list[dict[str, Any]] = []
    current_dayun_index = 0
    current_liunian_year = today.year
    current_liuyue_index = 0
    current_liuri_date = today.isoformat()

    age_now = today.year - birth_year + 1

    for dy in yun.getDaYun():
        ganzhi = dy.getGanZhi()
        if not ganzhi:
            continue
        idx = dy.getIndex()
        if dy.getStartAge() <= age_now + 1 <= dy.getEndAge():
            current_dayun_index = idx

        liunian_rows: list[dict[str, Any]] = []
        for ln in dy.getLiuNian():
            liuyue_rows = []
            for ly in ln.getLiuYue():
                ly_gz = ly.getGanZhi()
                liuyue_rows.append(
                    {
                        "index": ly.getIndex(),
                        "ganzhi": ly_gz,
                        "monthLabel": ly.getMonthInChinese(),
                        "xunkong": ly.getXunKong(),
                        "pillar": flow_pillar(day_gan, ly_gz, year_zhi),
                    }
                )
            ln_year = ln.getYear()
            ln_gz = ln.getGanZhi()
            if ln_year == today.year:
                current_liunian_year = ln_year
                month_gz = Solar.fromYmd(today.year, today.month, today.day).getLunar().getMonthInGanZhi()
                for ly_row in liuyue_rows:
                    if ly_row["ganzhi"] == month_gz:
                        current_liuyue_index = ly_row["index"]
                        break
            liunian_rows.append(
                {
                    "year": ln_year,
                    "age": ln.getAge(),
                    "ganzhi": ln_gz,
                    "xunkong": ln.getXunKong(),
                    "pillar": flow_pillar(day_gan, ln_gz, year_zhi),
                    "liuyue": liuyue_rows,
                }
            )

        dayun_rows.append(
            {
                "index": idx,
                "ganzhi": ganzhi,
                "startAge": dy.getStartAge(),
                "endAge": dy.getEndAge(),
                "startYear": dy.getStartYear(),
                "endYear": dy.getEndYear(),
                "xunkong": dy.getXunKong(),
                "pillar": flow_pillar(day_gan, ganzhi, year_zhi),
                "liunian": liunian_rows,
            }
        )

    # Flow-day data is loaded on demand via /liuri/{year} when the user opens the view.
    liuri_cache: dict[str, dict[str, list[dict[str, Any]]]] = {}

    birth_pillars = birth_flow_pillars(day_gan, year_zhi, pillars_dict)
    for key in PILLAR_KEYS:
        xunkong_fn = {
            "year": ec.getYearXunKong,
            "month": ec.getMonthXunKong,
            "day": ec.getDayXunKong,
            "hour": ec.getTimeXunKong,
        }[key]
        birth_pillars[key]["xunkong"] = xunkong_fn()

    jieqi = [
        "\u7acb\u6625",
        "\u96e8\u6c34",
        "\u60ca\u86d9",
        "\u6625\u5206",
        "\u6e05\u660e",
        "\u8c37\u96e8",
        "\u7acb\u590f",
        "\u5c0f\u6ee1",
        "\u8292\u79cd",
        "\u590f\u81f3",
        "\u5c0f\u6691",
        "\u5927\u6691",
        "\u7acb\u79cb",
        "\u5904\u6691",
        "\u767d\u9732",
        "\u79cb\u5206",
        "\u5bd2\u9732",
        "\u971c\u964d",
        "\u7acb\u51ac",
        "\u5c0f\u96ea",
        "\u5927\u96ea",
        "\u51ac\u81f3",
        "\u5c0f\u5bd2",
        "\u5927\u5bd2",
    ]

    return {
        "current": {
            "dayunIndex": current_dayun_index,
            "liunianYear": current_liunian_year,
            "liuyueIndex": current_liuyue_index,
            "liuriDate": current_liuri_date,
        },
        "birthYear": birth_year,
        "genderRole": gender_role,
        "dayMaster": day_gan,
        "dayunStart": {
            "year": yun.getStartYear(),
            "month": yun.getStartMonth(),
            "day": yun.getStartDay(),
            "hour": yun.getStartHour(),
        },
        "dayunForward": yun.isForward(),
        "birthPillars": birth_pillars,
        "dayun": dayun_rows,
        "liuriByYear": liuri_cache,
        "jieqi": jieqi,
    }
