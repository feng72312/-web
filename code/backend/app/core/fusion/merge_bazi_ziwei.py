"""Merge Bazi and Ziwei MCQ letters for Contest8 fusion."""

from __future__ import annotations

from app.benchmark.contest8_rag import infer_question_theme

PreferredBaziZiwei = str  # agree | bazi | ziwei | arbitrate

ZIWEI_PREFERRED_THEMES: frozenset[str] = frozenset(
    {"婚姻感情", "健康疾病", "官非"}
)

BAZI_PREFERRED_THEMES: frozenset[str] = frozenset(
    {"流年事件", "职业财运", "综合", "学历", "家庭出身", "子女", "田宅", "性格外貌"}
)


def theme_prefers_ziwei(question: str) -> bool:
    theme = infer_question_theme(question)
    if theme in ZIWEI_PREFERRED_THEMES:
        return True
    if theme in BAZI_PREFERRED_THEMES:
        return False
    return False


is_ziwei_suitable = theme_prefers_ziwei


def merge_bazi_ziwei_letters(
    bazi_letter: str,
    ziwei_letter: str,
    question: str,
    *,
    bazi_confidence: str = "",
    ziwei_confidence: str = "",
) -> tuple[str, PreferredBaziZiwei]:
    """
    Plan A: same letter -> use it; else route by question theme.
    Returns (merged_letter, preferred_channel).
    """
    b = (bazi_letter or "").strip().upper()
    z = (ziwei_letter or "").strip().upper()
    if b and z and b == z:
        return b, "agree"
    if is_ziwei_suitable(question) and b and z and b != z:
        z_band = (ziwei_confidence or "").strip().lower()
        b_band = (bazi_confidence or "").strip().lower()
        if z_band in {"strong", "medium"} and z:
            if z_band == "strong" or b_band != "strong":
                return z, "ziwei"
        if b_band == "strong" and z_band == "weak" and b:
            return b, "bazi"
    if theme_prefers_ziwei(question):
        letter = z or b
        return letter, "ziwei"
    letter = b or z
    return letter, "bazi"


def merge_bazi_ziwei_stances(
    bazi_stance: str,
    ziwei_stance: str,
    question: str,
) -> PreferredBaziZiwei:
    """Route by stance agreement or question theme for interpret fusion."""
    bs = (bazi_stance or "").strip()
    zs = (ziwei_stance or "").strip()
    if bs and zs and bs == zs and bs not in ("未定",):
        return "agree"
    if theme_prefers_ziwei(question):
        return "ziwei"
    return "bazi"
