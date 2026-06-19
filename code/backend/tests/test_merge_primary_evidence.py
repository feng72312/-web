from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

from app.core.judgement.chain import BaziJudgementChain
from app.core.judgement.evidence import merge_primary_evidence
from app.core.judgement.models import TieredEvidence

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


def test_merge_primary_evidence_prefers_graph_and_dedupes() -> None:
    graph_rows = [
        {
            "ruleId": "geju:month:正官",
            "excerpt": "graph",
            "evidenceBucket": "primaryEvidence",
            "libraryRole": "rule_graph",
        }
    ]
    rag_rows = [
        {
            "ruleId": "geju:month:正官",
            "excerpt": "rag duplicate",
            "evidenceBucket": "primaryEvidence",
        },
        {
            "excerpt": "rag unique",
            "evidenceBucket": "primaryEvidence",
            "evidenceRole": "tiaohou_judge",
        },
    ]
    merged = merge_primary_evidence(graph_rows, rag_rows)
    assert len(merged) == 2
    assert merged[0]["libraryRole"] == "rule_graph"
    assert merged[1]["excerpt"] == "rag unique"


def test_rag_mode_keeps_graph_primary_when_rag_only_low_trust() -> None:
    async def _fake_fetch(self, requests, *, top_k=3):
        tiered = TieredEvidence()
        tiered.excludedOrLowTrust = [
            {"excerpt": "low trust only", "evidenceRole": "low_trust"},
        ]
        return tiered

    with patch(
        "app.core.judgement.evidence.ClassicFirstRetriever.fetch_for_requests",
        new=_fake_fetch,
    ):
        report = asyncio.run(BaziJudgementChain(use_rag=True).run(SAMPLE_CHART))

    primary = report.tieredEvidence.primaryEvidence if report.tieredEvidence else []
    assert primary
    assert primary[0].get("libraryRole") == "rule_graph"
    summary = report.tieredEvidenceSummary or {}
    assert summary.get("caseOverreachRisk") is False
    primary_group = next(
        (g for g in summary.get("groups") or [] if g.get("bucket") == "primaryEvidence"),
        None,
    )
    assert primary_group and primary_group["count"] > 0
