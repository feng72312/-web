from __future__ import annotations

import asyncio

from app.core.judgement.chain import BaziJudgementChain
from app.core.judgement.evidence import build_tiered_evidence_summary

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


def test_build_tiered_evidence_summary_groups() -> None:
    summary = build_tiered_evidence_summary(
        {
            "primaryEvidence": [{"excerpt": "主裁A", "ruleId": "geju:month:食神"}],
            "caseReference": [{"excerpt": "命例B"}],
        }
    )
    assert summary["total"] == 2
    assert len(summary["groups"]) == 2
    assert summary["caseOverreachRisk"] is False


def test_judgement_report_includes_tiered_summary() -> None:
    report = asyncio.run(BaziJudgementChain(use_rag=False).run(SAMPLE_CHART))
    payload = report.to_dict()
    summary = payload.get("tieredEvidenceSummary") or {}
    if summary.get("total", 0) > 0:
        assert summary["groups"]
