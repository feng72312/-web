from __future__ import annotations

from app.core.hepan.bazi_rules import build_bazi_cross_notes
from app.core.hepan.scene import resolve_discipline


def _sample_chart(
    *,
    day_gan: str,
    day_zhi: str,
    gender: int,
    day_master: str,
    day_master_wuxing: str,
    wuxing_count: dict[str, int] | None = None,
) -> dict:
    return {
        "input": {"gender": gender},
        "dayMaster": day_master,
        "dayMasterWuxing": day_master_wuxing,
        "wuxingCount": wuxing_count or {"木": 1, "火": 1, "土": 1, "金": 1, "水": 1},
        "pillars": {
            "year": {"gan": "\u7532", "zhi": "\u5b50", "shishenGan": "", "hideGan": [], "shishenZhi": []},
            "month": {"gan": "\u4e19", "zhi": "\u5bc5", "shishenGan": "", "hideGan": [], "shishenZhi": []},
            "day": {
                "gan": day_gan,
                "zhi": day_zhi,
                "ganzhi": f"{day_gan}{day_zhi}",
                "nayin": "\u6d77\u91d1",
                "shishenGan": "",
                "hideGan": [],
                "shishenZhi": [],
            },
            "hour": {"gan": "\u620a", "zhi": "\u8fb0", "shishenGan": "", "hideGan": [], "shishenZhi": []},
        },
    }


def test_resolve_discipline_partnership_auto() -> None:
    assert resolve_discipline("partnership", "auto") == "bazi"


def test_resolve_discipline_marriage_auto() -> None:
    assert resolve_discipline("marriage", "auto") == "ziwei"


def test_bazi_day_zhi_he() -> None:
    chart_a = _sample_chart(
        day_gan="\u7532",
        day_zhi="\u5b50",
        gender=1,
        day_master="\u7532",
        day_master_wuxing="\u6728",
    )
    chart_b = _sample_chart(
        day_gan="\u4e59",
        day_zhi="\u4e11",
        gender=0,
        day_master="\u4e59",
        day_master_wuxing="\u6728",
    )
    notes = build_bazi_cross_notes(chart_a, chart_b, "marriage")
    ids = {n["id"] for n in notes}
    assert "bazi_day_zhi_relation" in ids
    day_note = next(n for n in notes if n["id"] == "bazi_day_zhi_relation")
    assert day_note["level"] == "fit"


def test_bazi_day_zhi_chong() -> None:
    chart_a = _sample_chart(
        day_gan="\u7532",
        day_zhi="\u5b50",
        gender=1,
        day_master="\u7532",
        day_master_wuxing="\u6728",
    )
    chart_b = _sample_chart(
        day_gan="\u4e19",
        day_zhi="\u5348",
        gender=0,
        day_master="\u4e19",
        day_master_wuxing="\u706b",
    )
    notes = build_bazi_cross_notes(chart_a, chart_b, "marriage")
    day_note = next(n for n in notes if n["id"] == "bazi_day_zhi_relation")
    assert day_note["level"] == "caution"
