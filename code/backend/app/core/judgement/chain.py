from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.concurrency.cpu_pool import run_cpu
from app.core.judgement.arbitrator import ClassicArbitrator, apply_no_primary_confidence_cap
from app.core.judgement.evidence import (
    ClassicFirstRetriever,
    build_evidence_chain,
    build_graph_primary_evidence,
    build_tiered_evidence_summary,
    merge_primary_evidence,
    load_case_references,
)
from app.core.judgement.judges import ALL_JUDGES
from app.core.judgement.models import BaziJudgementReport, JudgementStep, TieredEvidence
from app.core.knowledge.keys import build_chart_lookup_keys
from app.core.knowledge.luck_chart import enrich_chart_for_judgement
from app.core.rag.factory import build_rag_provider


STEP_DEFS = [
    ("month", "月令与旺衰"),
    ("tiaohou", "调候判断"),
    ("geju", "格局判断"),
    ("qishi", "气势流通"),
    ("shishen", "十神六亲"),
    ("interactions", "合冲刑害与神煞"),
    ("suiyun", "大运流年"),
    ("boundary", "结论边界"),
]


@dataclass
class _BaziCpuPhase:
    chart: dict[str, Any]
    verdicts: list[Any]
    evidence_requests: list[Any]
    arbitration: Any
    knowledge_hits: list[Any]
    graph_primary: list[dict[str, Any]]
    case_refs: list[dict[str, Any]]


class BaziJudgementChain:
    def __init__(self, *, use_rag: bool = True) -> None:
        self._arbitrator = ClassicArbitrator()
        self._use_rag = use_rag
        self._retriever = ClassicFirstRetriever(
            build_rag_provider() if use_rag else None
        )

    async def run(
        self,
        chart: dict[str, Any],
        *,
        question: str = "",
        benchmark_meta: dict[str, Any] | None = None,
    ) -> BaziJudgementReport:
        cpu = await run_cpu(
            self._cpu_phase,
            chart,
            question,
            benchmark_meta,
        )
        tiered = TieredEvidence()
        if self._use_rag:
            tiered = await self._retriever.fetch_for_requests(cpu.evidence_requests)
            tiered.primaryEvidence = merge_primary_evidence(
                cpu.graph_primary,
                tiered.primaryEvidence,
            )
            tiered.caseReference.extend(cpu.case_refs)
        else:
            tiered.primaryEvidence = cpu.graph_primary
        return await run_cpu(self._assemble_report, cpu, tiered)

    def _cpu_phase(
        self,
        chart: dict[str, Any],
        question: str,
        benchmark_meta: dict[str, Any] | None,
    ) -> _BaziCpuPhase:
        chart = enrich_chart_for_judgement(
            chart,
            question=question,
            benchmark_meta=benchmark_meta,
        )
        verdicts = [judge.judge(chart) for judge in ALL_JUDGES]
        evidence_requests = [judge.evidence_request(chart) for judge in ALL_JUDGES]
        arbitration = self._arbitrator.arbitrate(verdicts, evidence_requests)
        knowledge_hits = self._retriever.knowledge_hits_for_chart(chart)
        graph_primary = build_graph_primary_evidence(verdicts)
        case_refs = load_case_references(chart, limit=3) if self._use_rag else []
        return _BaziCpuPhase(
            chart=chart,
            verdicts=verdicts,
            evidence_requests=evidence_requests,
            arbitration=arbitration,
            knowledge_hits=knowledge_hits,
            graph_primary=graph_primary,
            case_refs=case_refs,
        )

    def _assemble_report(
        self,
        cpu: _BaziCpuPhase,
        tiered: TieredEvidence,
    ) -> BaziJudgementReport:
        rag_hits: list[dict[str, Any]] = []
        if self._use_rag:
            rag_hits = (
                tiered.primaryEvidence
                + tiered.secondaryEvidence
                + tiered.caseReference
                + tiered.excludedOrLowTrust
            )
        else:
            rag_hits = list(tiered.primaryEvidence)
        evidence_chain = build_evidence_chain(cpu.verdicts, cpu.knowledge_hits, rag_hits)
        primary_count = len(tiered.primaryEvidence or [])
        arbitration = apply_no_primary_confidence_cap(cpu.arbitration, primary_count)
        steps = self._build_steps(cpu.chart, cpu.verdicts)

        lookup_keys: dict[str, Any] = {}
        try:
            lookup_keys = build_chart_lookup_keys(cpu.chart)
        except Exception:
            lookup_keys = {}

        return BaziJudgementReport(
            steps=steps,
            arbitration=arbitration,
            evidenceChain=evidence_chain,
            tieredEvidence=tiered,
            tieredEvidenceSummary=build_tiered_evidence_summary(tiered.model_dump()),
            lookupKeys=lookup_keys,
        )

    def _build_steps(self, chart: dict[str, Any], verdicts: list) -> list[JudgementStep]:
        by_role = {v.role: v for v in verdicts}
        steps: list[JudgementStep] = []
        for step_id, label in STEP_DEFS:
            status = "ok"
            summary = ""
            if step_id == "month":
                month_v = by_role.get("month")
                if month_v:
                    summary = month_v.summary
                    status = (
                        "partial"
                        if month_v.conclusionKind == "insufficient_evidence"
                        else "ok"
                    )
                else:
                    month = (chart.get("pillars") or {}).get("month", {})
                    summary = f"月柱 {month.get('ganzhi', '')}, 月令气势为先"
            elif step_id in by_role:
                v = by_role[step_id]
                summary = v.summary
                status = "partial" if v.conclusionKind == "insufficient_evidence" else "ok"
            elif step_id == "boundary":
                case_v = by_role.get("case")
                summary = case_v.summary if case_v else "区分经典支持、规则推导与经验参考"
            else:
                status = "skipped"
            steps.append(JudgementStep(id=step_id, label=label, status=status, summary=summary))
        return steps
