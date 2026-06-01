from __future__ import annotations

import re

DAYUN_TOPIC = "dayun"

DAYUN_BASE_CATEGORIES = (
    "core",
    "xingyun_xiji",
    "gan_zhi_weight",
)


def select_dayun_categories(question: str = "") -> list[str]:
    text = (question or "").strip()
    cats = list(DAYUN_BASE_CATEGORIES)
    if re.search(r"起运|顺逆|童限|小运", text):
        cats.append("start_rule")
    if re.search(r"并临|岁运", text):
        cats.append("suiyun_note")
    if re.search(r"大运|大限|运程|虚龄", text):
        cats.append("dayun_change")
    seen: set[str] = set()
    ordered: list[str] = []
    for c in cats:
        if c not in seen:
            seen.add(c)
            ordered.append(c)
    return ordered


def build_dayun_lookup_keys(question: str = "") -> list[dict[str, str]]:
    return [{"category": c} for c in select_dayun_categories(question)]
