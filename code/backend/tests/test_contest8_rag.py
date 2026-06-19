from __future__ import annotations

from app.benchmark.contest8_rag import infer_question_theme


def test_career_override_after_graduation() -> None:
    q = "命主毕业后从事什么行业？"
    assert infer_question_theme(q) == "职业财运"


def test_major_subject_is_career() -> None:
    q = "命主大学时期读什么科系？"
    assert infer_question_theme(q) == "职业财运"


def test_pure_education_stays_education() -> None:
    q = "命主的学历状况如何？"
    assert infer_question_theme(q) == "学历"
