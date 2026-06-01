from __future__ import annotations

from app.core.qimen.engine import QimenEngine
from app.core.qimen.models import QimenInput
from app.core.qimen.solar_time import apply_true_solar_time
from datetime import datetime


def test_solar_time_offset():
    dt = datetime(2026, 5, 26, 12, 0, 0)
    west = apply_true_solar_time(dt, 90.0, 120.0)
    assert west < dt


def test_chaibu_chart_smoke():
    engine = QimenEngine()
    chart = engine.chart(
        QimenInput(
            question="出行是否顺利",
            category="xingzhan",
            year=2026,
            month=5,
            day=26,
            hour=14,
            minute=30,
            method="chaibu",
            direction="东",
        )
    )
    d = chart.to_dict()
    assert d["ju"]["juName"]
    assert len(d["palaces"]) == 9
    assert d["zhiFuZhiShi"]["zhiFuStar"]
    assert d["fourPillars"]["day"]


def test_ju_override_debug():
    engine = QimenEngine()
    chart = engine.chart(
        QimenInput(
            question="测试",
            year=2026,
            month=5,
            day=26,
            hour=14,
            minute=30,
            ju_override=8,
        )
    )
    assert chart.ju.ju_number == 8
    assert chart.meta.get("debugJuOverride") is True
