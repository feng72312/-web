"""Theme-matched few-shot examples from train split only."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from app.benchmark.contest8_dataset import SPLIT_YEARS, flatten_questions, normalize_answer_letter
from app.benchmark.contest8_rag import infer_question_theme


def _example_from_question(q) -> dict[str, Any]:
    answer = normalize_answer_letter(q.answer)
    answer_text = ""
    if answer and q.options:
        idx = ord(answer) - ord("A")
        if 0 <= idx < len(q.options):
            answer_text = q.options[idx]
    return {
        "question_id": q.question_id,
        "year": q.year,
        "question": q.question,
        "answer": answer,
        "answer_text": answer_text,
        "theme": infer_question_theme(q.question),
    }


@lru_cache(maxsize=1)
def load_train_gold_examples() -> tuple[dict[str, Any], ...]:
    items = []
    for q in flatten_questions(SPLIT_YEARS["train"]):
        if not q.answer:
            continue
        items.append(_example_from_question(q))
    return tuple(items)


def select_fewshot_by_theme(
    theme: str,
    *,
    exclude_question_id: str | None = None,
    max_items: int = 3,
) -> list[dict[str, Any]]:
    pool = list(load_train_gold_examples())
    same = [
        ex
        for ex in pool
        if ex.get("theme") == theme
        and ex.get("question_id") != exclude_question_id
    ]
    fallback = [
        ex
        for ex in pool
        if ex.get("theme") == "综合"
        and ex.get("question_id") != exclude_question_id
    ]
    out: list[dict[str, Any]] = []
    for source in (same, fallback, pool):
        for ex in source:
            if ex.get("question_id") in {x.get("question_id") for x in out}:
                continue
            if exclude_question_id and ex.get("question_id") == exclude_question_id:
                continue
            out.append(ex)
            if len(out) >= max_items:
                return out
    return out
