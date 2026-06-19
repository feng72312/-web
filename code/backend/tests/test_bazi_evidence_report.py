from __future__ import annotations

import asyncio

from app.core.judgement.chain import BaziJudgementChain
from app.core.judgement.evidence import build_evidence_chain
from app.core.judgement.judges import ALL_JUDGES


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


def test_evidence_chain_from_verdicts() -> None:
    verdicts = [judge.judge(SAMPLE_CHART) for judge in ALL_JUDGES if judge.role != "case"]
    chain = build_evidence_chain(verdicts, [], [])
    assert chain
    assert chain[0].conclusion


def test_judgement_report_has_tiered_evidence_field() -> None:
    report = asyncio.run(BaziJudgementChain(use_rag=False).run(SAMPLE_CHART))
    payload = report.to_dict()
    assert "tieredEvidence" in payload
    assert "arbitration" in payload
