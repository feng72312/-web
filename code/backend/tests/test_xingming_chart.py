from __future__ import annotations

import pytest

pytest.importorskip("swisseph")

from app.core.xingming.engine import XingmingEngine
from app.core.xingming.models import XingmingInput


def test_xingming_chart_structure():
    engine = XingmingEngine()
    result = engine.chart(
        XingmingInput(
            year=1990,
            month=6,
            day=15,
            hour=12,
            minute=0,
            gender=1,
            longitude=120.0,
            latitude=35.0,
        )
    )
    chart = result.to_dict()
    assert chart["meta"]["engine"] == "xingming"
    assert len(chart["bodies"]) == 11
    assert len(chart["palaces"]) == 12
    assert chart["mingPalace"]["name"] == "\u547d\u5bab"
    assert chart["rulesMeta"]["siYuModel"] == "guolao_v1"
