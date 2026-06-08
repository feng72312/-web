from __future__ import annotations

from app.core.fusion.models import ChannelVerdict, QuestionScope

TriplePreferred = str  # agree | bazi | ziwei | xingming | split


SCOPE_LABELS = {
    "life_outline": "\u5927\u52bf\u91cd\u547d(\u5b50\u5e73\u4e3a\u4e3b)",
    "stage_turn": "\u9636\u6bb5\u8f6c\u6298\u91cd\u5929\u8c61(\u661f\u547d\u4e3a\u4e3b)",
    "event_detail": "\u4e8b\u9879\u91cd\u547d\u7406(\u547d\u7406\u4e3a\u4e3b)",
    "mixed": "\u4e09\u901a\u9053\u5206\u8ff0",
}


def _available(*channels: ChannelVerdict) -> list[ChannelVerdict]:
    return [c for c in channels if c.available]


def _stances_agree(a: ChannelVerdict, b: ChannelVerdict) -> bool:
    if not a.available or not b.available:
        return False
    sa, sb = a.stance.strip(), b.stance.strip()
    if sa in ("", "\u672a\u5b9a") or sb in ("", "\u672a\u5b9a"):
        return False
    return sa == sb


def merge_triple_verdicts(
    question: str,
    bazi: ChannelVerdict,
    ziwei: ChannelVerdict,
    xingming: ChannelVerdict,
    *,
    default_scope: QuestionScope = "life_outline",
) -> tuple[str, QuestionScope, TriplePreferred]:
    from app.core.fusion.classify_triple import classify_triple_question

    scope = classify_triple_question(question, default_scope)
    channels = _available(bazi, ziwei, xingming)
    if not channels:
        return "\u4e09\u901a\u9053\u5747\u4e0d\u53ef\u7528.", scope, "split"

    if scope == "stage_turn" and xingming.available:
        preferred: TriplePreferred = "xingming"
    elif scope == "event_detail":
        preferred = "bazi"
    elif scope == "life_outline":
        preferred = "bazi"
    else:
        preferred = "split"

    agreed = (
        _stances_agree(bazi, ziwei)
        or _stances_agree(bazi, xingming)
        or _stances_agree(ziwei, xingming)
    )
    if agreed:
        preferred = "agree"

    if preferred == "agree":
        lead = next((c for c in channels if c.summary), channels[0])
        merged = (
            f"\u3010\u4e09\u76d8\u4e00\u81f4\u3011{lead.stance}\n"
            f"\u5b50\u5e73: {bazi.summary}\n"
            f"\u7d2b\u5fae: {ziwei.summary}\n"
            f"\u661f\u547d: {xingming.summary}"
        )
        return merged, scope, preferred

    if preferred == "xingming":
        merged = (
            f"\u3010\u7efc\u5408\u00b7\u5929\u8c61\u4e3a\u4e3b\u3011{SCOPE_LABELS.get(scope, '')}\n"
            f"\u661f\u547d: {xingming.summary}\n"
            f"\u5b50\u5e73: {bazi.summary}\n"
            f"\u7d2b\u5fae: {ziwei.summary}"
        )
    elif preferred == "bazi":
        merged = (
            f"\u3010\u7efc\u5408\u00b7\u547d\u7406\u4e3a\u4e3b\u3011\n"
            f"\u5b50\u5e73: {bazi.summary}\n"
            f"\u7d2b\u5fae: {ziwei.summary}\n"
            f"\u661f\u547d: {xingming.summary}"
        )
    else:
        merged = (
            f"\u3010\u7efc\u5408\u00b7\u5206\u8ff0\u3011{SCOPE_LABELS.get(scope, '')}\n"
            f"\u3010\u5b50\u5e73\u3011{bazi.summary}\n"
            f"\u3010\u7d2b\u5fae\u3011{ziwei.summary}\n"
            f"\u3010\u661f\u547d\u3011{xingming.summary}"
        )
    return merged, scope, preferred
