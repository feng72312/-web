from __future__ import annotations

import asyncio

from app.core.liuyao.engine import LiuyaoEngine
from app.core.liuyao.judgement.chain import LiuyaoJudgementChain
from app.core.liuyao.models import LiuyaoInput


def _sample_chart() -> dict:
    engine = LiuyaoEngine()
    return engine.divine(
        LiuyaoInput(
            question="这次投资能不能赚钱",
            method="coin",
            coin_lines=[7, 8, 9, 6, 7, 8],
            year=2024,
            month=6,
            day=15,
            hour=10,
            minute=30,
        )
    ).to_dict()


def test_judgement_chain_runs_without_rag():
    chart = _sample_chart()
    report = asyncio.run(
        LiuyaoJudgementChain(use_rag=False).run(chart, question=chart["input"]["question"])
    )
    payload = report.to_dict()
    assert len(payload.get("steps") or []) >= 8
    assert len(payload.get("judges") or []) >= 8
    assert payload.get("topic", {}).get("topicId") == "wealth"
    assert payload.get("yongShen", {}).get("source") == "rule"
    arbitration = payload.get("arbitration") or {}
    assert "confidenceScore" in arbitration
    assert payload.get("enrichedChart", {}).get("lines")


def test_enriched_chart_has_kong_po_fields():
    chart = _sample_chart()
    report = asyncio.run(
        LiuyaoJudgementChain(use_rag=False).run(chart, question=chart["input"]["question"])
    )
    lines = report.enrichedChart.get("lines") or []
    assert lines
    assert "kongPoState" in lines[0]
    assert "lineStrength" in lines[0]


def test_evidence_chain_populated():
    chart = _sample_chart()
    report = asyncio.run(
        LiuyaoJudgementChain(use_rag=False).run(chart, question=chart["input"]["question"])
    )
    assert len(report.evidenceChain) >= 5
