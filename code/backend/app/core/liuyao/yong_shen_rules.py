from __future__ import annotations

import json
import re
from typing import Any

from app.core.liuyao.models import YongShenResult

KEYWORD_RULES: list[tuple[tuple[str, ...], str]] = [
    (("考试", "学习", "文书", "证书", "学校", "录取"), "父母"),
    (("财", "钱", "投资", "生意", "借贷", "工资", "收入"), "妻财"),
    (("官", "工作", "升职", "事业", "职位", "领导"), "官鬼"),
    (("婚", "恋", "嫁", "娶", "感情", "对象"), "妻财"),
    (("病", "医", "身体", "疾", "健康"), "官鬼"),
    (("子", "孕", "产", "生育", "后代"), "子孙"),
    (("兄弟", "竞争", "同辈", "合伙"), "兄弟"),
]


def find_yong_shen_position(chart: dict[str, Any], liuqin: str) -> int:
    for line in chart.get("lines", []):
        if line.get("liuqin") == liuqin:
            return int(line["position"])
    shi = chart.get("shiYing", {}).get("shi", 1)
    return int(shi)


def fallback_yong_shen(chart: dict[str, Any], question: str) -> YongShenResult:
    matched = "兄弟"
    reason = "未匹配到明确关键词, 默认以兄弟爻为用神"
    for keywords, liuqin in KEYWORD_RULES:
        if any(word in question for word in keywords):
            matched = liuqin
            reason = f"问事含相关语义, 取{liuqin}爻为用神"
            break
    position = find_yong_shen_position(chart, matched)
    return YongShenResult(
        yong_shen=matched,
        position=position,
        reason=reason,
        source="fallback",
    )


def parse_yong_shen_json(text: str) -> dict[str, Any] | None:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
