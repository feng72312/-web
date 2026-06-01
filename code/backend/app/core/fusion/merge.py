from __future__ import annotations

from app.core.fusion.classify import classify_question
from app.core.fusion.models import ChannelVerdict, FusionResult, PreferredChannel, QuestionScope

SCOPE_LABELS = {
    "life_outline": "大势重命(八字为主)",
    "event_detail": "此事重卦(六爻为主)",
    "mixed": "命局与此事分述",
}


def _stances_agree(a: ChannelVerdict, b: ChannelVerdict) -> bool:
    if not a.available or not b.available:
        return False
    sa, sb = a.stance.strip(), b.stance.strip()
    if sa in ("", "未定") or sb in ("", "未定"):
        return False
    return sa == sb


def _pick_preferred(scope: QuestionScope, agreed: bool) -> PreferredChannel:
    if agreed:
        return "agree"
    if scope == "event_detail":
        return "liuyao"
    if scope == "life_outline":
        return "bazi"
    return "split"


def _build_merged_summary(
    scope: QuestionScope,
    preferred: PreferredChannel,
    bazi: ChannelVerdict,
    liuyao: ChannelVerdict,
    agreed: bool,
) -> str:
    if not bazi.available and not liuyao.available:
        return "八字与六爻通道均不可用, 请检查 AI 与 RAG 配置."
    if bazi.available and not liuyao.available:
        return f"【综合·仅八字】{bazi.summary}"
    if liuyao.available and not bazi.available:
        return f"【综合·仅六爻】{liuyao.summary}"

    if agreed:
        return (
            f"【综合·一致】八字与卦象倾向均为「{bazi.stance}」。\n"
            f"八字: {bazi.summary}\n"
            f"六爻: {liuyao.summary}"
        )

    if preferred == "split" or scope == "mixed":
        return (
            f"【综合·分述】{SCOPE_LABELS[scope]}\n"
            f"【命局】({bazi.stance}) {bazi.summary}\n"
            f"【此事卦象】({liuyao.stance}) {liuyao.summary}"
        )

    if preferred == "liuyao":
        return (
            f"【综合·此事重卦】卦象({liuyao.stance}): {liuyao.summary}\n"
            f"【命局背景】({bazi.stance}): {bazi.summary}"
        )

    return (
        f"【综合·大势重命】命局({bazi.stance}): {bazi.summary}\n"
        f"【卦象参考】({liuyao.stance}): {liuyao.summary}"
    )


def merge_mcq_letters(
    bazi_letter: str,
    liuyao_letter: str,
    question: str,
    *,
    default_scope: QuestionScope = "life_outline",
) -> tuple[str, QuestionScope, str]:
    """Return merged letter, scope, and preferred channel for contest MCQ."""
    scope = classify_question(question, default_scope)
    if bazi_letter and liuyao_letter and bazi_letter == liuyao_letter:
        return bazi_letter, scope, "agree"
    if scope == "event_detail":
        letter = liuyao_letter or bazi_letter
        return letter, scope, "liuyao"
    if scope == "life_outline":
        letter = bazi_letter or liuyao_letter
        return letter, scope, "bazi"
    letter = bazi_letter or liuyao_letter
    return letter, scope, "split"


def merge_verdicts(
    question: str,
    bazi: ChannelVerdict,
    liuyao: ChannelVerdict,
    *,
    default_scope: QuestionScope = "life_outline",
) -> FusionResult:
    scope = classify_question(question, default_scope)
    agreed = _stances_agree(bazi, liuyao)
    preferred = _pick_preferred(scope, agreed)
    merged = _build_merged_summary(scope, preferred, bazi, liuyao, agreed)
    return FusionResult(
        question=question,
        question_scope=scope,
        agreed=agreed,
        preferred_channel=preferred,
        bazi=bazi,
        liuyao=liuyao,
        merged_summary=merged,
        weight_note=SCOPE_LABELS[scope],
    )
