from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.config import settings
from app.core.concurrency.cpu_pool import run_cpu
from app.core.liuyao.judgement.arbitrator import LiuyaoArbiter
from app.core.liuyao.judgement.chart_enrich import enrich_chart_for_judgement
from app.core.liuyao.judgement.evidence import (
    LiuyaoEvidenceRetriever,
    build_evidence_chain,
    build_tiered_evidence_summary,
)
from app.core.liuyao.judgement.judgement_models import JudgementStep, LiuyaoJudgementReport
from app.core.liuyao.judgement.judges import (
    DongBianJudge,
    LiuShenJudge,
    ShengKeJudge,
    ShiYingJudge,
    WangShuaiJudge,
    YingQiJudge,
)
from app.core.liuyao.judgement.topic_judge import classify_topic
from app.core.liuyao.judgement.yong_shen_judge import judge_yong_shen
from app.core.rag.factory import build_rag_provider


STEP_DEFS = [
    ("topic", "占事分类"),
    ("yong_shen", "用神定位"),
    ("wang_shuai", "旺衰空破"),
    ("sheng_ke", "生克原忌"),
    ("dong_bian", "动变六冲"),
    ("shi_ying", "世应关系"),
    ("liu_shen", "六神辅助"),
    ("ying_qi", "应期边界"),
]


@dataclass
class _LiuyaoCpuPhase:
    enriched: dict[str, Any]
    topic: Any
    ys_payload: dict[str, Any]
    verdicts: list[Any]
    evidence_requests: list[Any]


class LiuyaoJudgementChain:
    def __init__(self, *, use_rag: bool = True) -> None:
        self._use_rag = use_rag
        self._arbiter = LiuyaoArbiter()
        self._wang = WangShuaiJudge()
        self._sheng = ShengKeJudge()
        self._dong = DongBianJudge()
        self._shi_ying = ShiYingJudge()
        self._liu_shen = LiuShenJudge()
        self._ying_qi = YingQiJudge()
        self._retriever = LiuyaoEvidenceRetriever(
            build_rag_provider() if use_rag else None
        )

    async def run(
        self,
        chart: dict[str, Any],
        *,
        question: str = "",
        yong_shen: dict[str, Any] | None = None,
        yong_shen_override: bool = False,
    ) -> LiuyaoJudgementReport:
        cpu = await run_cpu(
            self._cpu_phase,
            chart,
            question,
            yong_shen,
            yong_shen_override,
        )
        tiered = await self._retriever.fetch_for_requests(
            cpu.evidence_requests,
            category=settings.liuyao_rag_category,
        )
        return await run_cpu(self._assemble_report, cpu, tiered)

    def _cpu_phase(
        self,
        chart: dict[str, Any],
        question: str,
        yong_shen: dict[str, Any] | None,
        yong_shen_override: bool,
    ) -> _LiuyaoCpuPhase:
        question = (question or chart.get("input", {}).get("question") or "").strip()
        enriched = enrich_chart_for_judgement(chart)
        topic = classify_topic(question)

        if yong_shen:
            ys_payload = dict(yong_shen)
            if yong_shen_override:
                ys_payload["source"] = ys_payload.get("source") or "override"
                ys_payload["override"] = True
        else:
            ys_result = judge_yong_shen(enriched, question, topic)
            ys_payload = ys_result.to_dict()

        verdicts = [
            self._topic_verdict(topic),
            self._yong_shen_verdict(ys_payload),
            self._wang.judge(enriched, ys_payload),
            self._sheng.judge(enriched, ys_payload),
            self._dong.judge(enriched, ys_payload, topic.topic_id),
            self._shi_ying.judge(enriched, ys_payload),
            self._liu_shen.judge(enriched, ys_payload),
            self._ying_qi.judge(enriched, ys_payload),
        ]
        evidence_requests = [
            self._wang.evidence_request(enriched, ys_payload),
            self._sheng.evidence_request(enriched, ys_payload),
            self._dong.evidence_request(enriched, ys_payload),
            self._shi_ying.evidence_request(enriched, ys_payload),
            self._ying_qi.evidence_request(enriched, ys_payload),
        ]
        return _LiuyaoCpuPhase(
            enriched=enriched,
            topic=topic,
            ys_payload=ys_payload,
            verdicts=verdicts,
            evidence_requests=evidence_requests,
        )

    def _assemble_report(
        self,
        cpu: _LiuyaoCpuPhase,
        tiered: Any,
    ) -> LiuyaoJudgementReport:
        primary_count = len(tiered.primaryEvidence)
        arbitration = self._arbiter.arbitrate(
            cpu.verdicts,
            cpu.evidence_requests,
            primary_evidence_count=primary_count if self._use_rag else 1,
        )
        rag_hits = (
            tiered.primaryEvidence
            + tiered.secondaryEvidence
            + tiered.caseReference
            + tiered.modernSupport
        )
        evidence_chain = build_evidence_chain(cpu.verdicts, rag_hits)
        steps = self._build_steps(cpu.verdicts)

        return LiuyaoJudgementReport(
            steps=steps,
            topic=cpu.topic.to_dict(),
            yongShen=cpu.ys_payload,
            judges=cpu.verdicts,
            arbitration=arbitration,
            evidenceChain=evidence_chain,
            tieredEvidence=tiered,
            tieredEvidenceSummary=build_tiered_evidence_summary(tiered),
            enrichedChart=cpu.enriched,
        )

    def _topic_verdict(self, topic) -> Any:
        from app.core.liuyao.judgement.judgement_models import LiuyaoJudgeVerdict

        return LiuyaoJudgeVerdict(
            role="topic",
            classic="黄金策",
            summary=f"占事归类: {topic.topic_label} ({topic.topic_id})",
            stance="neutral",
            ruleIds=[topic.rule_id] if topic.rule_id else [f"topic:{topic.topic_id}"],
            confidenceBand="strong" if topic.confidence >= 0.6 else "medium",
            flags={"candidateYongShen": topic.candidate_yong_shen},
        )

    def _yong_shen_verdict(self, yong_shen: dict[str, Any]) -> Any:
        from app.core.liuyao.judgement.judgement_models import LiuyaoJudgeVerdict

        source = str(yong_shen.get("source") or "rule")
        conf = float(yong_shen.get("confidence") or 0.5)
        band = "strong" if conf >= 0.7 else "medium" if conf >= 0.45 else "weak"
        boundary = ""
        if yong_shen.get("override"):
            boundary = "用户已覆盖用神, 以下裁判基于覆盖值"
        return LiuyaoJudgeVerdict(
            role="yong_shen",
            classic="增删卜易",
            summary=(
                f"用神: {yong_shen.get('yongShen', '')} "
                f"第{yong_shen.get('position', '')}爻 ({source})"
            ),
            stance="neutral",
            ruleIds=[str(yong_shen.get("ruleId") or "yong_shen:locate")],
            confidenceBand=band,
            boundary=boundary,
            flags={"source": source, "override": bool(yong_shen.get("override"))},
        )

    def _build_steps(self, verdicts: list) -> list[JudgementStep]:
        by_role = {v.role: v for v in verdicts}
        steps: list[JudgementStep] = []
        for step_id, label in STEP_DEFS:
            verdict = by_role.get(step_id)
            status = "ok"
            summary = verdict.summary if verdict else ""
            if verdict and verdict.conclusionKind == "insufficient_evidence":
                status = "partial"
            if verdict and verdict.confidenceBand == "weak":
                status = "partial"
            steps.append(JudgementStep(id=step_id, label=label, status=status, summary=summary))
        return steps
