from __future__ import annotations

import asyncio

from app.core.judgement.arbitrator import ClassicArbitrator
from app.core.judgement.chain import BaziJudgementChain
from app.core.judgement.models import JudgeVerdict

CHART_WITH_CHONG = {
    "dayMaster": "甲",
    "dayMasterWuxing": "木",
    "wuxingCount": {"木": 2, "火": 1, "土": 1, "金": 2, "水": 2},
    "pillars": {
        "year": {"gan": "甲", "zhi": "子", "shishenGan": "比肩"},
        "month": {"gan": "丙", "zhi": "午", "shishenGan": "食神"},
        "day": {"gan": "甲", "zhi": "午"},
        "hour": {"gan": "乙", "zhi": "亥", "shishenGan": "劫财"},
    },
    "dayun": [{"ganzhi": "丁卯", "startAge": 8, "endAge": 17}],
    "pillarDetail": {
        "stemNotes": "甲己合",
        "branchNotes": "子午冲、子丑合",
        "columns": [{"shenSha": [{"name": "桃花"}]}, {}, {}, {}],
    },
}


def test_arbitrator_tiaohou_interactions_conflict() -> None:
    verdicts = [
        JudgeVerdict(role="tiaohou", classic="穷通宝鉴", summary="调候偏暖", stance="favorable"),
        JudgeVerdict(
            role="interactions",
            classic="子平真诠",
            summary="地支: 子午冲",
            stance="unfavorable",
        ),
    ]
    conflicts = ClassicArbitrator().arbitrate(verdicts, []).conflicts
    assert any("调候" in item and "刑冲" in item for item in conflicts)


def test_arbitrator_suiyun_interactions_conflict() -> None:
    verdicts = [
        JudgeVerdict(role="suiyun", classic="三命通会", summary="岁运见扶", stance="favorable"),
        JudgeVerdict(
            role="interactions",
            classic="子平真诠",
            summary="地支: 子午冲",
            stance="unfavorable",
        ),
    ]
    conflicts = ClassicArbitrator().arbitrate(verdicts, []).conflicts
    assert any("岁运" in item and "刑冲" in item for item in conflicts)


def test_arbitrator_tiaohou_suiyun_conflict() -> None:
    verdicts = [
        JudgeVerdict(role="tiaohou", classic="穷通宝鉴", summary="偏寒", stance="favorable"),
        JudgeVerdict(role="suiyun", classic="三命通会", summary="运逆", stance="unfavorable"),
    ]
    conflicts = ClassicArbitrator().arbitrate(verdicts, []).conflicts
    assert any("调候" in item and "岁运" in item for item in conflicts)


def test_chain_surfaces_interaction_related_conflicts() -> None:
    report = asyncio.run(BaziJudgementChain(use_rag=False).run(CHART_WITH_CHONG))
    interactions = next(
        (v for v in report.arbitration.judgeOpinions if v.role == "interactions"),
        None,
    )
    assert interactions is not None
    assert interactions.stance in ("unfavorable", "conditional")
    assert len(report.arbitration.conflicts or []) >= 1
