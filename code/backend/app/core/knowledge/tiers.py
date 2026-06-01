from __future__ import annotations

from app.core.knowledge.models import KnowledgeClaim, KnowledgeHit, SourceTier

LOOKUP_TIERS: frozenset[str] = frozenset({"T1", "T2"})
INTERPRET_TIERS: frozenset[str] = frozenset({"T1", "T2"})


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
