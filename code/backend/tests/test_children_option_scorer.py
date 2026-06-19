from __future__ import annotations

from app.core.knowledge.children_option_scorer import (
    build_children_option_score_block,
    score_children_birth_year,
)
from app.benchmark.contest8_rag import infer_question_theme


def _sample_chart() -> dict:
    return {
        "gender": "male",
        "pillars": {
            "day": {"zhi": "子"},
            "hour": {"zhi": "午"},
        },
        "luckTimeline": {
            "dayun": [
                {
                    "index": 1,
                    "ganzhi": "甲子",
                    "startAge": 1,
                    "endAge": 10,
                    "startYear": 1980,
                    "endYear": 1989,
                    "pillar": {"shishenGan": "比肩"},
                }
            ],
            "liunian": [
                {
                    "year": 2019,
                    "ganzhi": "己亥",
                    "pillar": {"shishenGan": "正印", "zhi": "亥", "gan": "己"},
                },
                {
                    "year": 2021,
                    "ganzhi": "辛丑",
                    "pillar": {"shishenGan": "正官", "zhi": "丑", "gan": "辛"},
                },
            ],
        },
    }


def test_wealth_child_context_is_career() -> None:
    q = "请问以下哪年命主忽然赚到大钱，受不了孩子抱怨，决定买房解决孩子读书的通勤问题?"
    assert infer_question_theme(q) == "职业财运"


def test_build_children_score_block_year_options() -> None:
    chart = _sample_chart()
    q = "命主目前有一个孩子，那年出生？"
    opts = ["A 2018", "B 2019", "C 2020", "D 2021"]
    block = build_children_option_score_block(chart, q, opts)
    assert "【子女选项规则分】" in block
    assert "2019" in block
    assert "2021" in block


def test_female_uses_shishang_scoring() -> None:
    chart = _sample_chart()
    chart["gender"] = "female"
    chart["birthYear"] = 1978
    male_sc = score_children_birth_year(chart, 2019, is_female=False)
    female_sc = score_children_birth_year(chart, 2019, is_female=True)
    assert isinstance(male_sc, float)
    assert isinstance(female_sc, float)


def test_recent_year_bonus_only_for_latest_option() -> None:
    chart = _sample_chart()
    chart["gender"] = "male"
    chart["birthYear"] = 1983
    q = "命主目前有一个孩子，那年出生？"
    opts = ["A 2018", "B 2019", "C 2020", "D 2021"]
    block = build_children_option_score_block(chart, q, opts)
    assert "2021" in block
    lines = {ln.split()[0]: ln for ln in block.splitlines() if ln[:1] in "ABCD"}
    score_2021 = float(lines["D"].split("规则分")[1])
    score_2018 = float(lines["A"].split("规则分")[1])
    assert score_2021 >= score_2018
