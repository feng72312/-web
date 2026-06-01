from __future__ import annotations

from app.core.qimen.engine import QimenEngine
from app.core.qimen.ju_maoshan import maoshan_yuan, qimen_ju_name_maoshan
from app.core.qimen.models import QimenInput


def test_maoshan_ju_name_format():
    name = qimen_ju_name_maoshan(2026, 5, 26, 14, 30)
    assert "局" in name
    assert "元" in name


def test_maoshan_chart_smoke():
    engine = QimenEngine()
    chart = engine.chart(
        QimenInput(
            question="出行",
            category="xingzhan",
            year=2026,
            month=5,
            day=26,
            hour=14,
            minute=30,
            method="maoshan",
        )
    )
    assert chart.meta.get("method") == "maoshan"
    assert len(chart.palaces) == 9


def test_maoshan_yuan_is_string():
    yuan = maoshan_yuan(2026, 5, 26, 14, 30)
    assert yuan in ("上元", "中元", "下元")
