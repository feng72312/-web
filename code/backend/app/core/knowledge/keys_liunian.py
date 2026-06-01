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
    theme = infer_question_theme(text)
    theme_event = {
        "官非": "event_guanfei",
        "健康疾病": "event_health",
        "婚姻感情": "event_marriage",
        "职业财运": "event_wealth",
        "流年事件": "event_career",
        "家庭出身": "event_family",
        "子女": "event_career",
    }
    if theme in theme_event:
        cats.append(theme_event[theme])
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
