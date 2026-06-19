from __future__ import annotations

from app.core.knowledge.children_subtheme import infer_children_subtheme


def test_birth_year_subtheme() -> None:
    q = "命主哪一年生孩子?"
    opts = ["A2012", "B2013", "C2015", "D2018"]
    assert infer_children_subtheme(q, opts) == "children-birth-year"


def test_dayun_span_subtheme() -> None:
    q = "虚龄35至44甲戌大运期间，其子女运？"
    opts = [
        "A 发妻诞下三子，均平安",
        "B 发妻头胎诞下一子，可惜儿子有损",
        "C 得一子，为资优生；1996丙子年参加国际比赛获奖",
        "D 得一子，于1996丙子年命主安排该子到英国读书",
    ]
    assert infer_children_subtheme(q, opts) == "children-dayun-span"


def test_status_subtheme() -> None:
    q = "命主的婚恋和子女情况？"
    opts = [
        "A. 婚恋不顺，经人介绍，2011年结婚，2014年生育一女。",
        "B. 2011年与中学同学奉子成婚，2012年初生一子，2015年生第二子。",
        "C. 多次恋爱，至今未婚，无子女。",
        "D. 2018年离婚后一直独身，无子女。",
    ]
    assert infer_children_subtheme(q, opts) == "children-status"


def test_non_children_returns_none() -> None:
    assert infer_children_subtheme("命主学历如何?", ["A. 大学"]) is None
