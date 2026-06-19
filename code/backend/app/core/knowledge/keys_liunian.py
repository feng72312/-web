from __future__ import annotations

import re

from app.benchmark.contest8_rag import infer_question_theme

LIUNIAN_TOPIC = "liunian"

# Always inject these rule bundles when liunian topic is requested.
LIUNIAN_BASE_CATEGORIES = (
    "core",
    "taisui_relation",
    "dayun_synergy",
    "push_method",
)

THEME_EVENT_CATEGORIES: dict[str, tuple[str, ...]] = {
    "官非": ("event_guanfei",),
    "健康疾病": ("event_health",),
    "婚姻感情": ("event_marriage",),
    "家庭出身": ("event_family",),
    "子女": ("event_career",),
    "流年事件": ("event_career",),
}

SANMING_LIUNIAN_TRIGGERS: tuple[tuple[str, str], ...] = (
    (r"真太岁|转趾|日柱同|本命年|日年相并", "sanming_zhen_taisui"),
    (r"并临|岁运并", "sanming_suiyun_binglin"),
    (r"太岁当头|征太岁", "sanming_taisui_head"),
    (r"伏吟", "sanming_fuyin"),
    (r"反吟|返吟", "sanming_fanyin"),
    (r"冲|战|克|刑|害|伐|征太岁|日犯岁君", "sanming_zhan_chong_he"),
    (r"小运|行年", "sanming_xiaoyun"),
)


def resolve_sanming_liunian_categories(question: str = "") -> list[str]:
    text = (question or "").strip()
    if not text:
        return []
    cats: list[str] = []
    for pattern, category in SANMING_LIUNIAN_TRIGGERS:
        if re.search(pattern, text):
            cats.append(category)
    return cats


def resolve_event_liunian_categories(question: str = "") -> list[str]:
    text = (question or "").strip()
    if not text:
        return []
    theme = infer_question_theme(text)
    if theme == "职业财运":
        cats: list[str] = []
        if re.search(r"事业|工作|创业|职位|升职|调动|单位", text):
            cats.append("event_career")
        if re.search(r"财|收入|生意|破财|进财|财运", text):
            cats.append("event_wealth")
        return cats or ["event_career", "event_wealth"]
    rows = THEME_EVENT_CATEGORIES.get(theme)
    return list(rows) if rows else []


def select_liunian_categories(question: str = "") -> list[str]:
    text = (question or "").strip()
    cats = list(LIUNIAN_BASE_CATEGORIES)
    if re.search(r"并临|岁运", text):
        cats.append("suiyun_binglin")
    if re.search(r"冲|战|克|刑|害|伏|伐", text):
        cats.append("zhan_chong_he")
    if re.search(r"真太岁|转趾|日柱|本命", text):
        cats.append("zhen_taisui")
    if re.search(r"用神|喜忌|救|有情", text):
        cats.append("yongshen_timing")
    if re.search(r"小运|小限|命宫|宫限", text):
        cats.append("xiaoyun_note")
    cats.extend(resolve_sanming_liunian_categories(text))
    cats.extend(resolve_event_liunian_categories(text))
    # de-dupe preserve order
    seen: set[str] = set()
    ordered: list[str] = []
    for c in cats:
        if c not in seen:
            seen.add(c)
            ordered.append(c)
    return ordered


def build_liunian_lookup_keys(question: str = "") -> list[dict[str, str]]:
    return [{"category": c} for c in select_liunian_categories(question)]
