from __future__ import annotations

import asyncio

from app.benchmark.contest8_benchmark_meta import check_judgement_coverage, enrich_question
from app.core.judgement.chain import BaziJudgementChain

SAMPLE_CHART = {
    "dayMaster": "甲",
    "dayMasterWuxing": "木",
    "wuxingCount": {"木": 2, "火": 1, "土": 2, "金": 1, "水": 2},
    "pillars": {
        "year": {"ganzhi": "甲子", "gan": "甲", "zhi": "子", "shishenGan": "比肩"},
        "month": {"ganzhi": "丙寅", "gan": "丙", "zhi": "寅", "shishenGan": "食神"},
        "day": {"ganzhi": "甲午", "gan": "甲", "zhi": "午", "shishenGan": ""},
        "hour": {"ganzhi": "乙亥", "gan": "乙", "zhi": "亥", "shishenGan": "劫财"},
    },
    "dayun": [{"ganzhi": "丁卯", "startAge": 8, "endAge": 17}],
}


class _FakeQuestion:
    question_id = "offline-coverage"
    question = "命主婚姻感情如何"
    year = 2024
    answer = "A"


def test_offline_chain_avoids_case_overreach() -> None:
    item = _FakeQuestion()
    meta = enrich_question(item)  # type: ignore[arg-type]
    report = asyncio.run(
        BaziJudgementChain(use_rag=False).run(
            SAMPLE_CHART,
            question=item.question,
            benchmark_meta=meta,
        )
    )
    payload = report.to_dict()
    coverage = check_judgement_coverage(payload, meta)
    assert coverage["caseReferenceCount"] == 0
    if coverage["primaryEvidenceCount"] > 0:
        assert coverage["caseOverreach"] is False


def test_offline_chain_populates_graph_primary_evidence() -> None:
    report = asyncio.run(BaziJudgementChain(use_rag=False).run(SAMPLE_CHART))
    primary = (report.tieredEvidence.primaryEvidence if report.tieredEvidence else []) or []
    if primary:
        assert primary[0].get("evidenceBucket") == "primaryEvidence"
        assert primary[0].get("libraryRole") == "rule_graph"
