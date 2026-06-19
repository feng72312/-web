from __future__ import annotations

from typing import Any

from app.core.liuyao.judgement.judgement_models import (
    EvidenceChainItem,
    EvidenceRequest,
    LiuyaoJudgeVerdict,
    TieredEvidence,
)

BUCKET_FIELD_MAP = {
    "primaryEvidence": "primaryEvidence",
    "secondaryEvidence": "secondaryEvidence",
    "caseReference": "caseReference",
    "modernSupport": "modernSupport",
    "excludedOrLowTrust": "excludedOrLowTrust",
}


def _normalize_hit(hit: dict[str, Any]) -> dict[str, Any]:
    source = str(hit.get("source") or "")
    excerpt = str(hit.get("excerpt") or "")
    return {"source": source, "excerpt": excerpt, **hit}


def _bucket_hit(hit: dict[str, Any]) -> str:
    bucket = str(hit.get("evidenceBucket") or "")
    if bucket in BUCKET_FIELD_MAP:
        return bucket

    if hit.get("caseOnly") or hit.get("case_only"):
        return "caseReference"

    tier = str(hit.get("authorityTier") or hit.get("authority_tier") or "").upper()
    role = str(hit.get("evidenceRole") or hit.get("evidence_role") or "")
    policy = str(hit.get("judgmentPolicy") or "")

    if tier == "B" or policy == "explain_only" or "B_现代" in str(hit.get("source") or ""):
        return "modernSupport"
    if role in {"core_divination_judge", "classic_topic_judge"} and tier in {"S", "A"}:
        return "primaryEvidence"
    if tier in {"S", "A"}:
        return "secondaryEvidence"
    if role in {"low_trust", "supplement_only"}:
        return "excludedOrLowTrust"
    return "secondaryEvidence"


def partition_rag_hits(hits: list[dict[str, Any]]) -> TieredEvidence:
    tiered = TieredEvidence()
    for hit in hits:
        row = _normalize_hit(hit)
        bucket = _bucket_hit(row)
        target = getattr(tiered, bucket, None)
        if isinstance(target, list):
            target.append(row)
    return tiered


def build_evidence_chain(
    verdicts: list[LiuyaoJudgeVerdict],
    rag_hits: list[dict[str, Any]],
) -> list[EvidenceChainItem]:
    items: list[EvidenceChainItem] = []
    for verdict in verdicts:
        if verdict.conclusionKind == "insufficient_evidence":
            continue
        quote = ""
        for hit in rag_hits[:6]:
            if verdict.classic and verdict.classic in str(hit.get("source") or ""):
                quote = str(hit.get("excerpt") or "")[:120]
                break
        items.append(
            EvidenceChainItem(
                conclusion=verdict.summary,
                ruleId=verdict.ruleIds[0] if verdict.ruleIds else "",
                primaryClassic=verdict.classic,
                quote=quote,
                boundary=verdict.boundary,
                confidence=verdict.confidenceBand,
                conclusionKind=verdict.conclusionKind,
            )
        )
    return items


def build_tiered_evidence_summary(tiered: TieredEvidence | dict[str, Any] | None) -> dict[str, Any]:
    data = tiered.model_dump() if isinstance(tiered, TieredEvidence) else (tiered or {})
    bucket_labels = {
        "primaryEvidence": "主裁典籍",
        "secondaryEvidence": "辅助古籍",
        "caseReference": "卦例参考",
        "modernSupport": "现代补充",
        "excludedOrLowTrust": "低信排除",
    }
    groups: list[dict[str, Any]] = []
    for bucket, label in bucket_labels.items():
        rows = list(data.get(bucket) or [])
        if not rows:
            continue
        groups.append(
            {
                "bucket": bucket,
                "label": label,
                "count": len(rows),
                "preview": [
                    str(row.get("source") or row.get("excerpt") or "")[:80]
                    for row in rows[:3]
                ],
            }
        )
    primary_count = len(data.get("primaryEvidence") or [])
    case_count = len(data.get("caseReference") or [])
    modern_count = len(data.get("modernSupport") or [])
    return {
        "groups": groups,
        "total": sum(group["count"] for group in groups),
        "caseOverreachRisk": bool(case_count) and primary_count == 0,
        "note": (
            "卦例仅作参考, 不得单独推翻主裁结论"
            if case_count and primary_count
            else "主裁典籍证据已就位"
            if primary_count
            else "现代补充仅作 explain_only"
            if modern_count and not primary_count
            else "暂无分层证据"
        ),
    }


class LiuyaoEvidenceRetriever:
    def __init__(self, rag_provider: Any | None) -> None:
        self._rag = rag_provider

    async def fetch_for_requests(
        self,
        requests: list[EvidenceRequest],
        *,
        category: str,
    ) -> TieredEvidence:
        if self._rag is None:
            return TieredEvidence()
        merged: list[dict[str, Any]] = []
        seen: set[str] = set()
        for req in requests[:6]:
            query = (req.query or "").strip()
            if not query:
                continue
            try:
                hits = await self._rag.search(
                    query,
                    top_k=4,
                    category=category,
                    authority_tiers=req.authorityTiers or None,
                    evidence_roles=req.evidenceRoles or None,
                    library_roles=req.libraryRoles or None,
                    classic_whitelist=req.classicWhitelist or None,
                    topic_scope=[req.topic] if req.topic else None,
                    judge_only=req.judgeOnly,
                )
            except Exception:
                continue
            for hit in hits or []:
                row = _normalize_hit(hit)
                key = f"{row.get('source', '')}:{str(row.get('excerpt', ''))[:40]}"
                if key in seen:
                    continue
                seen.add(key)
                merged.append(row)
        merged.sort(key=_rank_hit, reverse=True)
        return partition_rag_hits(merged)


def _rank_hit(hit: dict[str, Any]) -> float:
    score = float(hit.get("rerankScore") or hit.get("score") or 0.0)
    tier = str(hit.get("authorityTier") or "D")
    tier_weight = {"S": 1.0, "A": 0.85, "B": 0.35, "C": 0.15, "D": 0.05}.get(tier, 0.05)
    if hit.get("caseOnly"):
        score *= 0.55
    if str(hit.get("judgmentPolicy") or "") == "explain_only":
        score *= 0.4
    return score * tier_weight
