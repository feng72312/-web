from __future__ import annotations

from typing import Any

ERROR_LABELS = (
    "ignore_month_command",
    "wrong_tiaohou",
    "wrong_geju",
    "wrong_strength",
    "wrong_yongshen",
    "wrong_dayun",
    "wrong_liunian",
    "case_overfit",
    "low_authority_override",
    "overconfident_claim",
)


def infer_error_labels(
    *,
    gold: str,
    predicted: str,
    judgement: dict[str, Any] | None = None,
    raw_response: str = "",
) -> list[str]:
    labels: list[str] = []
    if gold == predicted:
        return labels

    body = (raw_response or "").lower()
    if judgement:
        arb = judgement.get("arbitration") or {}
        tiered = judgement.get("tieredEvidence") or {}
        coverage = judgement.get("coverage") or {}
        case_count = len(tiered.get("caseReference") or [])
        primary_count = len(tiered.get("primaryEvidence") or [])
        if coverage.get("caseOverreach"):
            labels.append("case_overfit")
        elif case_count > 0 and primary_count == 0:
            labels.append("case_overfit")
        elif case_count > primary_count:
            labels.append("case_overfit")
        if tiered.get("excludedOrLowTrust") and not tiered.get("primaryEvidence"):
            labels.append("low_authority_override")
        if arb.get("confidenceBand") == "strong" and gold != predicted:
            labels.append("overconfident_claim")
        steps = {s.get("id"): s for s in judgement.get("steps") or []}
        month_step = steps.get("month") or {}
        if month_step.get("status") == "skipped":
            labels.append("ignore_month_command")
        if (steps.get("tiaohou") or {}).get("status") == "partial":
            labels.append("wrong_tiaohou")
        if (steps.get("geju") or {}).get("status") == "partial":
            labels.append("wrong_geju")
        if (steps.get("qishi") or {}).get("status") == "partial":
            labels.append("wrong_strength")
        if (steps.get("suiyun") or {}).get("status") == "partial":
            labels.append("wrong_dayun")

    if "流年" in body and gold != predicted:
        labels.append("wrong_liunian")
    if "用神" in body and gold != predicted and "wrong_yongshen" not in labels:
        labels.append("wrong_yongshen")

    return list(dict.fromkeys(labels))
