from __future__ import annotations

from app.core.knowledge.models import KnowledgeHit


def knowledge_hits_to_evidence(
    hits: list[KnowledgeHit] | list[dict],
    *,
    limit: int = 5,
    claims_per_hit: int = 3,
) -> list[dict]:
    """Serialize knowledge hits for API / frontend evidence panels."""
    evidence: list[dict] = []
    for raw in hits[:limit]:
        if isinstance(raw, KnowledgeHit):
            hit = raw
        else:
            hit = KnowledgeHit.model_validate(raw)

        claims = []
        for claim in hit.claims[:claims_per_hit]:
            claims.append(
                {
                    "classic": claim.classic,
                    "chapter": claim.chapter,
                    "quote": claim.quote,
                    "conclusion": claim.conclusion,
                    "role": claim.role,
                    "sourceFile": claim.sourceFile,
                    "sourceCategory": claim.sourceCategory,
                }
            )

        evidence.append(
            {
                "id": hit.id,
                "topic": hit.topic,
                "summary": hit.summary,
                "agreementLevel": hit.agreementLevel,
                "sourceTier": hit.sourceTier,
                "domain": hit.domain,
                "claims": claims,
            }
        )
    return evidence
