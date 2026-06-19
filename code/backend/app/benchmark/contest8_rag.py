from __future__ import annotations

import re
from typing import Any

# 题干同时含「毕业/大学」与职业取向词时, 优先判职业 (如「毕业后从事什么行业」).
_CAREER_THEME_OVERRIDE_KEYS: tuple[str, ...] = ("行业", "从事", "科系", "现职")
# 孩子仅为背景、主问财运/买房时, 优先判职业财运.
_WEALTH_CHILD_CONTEXT_KEYS: tuple[str, ...] = ("赚到大钱", "赚大钱", "忽然赚", "骤然赚")
_WEALTH_CHILD_EVENT_KEYS: tuple[str, ...] = ("买房", "通勤", "读书问题")

THEME_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("婚姻感情", ("婚姻", "结婚", "感情", "配偶", "离婚", "再婚", "桃花", "同居", "外遇", "同性恋")),
    ("子女", ("子女", "孩子", "生子", "流产", "麟儿", "育有")),
    ("职业财运", ("职业", "工作", "事业", "财运", "收入", "创业", "生意", "老板", "打工", "身家", "年薪", "投资")),
    ("学历", ("学历", "读书", "毕业", "大学", "中学", "专科", "博士")),
    ("健康疾病", ("健康", "疾病", "病", "手术", "住院", "癌", "骨折", "意外", "车祸")),
    ("官非", ("官非", "刑事", "牢狱", "警察", "扣留")),
    ("田宅", ("房产", "田宅", "搬迁", "买房", "公屋")),
    ("性格外貌", ("性格", "外貌", "身材", "脾气", "个性")),
    ("家庭出身", ("家境", "出身", "父母", "家庭背景", "父亲", "母亲")),
    ("流年事件", ("年发生", "大运", "大限", "虚龄", "运程")),
]


def infer_question_theme(question: str) -> str:
    text = question.strip()
    if any(k in text for k in _CAREER_THEME_OVERRIDE_KEYS):
        return "职业财运"
    if any(k in text for k in _WEALTH_CHILD_CONTEXT_KEYS) and any(
        k in text for k in _WEALTH_CHILD_EVENT_KEYS
    ):
        return "职业财运"
    for theme, keywords in THEME_RULES:
        for kw in keywords:
            if kw in text:
                return theme
    return "综合"


def build_case_rag_query(chart: dict[str, Any], question: str) -> str:
    """Retrieve similar 命例讲解 from RAG (实战命例, 滴天髓命例, etc.)."""
    dm = chart.get("dayMaster", "")
    pillars = chart.get("pillars") or {}
    month_pillar = pillars.get("month", {}).get("ganzhi", "")
    day_pillar = pillars.get("day", {}).get("ganzhi", "")
    theme = infer_question_theme(question)
    stem = re.sub(r"\s+", " ", question)[:120]
    extra = ""
    if theme == "流年事件":
        years = re.findall(r"(19|20)\d{2}", question)
        if years:
            extra = f" 流年{''.join(years[:3])}年 太岁 应期 事件"
        else:
            extra = " 流年 太岁 应期 哪一年"
    elif theme == "婚姻感情":
        extra = " 配偶星 合冲 离婚 结婚 流年"
    elif theme == "健康疾病":
        extra = " 疾厄 手术 住院 流年 冲克"
    elif theme == "官非":
        extra = " 官非 七杀 牢狱 流年"
    elif theme == "学历":
        extra = " 印星 财坏印 学业中断 学历层次 肄业 辍学 早运大运"
    elif theme == "家庭出身":
        extra = " 父母星 偏财为父 正印为母 年柱 月柱 家境 父母寿元"
    else:
        extra = ""
    return (
        f"八字实战命例讲解 {theme} "
        f"日主{dm} 日柱{day_pillar} 月柱{month_pillar} "
        f"开口直断 应期 大运流年{extra} "
        f"{stem}"
    )
