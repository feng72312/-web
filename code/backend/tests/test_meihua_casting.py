from app.core.meihua.engine import MeihuaEngine
from app.core.meihua.models import MeihuaInput


def test_number_cast_produces_chart():
    engine = MeihuaEngine()
    chart = engine.divine(
        MeihuaInput(question="测试", method="number", numbers=[12, 34, 5])
    )
    assert chart.ben_gua.name
    assert len(chart.lines) == 6
    assert chart.ti_gua.name
    assert chart.yong_gua.name
    assert chart.ti_yong_relation


def test_time_cast_produces_chart():
    engine = MeihuaEngine()
    chart = engine.divine(
        MeihuaInput(
            question="测试",
            method="time",
            year=2026,
            month=5,
            day=28,
            hour=12,
            minute=0,
        )
    )
    assert chart.meta.get("castNote")
    assert chart.hu_gua is not None or chart.ben_gua.name
