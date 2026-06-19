from __future__ import annotations

from app.core.ziwei.judgement.models import (
    ArbitrationResult,
    EvidenceRequest,
    ZiweiJudgeVerdict,
)


def _append_conflict(conflicts: list[str], message: str) -> None:
    if message and message not in conflicts:
        conflicts.append(message)


def _band_score(band: str) -> float:
    return {"strong": 0.85, "medium": 0.55, "weak": 0.3}.get(band, 0.5)


def _score_to_band(score: float) -> str:
    if score >= 0.72:
        return "strong"
    if score >= 0.45:
        return "medium"
    return "weak"


class ZiweiArbiter:
    def arbitrate(
        self,
        verdicts: list[ZiweiJudgeVerdict],
        evidence_requests: list[EvidenceRequest],
        *,
        primary_evidence_count: int = 0,
    ) -> ArbitrationResult:
        by_role = {v.role: v for v in verdicts}
        conflicts: list[str] = []
        boundaries: list[str] = []

        soul = by_role.get("star")
        palace = by_role.get("palace")
        mutagen = by_role.get("mutagen")
        pattern = by_role.get("pattern")

        if soul and palace:
            if soul.stance == "favorable" and palace.stance == "unfavorable":
                _append_conflict(
                    conflicts,
                    "命宫星曜偏吉, 但主题宫位有独立风险, 须分区表述",
                )
            if soul.stance == "favorable" and mutagen and mutagen.stance == "unfavorable":
                _append_conflict(
                    conflicts,
                    "命宫格局佳, 但四化飞忌/化忌引动存在, 婚恋或主题宫须单独论风险",
                )

        if pattern and pattern.stance == "favorable" and mutagen and mutagen.stance == "unfavorable":
            _append_conflict(conflicts, "格局成立但四化有忌, 须看救应与限运")

        for verdict in verdicts:
            if verdict.boundary:
                boundaries.append(verdict.boundary)

        scores = [
            _band_score(v.confidenceBand)
            for v in verdicts
            if v.conclusionKind != "insufficient_evidence"
        ]
        base_score = sum(scores) / len(scores) if scores else 0.4
        if conflicts:
            base_score = max(0.25, base_score - 0.1 * len(conflicts))
        if primary_evidence_count <= 0:
            base_score = min(base_score, 0.55)
            boundaries.append("缺少主裁证据, 置信度已封顶")

        band = _score_to_band(base_score)
        summary = "综合裁判完成"
        if conflicts:
            summary = "存在分区冲突, 须分层表述, 不得用单宫或单星覆盖全盘"
        elif soul and soul.stance == "favorable" and (not mutagen or mutagen.stance != "unfavorable"):
            summary = "命宫与主题证据整体偏稳"

        return ArbitrationResult(
            judgeOpinions=verdicts,
            conflicts=conflicts,
            finalBoundaries=boundaries,
            confidenceScore=round(base_score, 2),
            confidenceBand=band,
            evidenceRequests=evidence_requests,
            summary=summary,
        )
