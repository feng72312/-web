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
