from __future__ import annotations

import re
from typing import Any

from app.benchmark.contest8_dataset import ContestQuestion
from app.benchmark.contest8_rag import infer_question_theme
from app.benchmark.error_labels import ERROR_LABELS
from app.core.knowledge.keys_liunian import resolve_event_liunian_categories
from app.core.knowledge.year_infer import infer_target_year


def infer_reasoning_tags(question: str) -> list[str]:
    text = question or ""
    tags: list[str] = []
    mapping = {
        "格局": "geju",
        "用神": "yongshen",
        "调候": "tiaohou",
        "大运": "dayun",
        "流年": "liunian",
        "十神": "shishen",
        "婚姻": "marriage",
        "事业": "career",
        "健康": "health",
        "财运": "wealth",
    }
    for key, value in mapping.items():
        if key in text:
            tags.append(value)
    return tags or ["general"]


def infer_must_check_rules(question: str) -> list[str]:
    tags = infer_reasoning_tags(question)
    rules: list[str] = []
    if "geju" in tags:
        rules.append("geju:month")
    if "tiaohou" in tags:
        rules.append("tiaohou")
    if "dayun" in tags or "liunian" in tags:
        rules.append("suiyun")
    if "shishen" in tags:
        rules.append("shishen")
    if "yongshen" in tags or "general" in tags:
        rules.append("qishi")
    return rules


def enrich_question(item: ContestQuestion) -> dict[str, Any]:
    question = item.question
    return {
        "targetYear": infer_target_year(question),
        "questionTheme": infer_question_theme(question),
        "expectedEventLiunian": resolve_event_liunian_categories(question),
        "expectedReasoningTags": infer_reasoning_tags(question),
        "mustCheckRules": infer_must_check_rules(question),
        "forbiddenEvidenceTypes": ["case_reference", "low_trust"],
        "errorLabels": list(ERROR_LABELS),
    }


def check_judgement_coverage(
    judgement: dict[str, Any] | None,
    meta: dict[str, Any],
) -> dict[str, Any]:
    if not judgement:
        return {"covered": False, "missingRules": meta.get("mustCheckRules", [])}
    opinions = {
        str(row.get("role", ""))
        for row in (judgement.get("arbitration") or {}).get("judgeOpinions") or []
    }
    tag_to_role = {
        "geju": "geju",
        "tiaohou": "tiaohou",
        "dayun": "suiyun",
        "liunian": "suiyun",
        "shishen": "shishen",
        "yongshen": "qishi",
        "qishi": "qishi",
    }
    missing: list[str] = []
    for tag in meta.get("expectedReasoningTags") or []:
        role = tag_to_role.get(tag)
        if role and role not in opinions:
            missing.append(tag)

    suiyun_rule_ids: list[str] = []
    for row in (judgement.get("arbitration") or {}).get("judgeOpinions") or []:
        if str(row.get("role", "")) == "suiyun":
            suiyun_rule_ids = list(row.get("ruleIds") or [])
            break
    missing_events: list[str] = []
    for category in meta.get("expectedEventLiunian") or []:
        if f"liunian:{category}" not in suiyun_rule_ids:
            missing_events.append(category)

    tiered = judgement.get("tieredEvidence") or {}
    case_refs = tiered.get("caseReference") or []
    primary = tiered.get("primaryEvidence") or []
    forbidden_used = (
        bool(case_refs)
        and not primary
        and "case_reference" in (meta.get("forbiddenEvidenceTypes") or [])
    )
    return {
        "covered": not missing and not missing_events,
        "missingTags": missing,
        "missingEventLiunian": missing_events,
        "eventLiunianCovered": not missing_events,
        "caseOverreach": forbidden_used,
        "primaryEvidenceCount": len(primary),
        "caseReferenceCount": len(case_refs),
    }
