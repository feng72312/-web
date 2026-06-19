from __future__ import annotations

from app.benchmark.contest8_eval import QuestionResult


def test_question_result_includes_marriage_subtheme_field() -> None:
    r = QuestionResult(
        question_id="P001-Q1",
        year=2024,
        gold="A",
        predicted="A",
        correct=True,
        raw_response="答案: A",
        marriage_subtheme="marriage-narrative",
    )
    payload = r.__dict__
    assert payload["marriage_subtheme"] == "marriage-narrative"
