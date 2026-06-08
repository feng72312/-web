from __future__ import annotations

from app.core.fengshui import bazhai
from app.core.fengshui import xuankong
from app.core.fengshui.engine import FengshuiEngine
from app.core.fengshui.models import FengshuiInput


def test_ming_gua_male_1985():
    assert bazhai.calc_ming_gua_number(1985, 1) == 6


def test_ming_gua_female_1990():
    assert bazhai.calc_ming_gua_number(1990, 0) == 8


def test_ming_gua_male_2000():
    assert bazhai.calc_ming_gua_number(2000, 1) == 9


def test_zhai_gua_from_zi():
    assert bazhai.calc_zhai_gua_number("zi") == 1


def test_bazhai_chart_smoke():
    engine = FengshuiEngine()
    chart = engine.chart(
        FengshuiInput(
            question="这套房子适合长期居住吗",
            birth_year=1985,
            gender=1,
            sitting_mountain="zi",
            scene="residence",
        )
    ).to_dict()
    assert chart["mingGua"]["groupLabel"] == "西四命"
    assert chart["zhaiGua"]["groupLabel"] == "东四宅"
    assert chart["compatible"] is False
    assert len(chart["directions"]) == 8
    assert len(chart["palaces"]) == 8
    assert chart["zhaiGua"]["label"] == "坐子向午"


def test_compatible_dongsi():
    engine = FengshuiEngine()
    chart = engine.chart(
        FengshuiInput(
            question="床位如何调整",
            birth_year=1988,
            gender=0,
            sitting_mountain="mao",
        )
    ).to_dict()
    assert chart["mingGua"]["group"] == "dongsi"
    assert chart["zhaiGua"]["group"] == "dongsi"
    assert chart["compatible"] is True


def test_xuankong_period_2020():
    period = xuankong.calc_period(2020)
    assert period["number"] == 8


def test_xuankong_chart_smoke():
    engine = FengshuiEngine()
    chart = engine.chart(
        FengshuiInput(
            question="这套房财运如何",
            method="xuankong",
            build_year=2020,
            sitting_mountain="hai",
        )
    ).to_dict()
    assert chart["xuankong"]["period"]["number"] == 8
    assert chart["xuankong"]["label"] == "坐亥向巳"
    assert len(chart["xuankong"]["combinedPan"]) == 9


def test_xuankong_with_flow_year():
    engine = FengshuiEngine()
    chart = engine.chart(
        FengshuiInput(
            question="今年财位",
            method="xuankong",
            build_year=2020,
            flow_year=2026,
            sitting_mountain="zi",
        )
    ).to_dict()
    assert chart["xuankong"]["flowYear"] == 2026
    assert chart["xuankong"]["flowPan"]
