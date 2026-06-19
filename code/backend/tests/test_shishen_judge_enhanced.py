from __future__ import annotations

from app.core.judgement.judges import ShiShenJudge
from app.core.knowledge.factory import get_knowledge_service
from app.core.knowledge.shishen_context import build_shishen_lookup_keys, lookup_shishen_rows

SAMPLE_CHART = {
    "dayMaster": "甲",
    "dayMasterWuxing": "木",
    "gender": "male",
    "pillars": {
        "year": {"gan": "甲", "zhi": "子", "shishenGan": "比肩"},
        "month": {"gan": "丙", "zhi": "寅", "shishenGan": "食神"},
        "day": {"gan": "甲", "zhi": "午", "shishenGan": ""},
        "hour": {"gan": "乙", "zhi": "亥", "shishenGan": "劫财"},
    },
}


def test_build_shishen_lookup_keys_includes_liuqin() -> None:
    keys = build_shishen_lookup_keys(SAMPLE_CHART)
    aspects = {k.get("aspect") for k in keys if k.get("category") == "liuqin"}
    assert "general" in aspects
    assert "male_spouse" in aspects


def test_shishen_judge_hits_graph_when_enabled() -> None:
    service = get_knowledge_service()
    verdict = ShiShenJudge().judge(SAMPLE_CHART)
    assert verdict.role == "shishen"
    assert verdict.boundary
    if service.enabled:
        rows = lookup_shishen_rows(service.store, SAMPLE_CHART)
        if rows:
            assert verdict.ruleIds
            assert verdict.conclusionKind == "classic_direct"
