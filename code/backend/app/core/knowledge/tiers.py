from __future__ import annotations

from app.core.knowledge.models import KnowledgeClaim, KnowledgeHit, SourceTier

LOOKUP_TIERS: frozenset[str] = frozenset({"T1", "T2"})
INTERPRET_TIERS: frozenset[str] = frozenset({"T1", "T2"})

AUTHORITY_TIERS_JUDGE: frozenset[str] = frozenset({"S", "A"})
AUTHORITY_TIERS_LOOKUP: frozenset[str] = frozenset({"S", "A", "B"})

LEGACY_TO_AUTHORITY = {"T1": "S", "T2": "A", "T3": "C", "T4": "D"}


def authority_tier_for_node(node: dict) -> str:
    if node.get("authorityTier"):
        return str(node["authorityTier"])
    legacy = str(node.get("sourceTier") or "T4")
    return LEGACY_TO_AUTHORITY.get(legacy, "D")


def hit_to_public(node: dict) -> KnowledgeHit:
    claims = [
        KnowledgeClaim.model_validate(item)
        for item in (node.get("claims") or [])
    ]
    return KnowledgeHit(
        id=node["id"],
        topic=node["topic"],
        lookupKey=node.get("lookupKey") or {},
        summary=node.get("summary") or "",
        claims=claims,
        agreementLevel=node.get("agreementLevel") or "single_source",
        safeAutoAnswer=bool(node.get("safeAutoAnswer")),
        sourceTier=node.get("sourceTier") or "T1",
        domain=node.get("domain") or "bazi",
    )


def allow_safe_auto_answer(node: dict) -> bool:
    if not node.get("safeAutoAnswer"):
        return False
    if not node.get("reviewedAt"):
        return False
    tier: SourceTier = node.get("sourceTier") or "T4"
    if tier not in LOOKUP_TIERS:
        return False
    if node.get("topic") == "case":
        return False
    if node.get("domain") == "bazi-adjacent":
        return False
    claims = node.get("claims") or []
    roles = [item.get("role") for item in claims]
    if "contradiction" in roles:
        return False
    if node.get("agreementLevel") == "disputed":
        return False
    if not any(item.get("role") == "primary" for item in claims):
        return False
    return True
