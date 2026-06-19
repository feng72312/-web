from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TopicResult:
    topic_id: str
    topic_label: str
    candidate_yong_shen: str
    alternate_yong_shen: list[str] = field(default_factory=list)
    special_rules: list[str] = field(default_factory=list)
    confidence: float = 0.5
    matched_keywords: list[str] = field(default_factory=list)
    rule_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "topicId": self.topic_id,
            "topicLabel": self.topic_label,
            "candidateYongShen": self.candidate_yong_shen,
            "alternateYongShen": self.alternate_yong_shen,
            "specialRules": self.special_rules,
            "confidence": round(self.confidence, 2),
            "matchedKeywords": self.matched_keywords,
            "ruleId": self.rule_id,
        }
