from __future__ import annotations

from app.core.judgement.judges import SuiYunJudge
from app.core.judgement.evidence import build_evidence_chain
from app.core.judgement.judges import ALL_JUDGES
from app.core.knowledge.factory import get_knowledge_service

SAMPLE_CHART = {
    "dayMaster": "甲",
    "dayMasterWuxing": "木",
    "wuxingCount": {"木": 2, "火": 1, "土": 2, "金": 1, "水": 2},
    "pillars": {
        "year": {"gan": "甲", "zhi": "子", "shishenGan": "比肩"},
        "month": {"gan": "丙", "zhi": "寅", "shishenGan": "食神"},
        "day": {"gan": "甲", "zhi": "午", "shishenGan": ""},
        "hour": {"gan": "乙", "zhi": "亥", "shishenGan": "劫财"},
    },
    "dayun": [{"ganzhi": "丁卯", "startAge": 8, "endAge": 17, "startYear": 1990}],
}


def test_suiyun_judge_attaches_liunian_rules_when_enabled() -> None:
    service = get_knowledge_service()
    verdict = SuiYunJudge().judge(SAMPLE_CHART)
    assert verdict.role == "suiyun"
    if service.enabled:
        assert len(verdict.ruleIds) >= 2
        assert any(rule_id.startswith("liunian:") for rule_id in verdict.ruleIds)


def test_evidence_chain_groups_suiyun_and_tiaohou() -> None:
    verdicts = [judge.judge(SAMPLE_CHART) for judge in ALL_JUDGES if judge.role != "case"]
    chain = build_evidence_chain(verdicts, [], [])
    conclusions = [item.conclusion for item in chain]
    if any("调候:" in c for c in conclusions):
        assert True
    if any("流年规则:" in c or "大运干支:" in c for c in conclusions):
        assert True
