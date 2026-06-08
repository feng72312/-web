from __future__ import annotations

from app.core.fusion.classify import classify_question
from app.core.fusion.models import QuestionScope

STAGE_TURN_KEYWORDS = (
    "\u592a\u5c81",
    "\u9650\u8fd0",
    "\u586b\u6069",
    "\u9636\u6bb5",
    "\u8f6c\u6298",
    "\u5929\u8c61",
    "\u4e03\u653f",
    "\u56db\u4f59",
    "\u5bbf\u5ea6",
    "\u5bf8",
)


def classify_triple_question(
    question: str,
    default_scope: QuestionScope = "life_outline",
) -> QuestionScope:
    text = (question or "").strip()
    if any(kw in text for kw in STAGE_TURN_KEYWORDS):
        return "stage_turn"
    scope = classify_question(question, default_scope)
    if scope == "mixed":
        return "mixed"
    return scope
