from __future__ import annotations

import asyncio

from app.benchmark.contest8_benchmark_meta import check_judgement_coverage, enrich_question
from app.core.judgement.chain import BaziJudgementChain
from app.core.judgement.judges import SuiYunJudge
from app.core.knowledge.factory import get_knowledge_service
from app.core.knowledge.keys_liunian import resolve_sanming_liunian_categories, select_liunian_categories
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
    "dayun": [{"ganzhi": "甲子", "startAge": 8, "endAge": 17, "startYear": 1990, "endYear": 1999}],
    "luckTimeline": {
        "dayun": [
            {
                "index": 1,
                "ganzhi": "甲子",
                "startAge": 8,
                "endAge": 17,
                "startYear": 1990,
                "endYear": 1999,
                "liunian": [{"year": 1996, "ganzhi": "丙子"}],
            }
        ]
    },
}


class _FakeQuestion:
    question_id = "q-test"
    question = "1996年是否发生岁运并临或真太岁"
    year = 1996
    answer = "A"


def test_resolve_sanming_liunian_categories() -> None:
    cats = resolve_sanming_liunian_categories("1996年是否发生岁运并临或真太岁")
    assert "sanming_suiyun_binglin" in cats
    assert "sanming_zhen_taisui" in cats


def test_resolve_sanming_zhan_chong_he() -> None:
    cats = resolve_sanming_liunian_categories("流年冲克太岁是否凶")
    assert "sanming_zhan_chong_he" in cats


def test_select_liunian_categories_includes_sanming_nodes() -> None:
    cats = select_liunian_categories("命主小运与伏吟如何")
    assert "sanming_xiaoyun" in cats
    assert "sanming_fuyin" in cats


def test_suiyun_judge_attaches_sanming_liunian_rules() -> None:
    service = get_knowledge_service()
    chart = enrich_chart_for_judgement(
        BASE_CHART,
        question="1996年是否发生岁运并临或真太岁",
        benchmark_meta={"targetYear": 1996},
    )
    verdict = SuiYunJudge().judge(chart)
    if service.enabled:
        assert any(rule_id.startswith("liunian:sanming_") for rule_id in verdict.ruleIds)


def test_check_judgement_coverage_event_liunian() -> None:
    service = get_knowledge_service()
    item = _FakeQuestion()
    meta = enrich_question(item)  # type: ignore[arg-type]
    chart = enrich_chart_for_judgement(BASE_CHART, question=item.question, benchmark_meta=meta)
    report = asyncio.run(
        BaziJudgementChain(use_rag=False).run(chart, question=item.question, benchmark_meta=meta)
    )
    payload = report.to_dict()
    coverage = check_judgement_coverage(payload, meta)
    assert "eventLiunianCovered" in coverage
    if service.enabled and meta.get("expectedEventLiunian"):
        assert coverage["eventLiunianCovered"] is True
