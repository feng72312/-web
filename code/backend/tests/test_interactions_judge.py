from __future__ import annotations

import asyncio

from app.core.judgement.chain import BaziJudgementChain
from app.core.judgement.judges import InteractionsJudge
from app.core.knowledge.factory import get_knowledge_service
from app.core.knowledge.keys_interactions import detect_interaction_patterns

CHART_WITH_CHONG = {
    "dayMaster": "甲",
    "dayMasterWuxing": "木",
    "wuxingCount": {"木": 2, "火": 1, "土": 1, "金": 2, "水": 2},
    "pillars": {
        "year": {"gan": "甲", "zhi": "子"},
        "month": {"gan": "丙", "zhi": "午", "shishenGan": "食神"},
        "day": {"gan": "甲", "zhi": "午"},
        "hour": {"gan": "乙", "zhi": "亥", "shishenGan": "劫财"},
    },
    "dayun": [{"ganzhi": "丁卯", "startAge": 8, "endAge": 17}],
    "pillarDetail": {
        "stemNotes": "甲己合",
        "branchNotes": "子午冲、子丑合",
        "columns": [
            {"shenSha": [{"name": "桃花"}, {"name": "驿马"}]},
            {"shenSha": []},
            {"shenSha": []},
            {"shenSha": []},
        ],
    },
}


def test_detect_interaction_patterns() -> None:
    patterns = detect_interaction_patterns(CHART_WITH_CHONG)
    assert "stem_he" in patterns
    assert "branch_chong" in patterns
    assert "branch_he" in patterns
    assert "shensha" in patterns


def test_interactions_judge_returns_rule_ids_when_graph_enabled() -> None:
    service = get_knowledge_service()
    verdict = InteractionsJudge().judge(CHART_WITH_CHONG)
    assert verdict.role == "interactions"
    assert "冲" in verdict.summary or "合" in verdict.summary
    if service.enabled and service.store.lookup(
        "interactions", {"pattern": "branch_chong", "category": "pillar_interaction"}
    ):
        assert verdict.ruleIds
        assert verdict.conclusionKind == "classic_direct"


def test_chain_includes_interactions_opinion() -> None:
    report = asyncio.run(BaziJudgementChain(use_rag=False).run(CHART_WITH_CHONG))
    roles = [op.role for op in report.arbitration.judgeOpinions]
    assert "interactions" in roles
    step = next(item for item in report.steps if item.id == "interactions")
    assert step.status == "ok"
    assert step.summary
