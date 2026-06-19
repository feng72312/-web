from __future__ import annotations

from app.core.knowledge.target_year_block import build_marriage_option_years_anchor


def _sample_chart() -> dict:
    return {
        "gender": "male",
        "pillars": {"day": {"zhi": "辰"}},
        "luckTimeline": {
            "dayun": [
                {
                    "index": 4,
                    "ganzhi": "戊午",
                    "startAge": 35,
                    "endAge": 44,
                    "startYear": 2017,
                    "endYear": 2026,
                    "pillar": {"shishenGan": "偏印"},
                    "liunian": [
                        {
                            "year": 2018,
                            "ganzhi": "戊戌",
                            "pillar": {"shishenGan": "偏印", "zhi": "戌", "gan": "戊"},
                        }
                    ],
                }
            ],
            "liunian": [],
        },
    }


def test_marriage_option_years_anchor() -> None:
    chart = _sample_chart()
    opts = ["A 2017", "B 2018", "C 2019", "D 2020"]
    block = build_marriage_option_years_anchor(chart, "哪年再婚?", opts)
    assert "【婚姻选项年份锚点】" in block
    assert "2018" in block
    assert "配偶星" in block
