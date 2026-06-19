from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


TOPIC_RULES: list[dict[str, Any]] = [
    {
        "topicId": "marriage",
        "topicLabel": "婚恋感情",
        "palaces": ["夫妻", "福德", "迁移"],
        "keywords": ["婚", "恋", "感情", "配偶", "对象", "桃花", "结婚", "离婚"],
        "ruleId": "topic:marriage",
    },
    {
        "topicId": "career",
        "topicLabel": "事业官禄",
        "palaces": ["官禄", "命宫", "财帛", "迁移"],
        "keywords": ["事业", "工作", "官", "升职", "创业", "职场", "就业"],
        "ruleId": "topic:career",
    },
    {
        "topicId": "wealth",
        "topicLabel": "财运资财",
        "palaces": ["财帛", "田宅", "福德"],
        "keywords": ["财", "钱", "投资", "收入", "生意", "资产", "理财"],
        "ruleId": "topic:wealth",
    },
    {
        "topicId": "health",
        "topicLabel": "健康疾厄",
        "palaces": ["疾厄", "福德", "命宫"],
        "keywords": ["健康", "病", "疾", "身体", "手术", "康复"],
        "ruleId": "topic:health",
    },
    {
        "topicId": "family",
        "topicLabel": "家庭亲子",
        "palaces": ["子女", "父母", "田宅"],
        "keywords": ["子女", "孩子", "父母", "家庭", "怀孕", "生育"],
        "ruleId": "topic:family",
    },
    {
        "topicId": "general",
        "topicLabel": "综合命格",
        "palaces": ["命宫", "财帛", "官禄", "迁移"],
        "keywords": [],
        "ruleId": "topic:general",
    },
]


@dataclass
class TopicResult:
    topic_id: str
    topic_label: str
    target_palaces: list[str] = field(default_factory=list)
    confidence: float = 0.5
    matched_keywords: list[str] = field(default_factory=list)
    rule_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "topicId": self.topic_id,
            "topicLabel": self.topic_label,
            "targetPalaces": self.target_palaces,
            "confidence": round(self.confidence, 2),
            "matchedKeywords": self.matched_keywords,
            "ruleId": self.rule_id,
        }


def classify_topic(question: str) -> TopicResult:
    text = (question or "").strip()
    tokens = re.findall(r"[\u4e00-\u9fff]{2,}", text)
    best: TopicResult | None = None
    for rule in TOPIC_RULES:
        if rule["topicId"] == "general":
            continue
        matched = [kw for kw in rule["keywords"] if kw in text or any(kw in token for token in tokens)]
        if not matched:
            continue
        confidence = min(0.95, 0.55 + 0.08 * len(matched))
        candidate = TopicResult(
            topic_id=rule["topicId"],
            topic_label=rule["topicLabel"],
            target_palaces=list(rule["palaces"]),
            confidence=confidence,
            matched_keywords=matched,
            rule_id=rule["ruleId"],
        )
        if best is None or candidate.confidence > best.confidence:
            best = candidate
    if best:
        return best
    fallback = TOPIC_RULES[-1]
    return TopicResult(
        topic_id=fallback["topicId"],
        topic_label=fallback["topicLabel"],
        target_palaces=list(fallback["palaces"]),
        confidence=0.45,
        rule_id=fallback["ruleId"],
    )
