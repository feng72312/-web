from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.config import settings
from app.core.concurrency.cpu_pool import run_cpu
from app.core.rag.factory import build_rag_provider
from app.core.ziwei.chart_enrich import enrich_chart
from app.core.ziwei.judgement.arbitrator import ZiweiArbiter
from app.core.ziwei.judgement.cross_school_judge import CrossSchoolJudge
from app.core.ziwei.judgement._helpers import chart_school
from app.core.ziwei.judgement.evidence import (
    ZiweiEvidenceRetriever,
    build_evidence_chain,
    build_tiered_evidence_summary,
)
from app.core.ziwei.judgement.limit_judge import LimitJudge
from app.core.ziwei.judgement.models import JudgementStep, ZiweiJudgeVerdict, ZiweiJudgementReport
from app.core.ziwei.judgement.mutagen_judge import MutagenJudge
from app.core.ziwei.judgement.palace_judge import PalaceJudge
from app.core.ziwei.judgement.pattern_judge import PatternJudge
from app.core.ziwei.judgement.star_judge import StarJudge
from app.core.ziwei.judgement.topic_judge import classify_topic


STEP_DEFS = [
    ("topic", "占事分类"),
    ("palace", "宫位裁判"),
    ("star", "星曜裁判"),
    ("mutagen", "四化裁判"),
    ("pattern", "格局裁判"),
    ("limit", "限运裁判"),
    ("cross_school", "法派仲裁"),
]


@dataclass
class _ZiweiCpuPhase:
    enriched: dict[str, Any]
    topic: Any
    verdicts: list[ZiweiJudgeVerdict]
    evidence_requests: list[Any]
    active_school: str


class ZiweiJudgementChain:
    def __init__(self, *, use_rag: bool = True) -> None:
        self._use_rag = use_rag
        self._arbiter = ZiweiArbiter()
        self._palace = PalaceJudge()
        self._star = StarJudge()
        self._mutagen = MutagenJudge()
        self._pattern = PatternJudge()
        self._limit = LimitJudge()
        self._cross_school = CrossSchoolJudge()
        self._retriever = ZiweiEvidenceRetriever(
            build_rag_provider() if use_rag else None
        )

    async def run(
        self,
        chart: dict[str, Any],
        *,
        question: str = "",
        target_year: int | None = None,
        school: str | None = None,
    ) -> ZiweiJudgementReport:
        cpu = await run_cpu(
            self._cpu_phase,
            chart,
            question,
            target_year,
            school,
        )
        tiered = await self._retriever.fetch_for_requests(
            cpu.evidence_requests,
            category=settings.ziwei_rag_category,
            school=cpu.active_school,
        )
        return await run_cpu(self._assemble_report, cpu, tiered)

    def _cpu_phase(
        self,
        chart: dict[str, Any],
        question: str,
        target_year: int | None,
        school: str | None,
    ) -> _ZiweiCpuPhase:
        question = (question or chart.get("input", {}).get("question") or "").strip()
        enriched = enrich_chart(dict(chart))
        topic = classify_topic(question)

        pattern_verdict = self._pattern.judge(enriched)
        verdicts = [
            self._topic_verdict(topic),
            self._palace.judge(enriched, topic),
            self._star.judge(enriched),
            self._mutagen.judge(enriched),
            pattern_verdict,
            self._limit.judge(enriched, target_year=target_year, topic=topic),
            self._cross_school.judge(enriched, school=school),
        ]
        evidence_requests = [
            self._palace.evidence_request(enriched, topic),
            self._star.evidence_request(enriched),
            self._mutagen.evidence_request(enriched),
            self._pattern.evidence_request(enriched, pattern_verdict),
            self._limit.evidence_request(enriched, topic),
        ]
        active_school = school or chart_school(enriched)
        return _ZiweiCpuPhase(
            enriched=enriched,
            topic=topic,
            verdicts=verdicts,
            evidence_requests=evidence_requests,
            active_school=active_school,
        )

    def _assemble_report(
        self,
        cpu: _ZiweiCpuPhase,
        tiered: Any,
    ) -> ZiweiJudgementReport:
        primary_count = len(tiered.primaryEvidence)
        arbitration = self._arbiter.arbitrate(
            cpu.verdicts,
            cpu.evidence_requests,
            primary_evidence_count=primary_count if self._use_rag else 1,
        )
        rag_hits = (
            tiered.primaryEvidence
            + tiered.secondaryEvidence
            + tiered.schoolCommentary
            + tiered.caseReference
        )
        evidence_chain = build_evidence_chain(cpu.verdicts, rag_hits)
        steps = self._build_steps(cpu.verdicts)

        return ZiweiJudgementReport(
            steps=steps,
            topic=cpu.topic.to_dict(),
            judges=cpu.verdicts,
            arbitration=arbitration,
            evidenceChain=evidence_chain,
            tieredEvidence=tiered,
            tieredEvidenceSummary=build_tiered_evidence_summary(tiered),
            enrichedChart=cpu.enriched,
            rulesMeta=dict(cpu.enriched.get("rulesMeta") or {}),
        )

    def _topic_verdict(self, topic) -> ZiweiJudgeVerdict:
        return ZiweiJudgeVerdict(
            role="topic",
            classic="太微赋",
            summary=f"占事归类: {topic.topic_label}",
            stance="neutral",
            ruleIds=[topic.rule_id] if topic.rule_id else [f"topic:{topic.topic_id}"],
            confidenceBand="strong" if topic.confidence >= 0.6 else "medium",
            flags={"targetPalaces": topic.target_palaces},
        )

    def _build_steps(self, verdicts: list[ZiweiJudgeVerdict]) -> list[JudgementStep]:
        role_map = {
            "topic": "topic",
            "palace": "palace",
            "star": "star",
            "mutagen": "mutagen",
            "pattern": "pattern",
            "limit": "limit",
            "cross_school": "cross_school",
        }
        by_role = {v.role: v for v in verdicts}
        steps: list[JudgementStep] = []
        for step_id, label in STEP_DEFS:
            verdict = by_role.get(role_map.get(step_id, step_id))
            status = "ok"
            summary = verdict.summary if verdict else ""
            if verdict and verdict.conclusionKind == "insufficient_evidence":
                status = "partial"
            if verdict and verdict.confidenceBand == "weak":
                status = "partial"
            steps.append(JudgementStep(id=step_id, label=label, status=status, summary=summary))
        return steps
