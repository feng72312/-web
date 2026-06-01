from __future__ import annotations

from app.core.knowledge.factory import get_knowledge_service
from app.core.qimen.engine import QimenEngine
from app.core.qimen.models import QimenInput


def test_lookup_qimen_chart_does_not_crash():
    chart = QimenEngine().chart(
        QimenInput(
            question="出行是否顺利",
            year=2026,
            month=5,
            day=29,
            hour=12,
            method="chaibu",
        )
    ).to_dict()
    svc = get_knowledge_service()
    if not svc.enabled:
        return
    result = svc.lookup_qimen_chart(chart)
    assert isinstance(result.lookupKeys, dict)
    assert isinstance(result.hits, list)
