from __future__ import annotations

from app.core.knowledge.marriage_option_scorer import (
    build_marriage_option_score_block,
    compute_marriage_score_margin,
    score_marriage_year,
)


def _sample_chart() -> dict:
    return {
        "gender": "male",
        "birthYear": 1980,
        "pillars": {
            "day": {"zhi": "辰", "shishenGan": "比肩"},
            "hour": {"zhi": "午"},
        },
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
                }
            ],
            "liunian": [
                {
                    "year": 2017,
                    "ganzhi": "丁酉",
                    "pillar": {
                        "shishenGan": "正官",
                        "zhi": "酉",
                        "gan": "丁",
                        "hideStems": [],
                    },
                },
                {
                    "year": 2018,
                    "ganzhi": "戊戌",
                    "pillar": {
                        "shishenGan": "偏印",
                        "zhi": "戌",
                        "gan": "戊",
                        "hideStems": [],
                    },
                },
            ],
        },
    }


def test_build_marriage_score_block_year_options() -> None:
    chart = _sample_chart()
    q = "命主哪一年再婚?"
    opts = ["A 2017", "B 2018", "C 2019", "D 2020"]
    block = build_marriage_option_score_block(chart, q, opts)
    assert "【婚姻选项规则分】" in block
    assert "2017" in block
    assert "2018" in block


def test_female_uses_guan_scoring() -> None:
    chart = _sample_chart()
    chart["gender"] = "female"
    q = "命主哪一年结婚?"
    male_sc = score_marriage_year(chart, q, 2017, is_female=False)
    female_sc = score_marriage_year(chart, q, 2017, is_female=True)
    assert isinstance(male_sc, float)
    assert isinstance(female_sc, float)


def test_compute_margin_returns_tuple() -> None:
    chart = _sample_chart()
    q = "命主哪一年再婚?"
    opts = ["A 2017", "B 2018", "C 2019", "D 2020"]
    top, margin = compute_marriage_score_margin(chart, q, opts)
    assert top >= 0.0
    assert margin >= 0.0


def test_narrative_block_skipped_for_status() -> None:
    chart = _sample_chart()
    q = "截至2017年, 命主婚姻状况?"
    opts = [
        "A. 至今美满",
        "B. 2010年结婚后离婚",
        "C. 从未结婚",
        "D. 恋爱中",
    ]
    block = build_marriage_option_score_block(chart, q, opts)
    assert block == ""
