from __future__ import annotations

from app.core.judgement.judges import MonthStrengthJudge
from app.core.knowledge.month_strength import assess_month_strength, season_slot

SAMPLE_CHART = {
    "dayMaster": "甲",
    "dayMasterWuxing": "木",
    "wuxingCount": {"木": 2, "火": 1, "土": 2, "金": 1, "水": 2},
    "pillars": {
        "year": {"gan": "甲", "zhi": "子", "shishenGan": "比肩"},
        "month": {"gan": "丙", "zhi": "寅", "shishenGan": "食神"},
        "day": {"gan": "甲", "zhi": "午", "shishenGan": ""},
        "hour": {"gan": "乙", "zhi": "亥", "shishenGan": "劫财"},
    },
}


def test_season_slot_spring_wood_is_wang() -> None:
    assert season_slot("寅", "木") == "旺"


def test_assess_month_strength_returns_rule_ids() -> None:
    assessed = assess_month_strength(SAMPLE_CHART)
    assert assessed["ruleIds"] == ["month:strength:旺"]
    assert "身强" in assessed["body"] or "得令" in assessed["body"]


def test_month_strength_judge_role() -> None:
    verdict = MonthStrengthJudge().judge(SAMPLE_CHART)
    assert verdict.role == "month"
    assert verdict.ruleIds
    assert verdict.summary
