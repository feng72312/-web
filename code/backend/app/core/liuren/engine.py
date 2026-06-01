from __future__ import annotations

from app.core.liuren.adapter import build_chart
from app.core.liuren.models import LiurenInput, LiurenResult


class LiurenEngine:
    def chart(self, data: LiurenInput) -> LiurenResult:
        return build_chart(data)
