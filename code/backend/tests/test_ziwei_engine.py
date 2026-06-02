import pytest

from app.core.ziwei.engine import ZiweiEngine
from app.core.ziwei.models import ZiweiInput
from app.core.ziwei.rules import ZiweiRules

pytest.importorskip("iztro_py")


def test_ziwei_chart_snapshot() -> None:
    engine = ZiweiEngine()
    result = engine.chart(
        ZiweiInput(
            calendar_type="solar",
            year=1990,
            month=5,
            day=15,
            hour=11,
            minute=30,
            gender=1,
            use_true_solar_time=True,
            longitude=120.0,
            target_year=2026,
            rules=ZiweiRules(),
        )
    )
    chart = result.chart
    assert chart["meta"]["bureau"]
    assert len(chart["palaces"]) == 12
    assert chart["palaces"][0]["name"] == "命宫"
    assert chart["limits"]["decadal"]
    assert chart["limits"]["minor"]
    assert chart["limits"]["yearly"]["targetYear"] == 2026
