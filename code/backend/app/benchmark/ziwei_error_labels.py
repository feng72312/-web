from __future__ import annotations

from typing import Any

from app.core.fusion.merge_bazi_ziwei import is_ziwei_suitable

ZIWEI_ERROR_LABELS = (
    "empty_prediction",
    "wrong_topic_class",
    "wrong_chart_rule",
    "ignore_body_palace",
    "single_star_overfit",
    "ignore_triad",
    "ignore_opposite",
    "wrong_mutagen_direction",
    "wrong_limit_scope",
    "school_mixing",
    "case_overfit",
    "overconfident_claim",
)


def infer_ziwei_error_labels(
    *,
    gold: str,
    predicted: str,
    judgement: dict[str, Any] | None = None,
    raw_response: str = "",
    question: str = "",
) -> list[str]:
    labels: list[str] = []
    if not predicted:
        labels.append("empty_prediction")
        return labels
    if gold == predicted:
        return labels

    body = raw_response or ""
    if not judgement:
        if "命宫" in body and is_ziwei_suitable(question):
            labels.append("single_star_overfit")
        return list(dict.fromkeys(labels))

    topic = judgement.get("topic") or {}
    arbitration = judgement.get("arbitration") or {}
    tiered = judgement.get("tieredEvidence") or {}
    judges = {row.get("role"): row for row in judgement.get("judges") or []}

    if float(topic.get("confidence") or 0) < 0.45:
        labels.append("wrong_topic_class")

    rules_meta = judgement.get("rulesMeta") or {}
    if rules_meta.get("warnings"):
        labels.append("wrong_chart_rule")

    palace = judges.get("palace") or {}
    palace_flags = palace.get("flags") or {}
    if palace_flags.get("bodyPalaceRisk") and arbitration.get("confidenceBand") == "strong":
        labels.append("ignore_body_palace")

    star = judges.get("star") or {}
    if star.get("stance") == "favorable" and palace.get("stance") == "unfavorable":
        labels.append("single_star_overfit")

    if palace_flags.get("triadWeak") and arbitration.get("confidenceBand") == "strong":
        labels.append("ignore_triad")
    if palace_flags.get("oppositeBorrowed") and "借" not in body:
        labels.append("ignore_opposite")

    mutagen = judges.get("mutagen") or {}
    mut_flags = mutagen.get("flags") or {}
    if mutagen.get("stance") == "unfavorable" or mut_flags.get("jiHits"):
        if arbitration.get("confidenceBand") == "strong" and mutagen.get("stance") != "unfavorable":
            labels.append("wrong_mutagen_direction")

    limit_judge = judges.get("limit") or {}
    limit_flags = limit_judge.get("flags") or {}
    events = limit_flags.get("eventChain") or []
    if events and limit_judge.get("stance") == "mixed":
        labels.append("wrong_limit_scope")

    cross = judges.get("cross_school") or {}
    cross_flags = cross.get("flags") or {}
    if cross_flags.get("schoolConflict") and arbitration.get("confidenceBand") == "strong":
        labels.append("school_mixing")

    primary_count = len(tiered.get("primaryEvidence") or [])
    case_count = len(tiered.get("caseReference") or [])
    summary = judgement.get("tieredEvidenceSummary") or {}
    if summary.get("caseOverreachRisk"):
        labels.append("case_overfit")
    elif case_count > 0 and primary_count == 0:
        labels.append("case_overfit")

    if arbitration.get("confidenceBand") == "strong":
        labels.append("overconfident_claim")

    return list(dict.fromkeys(labels))


def aggregate_ziwei_error_label_counts(results: list[dict[str, Any]]) -> dict[str, int]:
    counter: dict[str, int] = {}
    for row in results:
        for label in row.get("errorLabels") or []:
            counter[label] = counter.get(label, 0) + 1
    return dict(sorted(counter.items(), key=lambda item: (-item[1], item[0])))
