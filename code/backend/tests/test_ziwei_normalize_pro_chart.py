import pytest

from app.core.ziwei.engine import ZiweiEngine
from app.core.ziwei.models import ZiweiInput
from app.core.ziwei.rules import ZiweiRules

pytest.importorskip("iztro_py")


def _sample_chart(*, detail_level: str = "pro") -> dict:
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
            detail_level=detail_level,
            rules=ZiweiRules(),
        )
    )
    return result.chart


def test_pro_chart_palace_position_and_relations() -> None:
    chart = _sample_chart()
    palaces = chart["palaces"]
    assert len(palaces) == 12
    for palace in palaces:
        assert palace["position"]["row"] >= 1
        assert palace["position"]["col"] >= 1
        assert palace["oppositeBranch"]
        assert len(palace["triadBranches"]) == 2
        assert "starGroups" in palace
        assert "mutagenStars" in palace
        assert "hasMalefic" in palace
        assert "brightnessSummary" in palace
        assert "isSoul" in palace
        assert palace["majorStars"]


def test_pro_chart_active_limits() -> None:
    chart = _sample_chart()
    active = chart["limits"]["active"]
    assert active["yearly"]["available"] is True
    assert active["decadal"]["available"] is True
    assert active["monthly"]["available"] is True
    assert active["daily"]["available"] is True
    assert active["hourly"]["available"] is True
    assert active["monthly"]["mutagenStars"]


def test_legacy_limits_fields_preserved() -> None:
    chart = _sample_chart()
    assert chart["limits"]["yearly"]["targetYear"] == 2026
    assert chart["limits"]["decadal"]
    assert chart["limits"]["minor"]


def test_simple_chart_skips_horoscope_layers() -> None:
    chart = _sample_chart(detail_level="simple")
    assert chart["meta"]["detailLevel"] == "simple"
    assert chart["limits"]["yearly"]["available"] is False
    assert chart["limits"]["active"]["yearly"]["available"] is False
    assert chart["limits"]["decadal"]
    assert len(chart["palaces"]) == 12
    palace = chart["palaces"][0]
    assert palace["position"]
    assert palace["majorStars"]
    assert "starGroups" not in palace
