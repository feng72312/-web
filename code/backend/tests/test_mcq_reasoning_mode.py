from __future__ import annotations

from app.core.knowledge.mcq_reasoning_mode import (
    is_year_option_mcq,
    should_structured_mcq_reasoning,
)


def test_structured_marriage() -> None:
    q = "命主婚姻状况如何?"
    assert should_structured_mcq_reasoning(q, ["A 已婚", "B 离婚", "C 单身", "D 再婚"])


def test_year_option_mcq() -> None:
    opts = ["A 2010年", "B 2017年", "C 2022年", "D 1995年"]
    assert is_year_option_mcq(opts)


def test_year_option_mcq_chinese_comma() -> None:
    opts = [
        "A 中七毕业",
        "B 2002年升学内地，2006年大学毕业",
        "C 预科后升本地大学，2004年大学毕业",
        "D 中五后，1998年出国留学",
    ]
    assert is_year_option_mcq(opts)


def test_structured_tiaohou_keyword() -> None:
    q = "此命调候用神为何?"
    assert should_structured_mcq_reasoning(q, ["A 木", "B 火", "C 土", "D 金"])


def test_structured_career_theme() -> None:
    q = "命主职业财运如何?"
    assert should_structured_mcq_reasoning(q, ["A 经商", "B 公职", "C 技艺", "D 务农"])
