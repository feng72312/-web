from __future__ import annotations

from app.core.judgement.evidence import load_case_references
from app.core.knowledge.case_factory import get_case_store

SAMPLE_CHART = {
    "dayMaster": "甲",
    "pillars": {
        "month": {"zhi": "寅", "shishenGan": "食神"},
    },
}


def test_case_store_loads_records() -> None:
    store = get_case_store()
    if not store.enabled:
        return
    assert store.stats()["caseCount"] >= 1


def test_case_reference_output_is_non_judging() -> None:
    refs = load_case_references(SAMPLE_CHART, limit=2)
    for row in refs:
        assert row.get("evidenceRole") == "case_reference"
        assert row.get("canJudge") is False
        assert row.get("forbiddenApply") is True
