from __future__ import annotations

from app.core.fusion.models import QuestionScope

OUTLINE_KEYWORDS = (
    "格局",
    "用神",
    "喜忌",
    "一生",
    "总体",
    "大运",
    "运势",
    "性格",
    "命局",
    "体用",
    "调候",
    "概括",
    "大势",
)

DETAIL_KEYWORDS = (
    "哪年",
    "何时",
    "是否",
    "能不能",
    "结婚",
    "离婚",
    "生子",
    "流产",
    "官非",
    "牢狱",
    "车祸",
    "骨折",
    "手术",
    "住院",
    "去世",
    "离世",
    "职业",
    "工作",
    "收入",
    "房产",
    "搬迁",
    "年发生",
    "这一年",
)


def classify_question(question: str, default_scope: QuestionScope = "life_outline") -> QuestionScope:
    text = (question or "").strip()
    if not text:
        return default_scope
    has_outline = any(kw in text for kw in OUTLINE_KEYWORDS)
    has_detail = any(kw in text for kw in DETAIL_KEYWORDS)
    if has_outline and has_detail:
        return "mixed"
    if has_detail:
        return "event_detail"
    if has_outline:
        return "life_outline"
    return default_scope
