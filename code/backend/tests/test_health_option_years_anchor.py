from __future__ import annotations

from app.core.knowledge.target_year_block import build_health_option_years_anchor


def test_health_option_years_anchor() -> None:
    chart = {
        "gender": "male",
        "birthYear": 1971,
        "birthMonth": 4,
        "birthDay": 12,
        "birthHour": 8,
        "pillars": {
            "year": {"gan": "辛", "zhi": "亥"},
            "month": {"gan": "壬", "zhi": "辰"},
            "day": {"gan": "甲", "zhi": "子"},
            "hour": {"gan": "戊", "zhi": "辰"},
        },
        "luckTimeline": {
            "dayun": [
                {
                    "index": 1,
                    "ganzhi": "辛卯",
                    "startAge": 8,
                    "endAge": 17,
                    "startYear": 1979,
                    "endYear": 1988,
                    "pillar": {"shishenGan": "正官"},
                    "liunian": [
                        {
                            "year": 2010,
                            "age": 39,
                            "ganzhi": "庚寅",
                            "pillar": {"shishenGan": "七杀", "gan": "庚", "zhi": "寅"},
                        }
                    ],
                }
            ],
            "liunian": [],
        },
    }
    opts = ["A. 1998年", "B. 2010年", "C. 2018年", "D. 2022年"]
    block = build_health_option_years_anchor(chart, "哪年骨折?", opts)
    assert "【健康选项年份锚点】" in block
    assert "2010年" in block
    assert "病灾看七杀" in block
