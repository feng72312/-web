from __future__ import annotations

from app.benchmark.contest8_dataset import (
    extract_single_fit_letter_from_reasoning,
    parse_contest_answer_letter,
)


def test_extract_single_fit() -> None:
    text = """
【选项排除】
A: 不符合 - x
B: 符合 - y
C: 不符合 - z
D: 不符合 - w
【结论】
选B
答案: D
"""
    assert extract_single_fit_letter_from_reasoning(text) == "B"


def test_reconcile_prefers_single_fit() -> None:
    text = """
【选项排除】
A: 不符合
B: 符合 - ok
C: 不符合
D: 不符合
答案: D
"""
    letter, source = parse_contest_answer_letter(
        text, prefer_final_line=True, reconcile_reasoning=True
    )
    assert letter == "B"
    assert source == "reasoning_fit"


def test_final_line_when_no_single_fit() -> None:
    text = "思考...\n答案: C"
    letter, source = parse_contest_answer_letter(
        text, prefer_final_line=True, reconcile_reasoning=True
    )
    assert letter == "C"
    assert source == "final_line"
