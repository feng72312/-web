from __future__ import annotations

from typing import Any

LIUYAO_ERROR_LABELS = (
    "wrong_topic_class",
    "wrong_yong_shen",
    "ignore_yue_jian",
    "ignore_kong_po",
    "wrong_dong_bian",
    "case_overfit",
    "modern_notes_override",
    "overconfident_claim",
    "empty_prediction",
)


def infer_liuyao_error_labels(
    *,
    gold: str,
    predicted: str,
    judgement: dict[str, Any] | None = None,
    raw_response: str = "",
) -> list[str]:
    labels: list[str] = []
    if not predicted:
        labels.append("empty_prediction")
        return labels
    if gold == predicted:
        return labels

    body = raw_response or ""
    if not judgement:
        if "用神" in body:
            labels.append("wrong_yong_shen")
        return list(dict.fromkeys(labels))

    topic = judgement.get("topic") or {}
    yong_shen = judgement.get("yongShen") or {}
    arbitration = judgement.get("arbitration") or {}
    tiered = judgement.get("tieredEvidence") or {}
    judges = {row.get("role"): row for row in judgement.get("judges") or []}

    if float(topic.get("confidence") or 0) < 0.45:
        labels.append("wrong_topic_class")

    if yong_shen.get("source") == "ai":
        labels.append("wrong_yong_shen")
    elif float(yong_shen.get("confidence") or 0) < 0.45:
        labels.append("wrong_yong_shen")

    wang = judges.get("wang_shuai") or {}
    flags = wang.get("flags") or {}
    if flags.get("yuePo") or flags.get("xunKong"):
        if arbitration.get("confidenceBand") == "strong":
            labels.append("ignore_kong_po")
    if wang.get("stance") == "unfavorable" and arbitration.get("confidenceBand") == "strong":
        labels.append("ignore_yue_jian")

    dong = judges.get("dong_bian") or {}
    if dong.get("boundary") and dong.get("stance") in {"mixed", "unfavorable"}:
        labels.append("wrong_dong_bian")

    primary_count = len(tiered.get("primaryEvidence") or [])
    case_count = len(tiered.get("caseReference") or [])
    modern_count = len(tiered.get("modernSupport") or [])
    summary = judgement.get("tieredEvidenceSummary") or {}

    if summary.get("caseOverreachRisk"):
        labels.append("case_overfit")
    elif case_count > 0 and primary_count == 0:
        labels.append("case_overfit")
    if modern_count > 0 and primary_count == 0:
        labels.append("modern_notes_override")

    if arbitration.get("confidenceBand") == "strong":
        labels.append("overconfident_claim")

    return list(dict.fromkeys(labels))


def aggregate_error_label_counts(results: list[dict[str, Any]]) -> dict[str, int]:
    counter: dict[str, int] = {}
    for row in results:
        for label in row.get("errorLabels") or []:
            counter[label] = counter.get(label, 0) + 1
    return dict(sorted(counter.items(), key=lambda item: (-item[1], item[0])))
