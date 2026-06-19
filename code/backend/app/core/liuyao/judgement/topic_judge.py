from __future__ import annotations

from app.core.liuyao.judgement.models import TopicResult
from app.core.liuyao.judgement.topic_rules import TOPIC_RULES, TopicRule


class TopicJudge:
    def classify(self, question: str) -> TopicResult:
        return classify_topic(question)


def classify_topic(question: str) -> TopicResult:
    text = (question or "").strip()
    if not text:
        return TopicResult(
            topic_id="general",
            topic_label="一般问事",
            candidate_yong_shen="兄弟",
            confidence=0.3,
            special_rules=["问事为空, 低置信度默认"],
            rule_id="topic:general",
        )

    best: TopicRule | None = None
    best_hits: list[str] = []
    best_score = 0

    for rule in TOPIC_RULES:
        hits = [kw for kw in rule.keywords if kw in text]
        if not hits:
            continue
        score = len(hits) * 10 + rule.priority
        if score > best_score:
            best = rule
            best_hits = hits
            best_score = score

    if best is None:
        return TopicResult(
            topic_id="general",
            topic_label="一般问事",
            candidate_yong_shen="兄弟",
            confidence=0.35,
            special_rules=["未匹配专题关键词, 参考一般断法"],
            rule_id="topic:general",
        )

    confidence = min(0.95, 0.45 + 0.12 * len(best_hits))
    if best.topic_id == "friend":
        confidence = min(confidence, 0.55)

    return TopicResult(
        topic_id=best.topic_id,
        topic_label=best.topic_label,
        candidate_yong_shen=best.candidate_yong_shen,
        alternate_yong_shen=list(best.alternate_yong_shen),
        special_rules=list(best.special_rules),
        confidence=confidence,
        matched_keywords=best_hits,
        rule_id=best.rule_id or f"topic:{best.topic_id}",
    )
