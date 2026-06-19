from __future__ import annotations

from app.core.judgement.judges import SuiYunJudge
from app.core.knowledge.factory import get_knowledge_service
from app.core.knowledge.keys_liunian import resolve_event_liunian_categories, select_liunian_categories
from app.core.knowledge.luck_chart import enrich_chart_for_judgement

BASE_CHART = {
    "dayMaster": "甲",
    "dayMasterWuxing": "木",
    "pillars": {
        "year": {"gan": "甲", "zhi": "子"},
        "month": {"gan": "丙", "zhi": "寅"},
        "day": {"gan": "甲", "zhi": "午"},
        "hour": {"gan": "乙", "zhi": "亥"},
    },
    "dayun": [{"ganzhi": "丁卯", "startAge": 8, "endAge": 17, "startYear": 1990, "endYear": 1999}],
}


def test_resolve_event_liunian_for_marriage_theme() -> None:
    cats = resolve_event_liunian_categories("命主在哪一年结婚")
    assert "event_marriage" in cats


def test_resolve_event_liunian_for_career_wealth_split() -> None:
    career = resolve_event_liunian_categories("2008年事业是否有升职")
    wealth = resolve_event_liunian_categories("2008年财运如何")
    assert "event_career" in career
    assert "event_wealth" not in career
    assert "event_wealth" in wealth


def test_select_liunian_categories_includes_event_and_base() -> None:
    cats = select_liunian_categories("2010年是否发生官非牢狱")
    assert "core" in cats
    assert "event_guanfei" in cats


def test_suiyun_judge_attaches_event_liunian_by_question() -> None:
    service = get_knowledge_service()
    chart = enrich_chart_for_judgement(
        BASE_CHART,
        question="命主2010年是否发生手术住院",
        benchmark_meta={"targetYear": 2010, "questionTheme": "健康疾病"},
    )
    verdict = SuiYunJudge().judge(chart)
    assert verdict.role == "suiyun"
    if service.enabled:
        assert any(rule_id == "liunian:event_health" for rule_id in verdict.ruleIds)
        assert "健康疾病" in verdict.summary or "疾病" in verdict.summary
