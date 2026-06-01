from __future__ import annotations

from app.core.liuren.engine import LiurenEngine
from app.core.liuren.models import LiurenInput


def test_liuren_chart_smoke():
    engine = LiurenEngine()
    result = engine.chart(
        LiurenInput(
            question="出行吉凶",
            cast_method="both",
            year=2026,
            month=5,
            day=26,
            hour=14,
            minute=30,
        )
    )
    d = result.to_dict()
    assert d["liuren"]["geJu"]["name"] or d["liuren"]["siKe"]
    assert d["liuren"]["sanChuan"].get("chu")
    assert len(d["liuren"]["tianDiPan"]["palaces"]) >= 12
    assert d["jinkou"]["renYuan"]


def test_liuren_jinkou_only():
    engine = LiurenEngine()
    result = engine.chart(
        LiurenInput(
            question="求财",
            cast_method="jinkou",
            jinkou_difen="子",
            year=2026,
            month=5,
            day=26,
            hour=10,
        )
    )
    d = result.to_dict()
    assert d.get("jinkou")
    assert d["jinkou"]["difen"] == "子"
    assert "liuren" not in d or d.get("liuren") is None
