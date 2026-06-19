from __future__ import annotations

from app.core.judgement.judges import GejuJudge, QiShiJudge, ShiShenJudge, SuiYunJudge
from app.core.knowledge.factory import get_knowledge_service
from app.core.knowledge.keys import build_chart_lookup_keys

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


def test_lookup_keys_include_new_topics() -> None:
    keys = build_chart_lookup_keys(SAMPLE_CHART)
    assert "geju" in keys
    assert "qishi" in keys
    assert "shishen" in keys
    assert "suiyun" in keys


def test_geju_judge_reads_graph_when_enabled() -> None:
    service = get_knowledge_service()
    verdict = GejuJudge().judge(SAMPLE_CHART)
    assert verdict.role == "geju"
    if service.enabled:
        key = build_chart_lookup_keys(SAMPLE_CHART)["geju"]
        if service.store.lookup("geju", key):
            assert verdict.ruleIds
            assert verdict.conclusionKind == "classic_direct"
            assert len(verdict.ruleIds) >= 2


def test_geju_alias_maps_partial_wealth_to_wealth() -> None:
    from app.core.knowledge.keys import normalize_geju_name

    assert normalize_geju_name("偏财") == "正财"
    assert normalize_geju_name("劫财") == "比肩"


def test_qishi_judge_reads_graph_when_enabled() -> None:
    service = get_knowledge_service()
    verdict = QiShiJudge().judge(SAMPLE_CHART)
    assert verdict.role == "qishi"
    if service.enabled:
        key = build_chart_lookup_keys(SAMPLE_CHART)["qishi"]
        if service.store.lookup("qishi", key):
            assert verdict.ruleIds


def test_shishen_and_suiyun_judges_return_verdicts() -> None:
    shishen = ShiShenJudge().judge(SAMPLE_CHART)
    suiyun = SuiYunJudge().judge(SAMPLE_CHART)
    assert shishen.role == "shishen"
    assert suiyun.role == "suiyun"
    assert suiyun.summary
