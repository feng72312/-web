from __future__ import annotations

from app.core.knowledge.target_year_block import build_virtual_age_dayun_anchor


def test_virtual_age_fallback_when_named_dayun_mismatch() -> None:
    chart = {
        "luckTimeline": {
            "dayun": [
                {
                    "index": 4,
                    "ganzhi": "辛未",
                    "startAge": 35,
                    "endAge": 44,
                    "startYear": 1990,
                    "endYear": 1999,
                    "pillar": {"shishenGan": "偏印"},
                },
                {
                    "index": 7,
                    "ganzhi": "甲戌",
                    "startAge": 67,
                    "endAge": 76,
                    "startYear": 2021,
                    "endYear": 2030,
                    "pillar": {"shishenGan": "七杀"},
                },
            ]
        }
    }
    q = "虚龄35至44甲戌大运期间，其子女运？"
    block = build_virtual_age_dayun_anchor(chart, q)
    assert "辛未" in block
    assert "不一致" in block or "虚龄35-44" in block
