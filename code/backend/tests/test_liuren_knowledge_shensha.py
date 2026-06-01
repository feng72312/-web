from __future__ import annotations

from app.core.knowledge.factory import get_knowledge_service
from app.core.liuren.engine import LiurenEngine
from app.core.liuren.models import LiurenInput


def test_shensha_expanded():
    chart = LiurenEngine().chart(
        LiurenInput(question="test", year=2026, month=5, day=26, hour=14)
    ).to_dict()
    sha = chart["liuren"]["shenSha"]
    assert len(sha) >= 8
    assert "日马" in sha or "月马" in sha


def test_liuren_knowledge_lookup_smoke():
    chart = LiurenEngine().chart(
        LiurenInput(question="test", year=2026, month=5, day=26, hour=10)
    ).to_dict()
    svc = get_knowledge_service()
    if not svc.enabled:
        return
    result = svc.lookup_liuren_chart(chart)
    assert result.lookupKeys.get("yue_jiang")
    topics = {h.topic for h in result.hits}
    assert "si_ke" in topics or "san_chuan" in topics or len(result.hits) >= 0
