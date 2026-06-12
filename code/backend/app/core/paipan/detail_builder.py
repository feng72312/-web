from __future__ import annotations

from typing import Any

from app.core.paipan.interactions import build_interaction_notes
from app.core.paipan.models import Pillar
from app.core.paipan.shensha import collect_pillar_shen_sha, make_shen_sha_context

PILLAR_KEYS = ("year", "month", "day", "hour")
PILLAR_LABELS = {
    "year": "\u5e74\u67f1",
    "month": "\u6708\u67f1",
    "day": "\u65e5\u67f1",
    "hour": "\u65f6\u67f1",
}


def _hide_stems_text(hide_gan: list[str], shishen_zhi: list[str]) -> list[str]:
    rows: list[str] = []
    for idx, gan in enumerate(hide_gan):
        label = shishen_zhi[idx] if idx < len(shishen_zhi) else ""
        rows.append(f"{gan}({label})" if label else gan)
    return rows


def pillars_to_dict(pillars: dict[str, Pillar]) -> dict[str, Any]:
    return {
        key: {
            "gan": p.gan,
            "zhi": p.zhi,
            "ganzhi": p.ganzhi,
            "ganWuxing": p.gan_wuxing,
            "zhiWuxing": p.zhi_wuxing,
            "nayin": p.nayin,
            "hideGan": p.hide_gan,
            "shishenGan": p.shishen_gan,
            "shishenZhi": p.shishen_zhi,
        }
        for key, p in pillars.items()
    }


def build_pillar_detail(ec, pillars: dict[str, Pillar], gender: int) -> dict[str, Any]:
    day_gan = pillars["day"].gan
    role = "\u5143\u7537" if gender == 1 else "\u5143\u5973"
    shen_sha_ctx = make_shen_sha_context(
        day_gan=pillars["day"].gan,
        day_zhi=pillars["day"].zhi,
        year_gan=pillars["year"].gan,
        year_zhi=pillars["year"].zhi,
        month_zhi=pillars["month"].zhi,
        gender=gender,
    )

    xunkong_map = {
        "year": ec.getYearXunKong(),
        "month": ec.getMonthXunKong(),
        "day": ec.getDayXunKong(),
        "hour": ec.getTimeXunKong(),
    }

    columns = []
    for key in PILLAR_KEYS:
        p = pillars[key]
        shishen = p.shishen_gan if key != "day" else role
        columns.append(
            {
                "key": key,
                "label": PILLAR_LABELS[key],
                "shishen": shishen,
                "gan": p.gan,
                "zhi": p.zhi,
                "ganWuxing": p.gan_wuxing,
                "zhiWuxing": p.zhi_wuxing,
                "hideStems": _hide_stems_text(p.hide_gan, p.shishen_zhi),
                "nayin": p.nayin,
                "xunkong": xunkong_map[key],
                "shenSha": collect_pillar_shen_sha(shen_sha_ctx, p.gan, p.zhi),
            }
        )

    notes = build_interaction_notes(
        {key: {"gan": pillars[key].gan, "zhi": pillars[key].zhi} for key in PILLAR_KEYS}
    )

    return {
        "columns": columns,
        "stemNotes": notes["stemNotes"],
        "branchNotes": notes["branchNotes"],
        "boneWeight": "\u6682\u672a\u63a5\u5165",
        "boneComment": "\u79f0\u9aa8\u529f\u80fd\u540e\u7eed\u7248\u672c\u5f00\u653e",
    }
