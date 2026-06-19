from __future__ import annotations

from app.core.knowledge.marriage_subtheme import infer_marriage_subtheme


def test_year_event_subtheme() -> None:
    q = "命主哪一年再婚?"
    opts = ["A 2017", "B 2018", "C 2019", "D 2020"]
    assert infer_marriage_subtheme(q, opts) == "marriage-year-event"


def test_status_subtheme() -> None:
    q = "截至2017年9月, 命主的感情婚姻状况?"
    opts = [
        "A. 至今美满",
        "B. 2010年结婚, 2015年离婚",
        "C. 从未结婚",
        "D. 恋爱中",
    ]
    assert infer_marriage_subtheme(q, opts) == "marriage-status"


def test_narrative_subtheme() -> None:
    q = "命主的婚姻情况?"
    opts = [
        "A. 2011年结婚, 2014年生育",
        "B. 2018年离婚后一直独身",
        "C. 多次恋爱, 至今未婚",
        "D. 奉子成婚, 育有二子",
    ]
    assert infer_marriage_subtheme(q, opts) == "marriage-narrative"


def test_affair_subtheme() -> None:
    q = "命主是否有外遇?"
    opts = [
        "A. 有外遇",
        "B. 无外遇",
        "C. 曾有私情",
        "D. 从未出轨",
    ]
    assert infer_marriage_subtheme(q, opts) == "marriage-affair"


def test_mixed_year_single_is_narrative() -> None:
    q = "此命何年结婚?"
    opts = ["A 1999", "B 2002", "C 2006", "D 到2022年为止，单身"]
    assert infer_marriage_subtheme(q, opts) == "marriage-narrative"


def test_non_marriage_returns_none() -> None:
    assert infer_marriage_subtheme("命主学历如何?", ["A. 大学"]) is None
