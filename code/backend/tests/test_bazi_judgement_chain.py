from __future__ import annotations

import asyncio

from app.core.judgement.chain import BaziJudgementChain
from app.core.judgement.judges import GejuJudge, TiaohouJudge
from app.core.judgement.arbitrator import ClassicArbitrator


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
    "pillarDetail": {"stemNotes": "甲己合", "branchNotes": "寅午半合"},
}


def test_judgement_chain_steps_order() -> None:
    chain = BaziJudgementChain(use_rag=False)
    report = asyncio.run(chain.run(SAMPLE_CHART))
    step_ids = [s.id for s in report.steps]
    assert step_ids[:3] == ["month", "tiaohou", "geju"]
    assert report.arbitration.confidenceBand in ("strong", "medium", "weak")


def test_geju_judge_uses_month_shishen() -> None:
    verdict = GejuJudge().judge(SAMPLE_CHART)
    assert verdict.role == "geju"
    assert "食神" in verdict.summary


def test_arbitrator_outputs_boundaries() -> None:
    verdicts = [TiaohouJudge().judge(SAMPLE_CHART), GejuJudge().judge(SAMPLE_CHART)]
    arb = ClassicArbitrator().arbitrate(verdicts, [])
    assert arb.judgeOpinions
    assert isinstance(arb.finalBoundaries, list)
