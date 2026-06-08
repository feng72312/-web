from __future__ import annotations

import re


RELATIONSHIP_KEYWORDS = ("关系", "感情", "爱情", "复合", "和好", "他", "她", "男友", "女友", "婚姻", "恋爱")
CHOICE_KEYWORDS = ("选择", "二选一", "选哪", "还是", "要不要", "该不该", "A还是B")
YEAR_KEYWORDS = ("今年", "一年", "年运", "未来一年", "12个月", "十二个月")
DEEP_KEYWORDS = ("整体", "详细", "深度", "全面", "重大", "人生")
SHORT_MAX = 8


def suggest_spread(question: str) -> dict[str, str]:
    text = question.strip()
    if not text:
        return {"spreadId": "three-card", "reason": "默认使用三牌阵, 兼顾过去现在未来."}

    if any(k in text for k in RELATIONSHIP_KEYWORDS):
        return {"spreadId": "relationship", "reason": "检测到关系/感情类问事, 推荐关系牌阵."}

    if any(k in text for k in CHOICE_KEYWORDS):
        return {"spreadId": "two-choice", "reason": "检测到抉择类问事, 推荐二选一牌阵."}

    if any(k in text for k in YEAR_KEYWORDS):
        return {"spreadId": "year-ahead", "reason": "检测到年运类问事, 推荐年运十二牌阵."}

    if len(text) <= SHORT_MAX:
        return {"spreadId": "single", "reason": "问题较短, 单牌可快速给出神谕指引."}

    if any(k in text for k in DEEP_KEYWORDS):
        return {"spreadId": "celtic-cross", "reason": "问题较复杂, 推荐凯尔特十字深度牌阵."}

    if re.search(r"(怎么|如何|怎样)", text):
        return {
            "spreadId": "situation-action-outcome",
            "reason": "检测到行动建议类问事, 推荐情境-行动-结果牌阵.",
        }

    return {"spreadId": "three-card", "reason": "通用问事, 推荐经典三牌阵 (过去/现在/未来)."}
