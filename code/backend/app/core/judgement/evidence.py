from __future__ import annotations

from typing import Any

from app.core.judgement.models import EvidenceChainItem, EvidenceRequest, TieredEvidence
from app.core.knowledge.case_factory import get_case_store
from app.core.knowledge.evidence import knowledge_hits_to_evidence
from app.core.knowledge.factory import get_knowledge_service
from app.core.knowledge.models import KnowledgeHit
from app.core.rag.base import normalize_rag_excerpts


def load_case_references(chart: dict[str, Any], *, limit: int = 3) -> list[dict[str, Any]]:
    store = get_case_store()
    if not store.enabled:
        return []
    return [store.to_case_reference(row) for row in store.match_chart(chart, limit=limit)]


JUDGE_EVIDENCE_ROLES = {
    "tiaohou": "tiaohou_judge",
    "geju": "geju_judge",
    "qishi": "qishi_judge",
    "shishen": "shishen_judge",
    "suiyun": "suiyun_judge",
}


def merge_primary_evidence(
    graph_rows: list[dict[str, Any]],
    rag_rows: list[dict[str, Any]],
    *,
    limit: int = 16,
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in graph_rows + rag_rows:
        rule_id = str(row.get("ruleId") or "").strip()
        key = f"rule:{rule_id}" if rule_id else f"excerpt:{str(row.get('excerpt') or '')[:80]}"
        if key in seen:
            continue
        seen.add(key)
        merged.append(row)
        if len(merged) >= limit:
            break
    return merged


def build_graph_primary_evidence(verdicts: list, *, limit: int = 16) -> list[dict[str, Any]]:
    service = get_knowledge_service()
    if not service.enabled:
        return []
    store = service.store
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for verdict in verdicts:
        if verdict.role == "case":
            continue
        evidence_role = JUDGE_EVIDENCE_ROLES.get(verdict.role, "primary_judge")
        for rule_id in verdict.ruleIds or []:
            if rule_id in seen:
                continue
            node = store.get_by_id(rule_id)
            if not node:
                continue
            seen.add(rule_id)
            claim = (node.get("claims") or [{}])[0]
            rows.append(
                {
                    "ruleId": rule_id,
                    "classic": str(claim.get("classic") or ""),
                    "authorityTier": str(node.get("authorityTier") or node.get("sourceTier", "S")),
                    "evidenceRole": evidence_role,
                    "evidenceBucket": "primaryEvidence",
                    "libraryRole": "rule_graph",
                    "canJudge": True,
                    "excerpt": str(node.get("summary") or claim.get("conclusion") or "")[:300],
                    "source": str(node.get("sourceFile") or ""),
                }
            )
            if len(rows) >= limit:
                return rows
    return rows


def _append_rule_ref(
    refs: list[dict[str, str]],
    seen: set[str],
    *,
    rule_id: str,
    classic: str = "",
    role: str = "",
    conclusion: str = "",
) -> None:
    rid = str(rule_id).strip()
    if not rid or rid in seen:
        return
    seen.add(rid)
    refs.append(
        {
            "ruleId": rid,
            "classic": classic,
            "role": role,
            "conclusion": conclusion[:120],
        }
    )


def _iter_rule_ids(raw: str) -> list[str]:
    return [part.strip() for part in str(raw or "").split(",") if part.strip()]


def extract_rule_id_refs(judgement_report: dict[str, Any] | None) -> list[dict[str, str]]:
    if not judgement_report:
        return []
    refs: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in judgement_report.get("evidenceChain") or []:
        classic = str(item.get("primaryClassic") or "")
        conclusion = str(item.get("conclusion") or "")
        for rule_id in _iter_rule_ids(str(item.get("ruleId") or "")):
            _append_rule_ref(
                refs,
                seen,
                rule_id=rule_id,
                classic=classic,
                conclusion=conclusion,
            )
    for verdict in (judgement_report.get("arbitration") or {}).get("judgeOpinions") or []:
        role = str(verdict.get("role") or "")
        classic = str(verdict.get("classic") or "")
        conclusion = str(verdict.get("summary") or "")
        for rule_id in verdict.get("ruleIds") or []:
            _append_rule_ref(
                refs,
                seen,
                rule_id=str(rule_id),
                classic=classic,
                role=role,
                conclusion=conclusion,
            )
    return refs


def build_tiered_evidence_summary(tiered: dict[str, Any] | None) -> dict[str, Any]:
    data = tiered or {}
    bucket_labels = {
        "primaryEvidence": "主裁证据",
        "secondaryEvidence": "辅助证据",
        "caseReference": "命例参考",
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
                    str(row.get("excerpt") or row.get("ruleId") or row.get("classic") or "")[:80]
                    for row in rows[:3]
                ],
            }
        )
    primary_count = len(data.get("primaryEvidence") or [])
    case_count = len(data.get("caseReference") or [])
    return {
        "groups": groups,
        "total": sum(group["count"] for group in groups),
        "caseOverreachRisk": bool(case_count) and primary_count == 0,
        "note": (
            "命例仅作参考, 不得单独决定格局与用神"
            if case_count and primary_count
            else "图谱/RAG 主裁证据已就位"
            if primary_count
            else "暂无分层证据"
        ),
    }


def _bucket_hit(hit: dict[str, Any]) -> str:
    role = str(hit.get("evidenceRole") or hit.get("evidenceBucket") or "")
    bucket_map = {
        "primary_judge": "primaryEvidence",
        "tiaohou_judge": "primaryEvidence",
        "geju_judge": "primaryEvidence",
        "qishi_judge": "primaryEvidence",
        "shishen_judge": "primaryEvidence",
        "suiyun_judge": "primaryEvidence",
        "interactions_judge": "secondaryEvidence",
        "secondary_support": "secondaryEvidence",
        "modern_explanation": "secondaryEvidence",
        "case_reference": "caseReference",
        "low_trust": "excludedOrLowTrust",
    }
    return bucket_map.get(role, "excludedOrLowTrust")


def partition_rag_hits(hits: list[dict[str, Any]]) -> TieredEvidence:
    tiered = TieredEvidence()
    for hit in hits:
        bucket = _bucket_hit(hit)
        target = getattr(tiered, bucket, None)
        if isinstance(target, list):
            target.append(hit)
    return tiered


def _geju_rule_group(rule_id: str) -> str:
    if rule_id.startswith("geju:aspect:"):
        return "aspect"
    if rule_id.startswith("geju:special:"):
        return "special"
    if rule_id.startswith("geju:month:"):
        return "month"
    return "other"


GEJU_GROUP_LABELS = {
    "aspect": "成败救应",
    "month": "月令格局",
    "special": "杂格外格",
    "other": "其他",
}


def _quote_from_node(node: dict | None) -> str:
    if not node:
        return ""
    claims = node.get("claims") or []
    if claims:
        return str(claims[0].get("quote") or "")[:300]
    return str(node.get("quote") or "")[:300]


def _build_geju_evidence_items(verdict, store) -> list[EvidenceChainItem]:
    grouped: dict[str, list[str]] = {}
    for rule_id in verdict.ruleIds or []:
        grouped.setdefault(_geju_rule_group(rule_id), []).append(rule_id)

    items: list[EvidenceChainItem] = []
    for group_key in ("month", "aspect", "special", "other"):
        rule_ids = grouped.get(group_key) or []
        if not rule_ids:
            continue
        quotes: list[str] = []
        for rule_id in rule_ids[:4]:
            quote = _quote_from_node(store.get_by_id(rule_id) if store else None)
            if quote:
                quotes.append(quote)
        label = GEJU_GROUP_LABELS.get(group_key, group_key)
        items.append(
            EvidenceChainItem(
                conclusion=f"{label}: {verdict.summary}",
                ruleId=", ".join(rule_ids),
                primaryClassic=verdict.classic,
                quote=quotes[0] if quotes else "",
                secondary=[],
                boundary=verdict.boundary,
                confidence=verdict.confidenceBand,
                conclusionKind=verdict.conclusionKind,
            )
        )
    return items


def _suiyun_rule_group(rule_id: str) -> str:
    if rule_id.startswith("liunian:sanming_"):
        return "liunian_sanming"
    if rule_id.startswith("liunian:event_"):
        return "liunian_event"
    if rule_id.startswith("liunian:"):
        return "liunian"
    if rule_id.startswith("suiyun:ganzhi:"):
        return "ganzhi"
    if rule_id.startswith("suiyun:category:"):
        return "category"
    return "other"


SUIYUN_GROUP_LABELS = {
    "ganzhi": "大运干支",
    "category": "岁运总则",
    "liunian": "流年规则",
    "liunian_event": "流年事件",
    "liunian_sanming": "三命流年",
    "other": "其他",
}


def _build_tiaohou_evidence_item(verdict, store) -> EvidenceChainItem | None:
    if not verdict.ruleIds:
        return None
    quote = _quote_from_node(store.get_by_id(verdict.ruleIds[0]) if store else None)
    return EvidenceChainItem(
        conclusion=f"调候: {verdict.summary}",
        ruleId=verdict.ruleIds[0],
        primaryClassic=verdict.classic,
        quote=quote,
        secondary=[],
        boundary=verdict.boundary,
        confidence=verdict.confidenceBand,
        conclusionKind=verdict.conclusionKind,
    )


def _build_suiyun_evidence_items(verdict, store) -> list[EvidenceChainItem]:
    grouped: dict[str, list[str]] = {}
    for rule_id in verdict.ruleIds or []:
        grouped.setdefault(_suiyun_rule_group(rule_id), []).append(rule_id)

    items: list[EvidenceChainItem] = []
    for group_key in ("ganzhi", "category", "liunian", "liunian_event", "liunian_sanming", "other"):
        rule_ids = grouped.get(group_key) or []
        if not rule_ids:
            continue
        quote = _quote_from_node(store.get_by_id(rule_ids[0]) if store else None)
        label = SUIYUN_GROUP_LABELS.get(group_key, group_key)
        items.append(
            EvidenceChainItem(
                conclusion=f"{label}: {verdict.summary}",
                ruleId=", ".join(rule_ids),
                primaryClassic=verdict.classic,
                quote=quote,
                secondary=[],
                boundary=verdict.boundary,
                confidence=verdict.confidenceBand,
                conclusionKind=verdict.conclusionKind,
            )
        )
    return items


def _build_interactions_evidence_items(verdict, store) -> list[EvidenceChainItem]:
    items: list[EvidenceChainItem] = []
    for rule_id in verdict.ruleIds or []:
        node = store.get_by_id(rule_id) if store else None
        summary = str((node or {}).get("summary") or verdict.summary)
        claim = ((node or {}).get("claims") or [{}])[0]
        items.append(
            EvidenceChainItem(
                conclusion=f"合冲刑害: {summary}",
                ruleId=rule_id,
                primaryClassic=str(claim.get("classic") or verdict.classic),
                quote=_quote_from_node(node),
                secondary=[],
                boundary=verdict.boundary,
                confidence=verdict.confidenceBand,
                conclusionKind=verdict.conclusionKind,
            )
        )
    if not items:
        items.append(
            EvidenceChainItem(
                conclusion=verdict.summary,
                ruleId="",
                primaryClassic=verdict.classic,
                quote="",
                secondary=[],
                boundary=verdict.boundary,
                confidence=verdict.confidenceBand,
                conclusionKind=verdict.conclusionKind,
            )
        )
    return items


def build_evidence_chain(
    verdicts: list,
    knowledge_hits: list[KnowledgeHit] | list[dict],
    rag_hits: list[dict[str, Any]],
) -> list[EvidenceChainItem]:
    chain: list[EvidenceChainItem] = []
    evidence_rows = knowledge_hits_to_evidence(knowledge_hits, limit=8)
    service = get_knowledge_service()
    store = service.store if service.enabled else None

    for verdict in verdicts:
        if verdict.role == "case":
            continue
        if verdict.role == "geju" and verdict.ruleIds and store:
            geju_items = _build_geju_evidence_items(verdict, store)
            if geju_items:
                chain.extend(geju_items)
                continue
        if verdict.role == "tiaohou" and verdict.ruleIds and store:
            tiaohou_item = _build_tiaohou_evidence_item(verdict, store)
            if tiaohou_item:
                chain.append(tiaohou_item)
                continue
        if verdict.role == "suiyun" and verdict.ruleIds and store:
            suiyun_items = _build_suiyun_evidence_items(verdict, store)
            if suiyun_items:
                chain.extend(suiyun_items)
                continue
        if verdict.role == "interactions" and store:
            interaction_items = _build_interactions_evidence_items(verdict, store)
            if interaction_items:
                chain.extend(interaction_items)
                continue

        quote = ""
        secondary: list[str] = []
        for row in evidence_rows:
            if row.get("topic") == verdict.role or verdict.classic in str(row.get("claims")):
                claims = row.get("claims") or []
                if claims:
                    quote = str(claims[0].get("quote") or "")[:300]
                break
        if not quote:
            for hit in rag_hits:
                if verdict.classic and hit.get("classic") == verdict.classic:
                    quote = str(hit.get("excerpt") or "")[:300]
                    break
        for hit in rag_hits:
            classic = str(hit.get("classic") or "")
            if classic and classic != verdict.classic:
                secondary.append(classic)

        chain.append(
            EvidenceChainItem(
                conclusion=verdict.summary,
                ruleId=verdict.ruleIds[0] if verdict.ruleIds else "",
                primaryClassic=verdict.classic,
                quote=quote,
                secondary=secondary[:3],
                boundary=verdict.boundary,
                confidence=verdict.confidenceBand,
                conclusionKind=verdict.conclusionKind,
            )
        )
    return chain


class ClassicFirstRetriever:
    """Controlled RAG retrieval driven by evidence requests."""

    def __init__(self, rag_provider: Any | None = None) -> None:
        self._rag = rag_provider

    async def fetch_for_requests(
        self,
        requests: list[EvidenceRequest],
        *,
        top_k: int = 3,
    ) -> TieredEvidence:
        if self._rag is None:
            return TieredEvidence()

        merged: list[dict[str, Any]] = []
        seen: set[str] = set()
        for req in requests:
            query = req.query or req.topic
            if not query:
                continue
            try:
                rows = await self._rag.search(
                    query,
                    top_k=top_k,
                    category="01八字命理",
                    authority_tiers=req.authorityTiers or None,
                    evidence_roles=req.evidenceRoles or None,
                    library_roles=req.libraryRoles or req.sourceScope or None,
                    classic_whitelist=req.classicWhitelist or None,
                    topic_scope=[req.topic] if req.topic else None,
                    exclude_benchmark=True,
                    judge_only=req.judgeOnly,
                )
            except TypeError:
                rows = await self._rag.search(query, top_k=top_k, category="01八字命理")
            except Exception:
                continue

            for row in normalize_rag_excerpts(rows if isinstance(rows, list) else []):
                key = str(row.get("excerpt") or "")[:80]
                if key and key not in seen:
                    seen.add(key)
                    merged.append(row)

        return partition_rag_hits(merged)

    def knowledge_hits_for_chart(self, chart: dict[str, Any]) -> list[KnowledgeHit]:
        service = get_knowledge_service()
        if not service.enabled:
            return []
        result = service.resolve_for_chart(chart)
        return result.hits
