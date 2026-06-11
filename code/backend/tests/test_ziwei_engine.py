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
            detail_level="pro",
            rules=ZiweiRules(),
        )
    )
    chart = result.chart
    assert chart["meta"]["bureau"]
    assert chart["meta"]["detailLevel"] == "pro"
    assert len(chart["palaces"]) == 12
    assert chart["palaces"][0]["name"] == "命宫"
    assert chart["limits"]["decadal"]
    assert chart["limits"]["minor"]
    assert chart["limits"]["yearly"]["targetYear"] == 2026
    assert chart["palaces"][0]["position"]
    assert chart["limits"]["active"]["monthly"]["available"] is True


def _raw_year_mutagen_map(table_id):
    from iztro_py import astro
    from iztro_py.i18n import set_language

    from app.core.ziwei.mutagen_tables import apply_mutagen_table_to_chart

    set_language("zh-CN")
    chart = astro.by_solar("1990-5-15", 6, "男")
    apply_mutagen_table_to_chart(chart, table_id)
    mapping = {}
    for palace in chart.palaces:
        for star in palace.major_stars + palace.minor_stars:
            if star.mutagen:
                mapping[star.name] = star.mutagen
    return mapping


def test_mutagen_table_geng_beipai() -> None:
    mapping = _raw_year_mutagen_map("geng_beipai")
    assert mapping.get("tianxiangMaj") == "忌"
    assert mapping.get("tiantongMaj") == "科"
    assert "taiyinMaj" not in mapping


def test_mutagen_table_nan_pai_geng_year() -> None:
    mapping = _raw_year_mutagen_map("nan_pai")
    assert mapping.get("taiyinMaj") == "忌"
    assert mapping.get("tiantongMaj") == "科"
    assert "tianxiangMaj" not in mapping


def test_feixing_school_flying_mutagens() -> None:
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
            detail_level="pro",
            rules=ZiweiRules(chart_school="feixing"),
        )
    )
    chart = result.chart
    assert chart["meta"]["chartSchool"] == "feixing"
    flying_palaces = [p for p in chart["palaces"] if p.get("flyingMutagens")]
    assert len(flying_palaces) == 12
    soul = chart["palaces"][0]
    assert soul["flyingMutagens"]["outbound"]


def test_ziwei_chart_defaults_to_simple() -> None:
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
            rules=ZiweiRules(),
        )
    )
    chart = result.chart
    assert chart["meta"]["detailLevel"] == "simple"
    assert chart["limits"]["yearly"]["available"] is False
