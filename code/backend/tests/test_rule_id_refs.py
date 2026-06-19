from __future__ import annotations

import asyncio

from app.core.judgement.chain import BaziJudgementChain
from app.core.judgement.evidence import extract_rule_id_refs

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


def test_extract_rule_id_refs_from_chain() -> None:
    report = asyncio.run(BaziJudgementChain(use_rag=False).run(SAMPLE_CHART))
    payload = report.to_dict()
    refs = extract_rule_id_refs(payload)
    assert refs
    assert all(row.get("ruleId") for row in refs)
