from __future__ import annotations

from app.core.knowledge.family_option_scorer import (
    build_family_option_score_block,
    score_death_father_year,
    score_death_mother_year,
    score_wealth_tier_option,
)


def _minimal_chart() -> dict:
    return {
        "pillars": {
            "year": {"shishenGan": "偏财", "gan": "甲", "zhi": "子"},
            "month": {"shishenGan": "正印", "gan": "丙", "zhi": "寅"},
            "day": {"shishenGan": "日主", "gan": "戊", "zhi": "午"},
            "hour": {"shishenGan": "比肩", "gan": "戊", "zhi": "申"},
        },
        "birth": {"year": 1980},
    }


def test_wealth_tier_scores_vary_by_option() -> None:
    chart = _minimal_chart()
    poor = score_wealth_tier_option(chart, "贫穷家庭出身")
    rich = score_wealth_tier_option(chart, "富贵家庭出身")
    assert rich > poor


def test_build_block_for_wealth_tier() -> None:
    chart = _minimal_chart()
    q = "此命出身贫或富?"
    opts = [
        "A. 贫穷家庭出身",
        "B. 小康之家出身",
        "C. 富贵家庭出身",
        "D. 虽有父母, 童年却被养在孤儿院",
    ]
    block = build_family_option_score_block(chart, q, opts)
    assert "【家庭出身选项规则分】" in block
    assert "A " in block
    assert "规则分" in block


def test_death_year_scores_in_range() -> None:
    chart = _minimal_chart()
    chart["dayun"] = []
    chart["liunian"] = {}
    s_f = score_death_father_year(chart, 2000)
    s_m = score_death_mother_year(chart, 2000)
    assert 0.0 <= s_f <= 1.0
    assert 0.0 <= s_m <= 1.0


def test_build_block_for_death_mother() -> None:
    chart = _minimal_chart()
    q = "命主母亲于哪年离世?"
    opts = ["A. 1989年", "B. 1990年", "C. 2011年", "D. 2021年"]
    block = build_family_option_score_block(chart, q, opts)
    assert "丧母题" in block
    assert "2011" in block or "1989" in block

