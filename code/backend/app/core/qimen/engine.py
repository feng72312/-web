from __future__ import annotations

from app.core.qimen.adapter import build_chart
from app.core.qimen.models import QimenChart, QimenInput


class QimenEngine:
    """Shi-jia Qimen chart builder (chai bu default, zhi run optional)."""

    def chart(self, data: QimenInput) -> QimenChart:
        return build_chart(data)
