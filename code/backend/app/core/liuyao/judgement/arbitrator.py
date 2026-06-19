from __future__ import annotations

from app.core.liuyao.judgement.judgement_models import (
    ArbitrationResult,
    EvidenceRequest,
    LiuyaoJudgeVerdict,
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


class LiuyaoArbiter:
    def arbitrate(
        self,
        verdicts: list[LiuyaoJudgeVerdict],
        evidence_requests: list[EvidenceRequest],
        *,
        primary_evidence_count: int = 0,
    ) -> ArbitrationResult:
        by_role = {v.role: v for v in verdicts}
        conflicts: list[str] = []
        boundaries: list[str] = []
        wang = by_role.get("wang_shuai")
        sheng = by_role.get("sheng_ke")
        dong = by_role.get("dong_bian")

        if wang and sheng:
            if wang.stance == "favorable" and sheng.stance in {"unfavorable", "mixed"}:
                _append_conflict(
                    conflicts,
                    "用神得月建之气偏旺, 但忌神发动或克用神, 有基础但受阻",
                )
            if wang.stance == "unfavorable" and sheng.stance == "favorable":
                _append_conflict(
                    conflicts,
                    "用神偏弱而原神扶助, 须看填实、合会或动变救应",
                )

        if dong and wang:
            if dong.flags.get("benLiuChong") and wang.flags.get("yuePo"):
                _append_conflict(conflicts, "六冲又月破, 事多散动且用神受损")

        for verdict in verdicts:
            if verdict.boundary:
                boundaries.append(verdict.boundary)

        scores = [_band_score(v.confidenceBand) for v in verdicts if v.conclusionKind != "insufficient_evidence"]
        base_score = sum(scores) / len(scores) if scores else 0.4
        if conflicts:
            base_score = max(0.25, base_score - 0.12 * len(conflicts))
        if wang and wang.flags.get("yuePo"):
            base_score = max(0.2, base_score - 0.15)
        if primary_evidence_count <= 0:
            base_score = min(base_score, 0.55)
            boundaries.append("缺少主裁证据, 置信度已封顶")
        band = _score_to_band(base_score)
        summary = "综合裁判完成"
        if conflicts:
            summary = "有基础但受阻" if "有基础但受阻" in " ".join(conflicts) else "存在裁判冲突, 须分层表述"
        elif wang and wang.stance == "favorable" and sheng and sheng.stance == "favorable":
            summary = "用神得气且生克方向偏利"
        elif wang and wang.stance == "unfavorable":
            summary = "用神失令或空破, 宜谨慎论吉凶"

        return ArbitrationResult(
            judgeOpinions=verdicts,
            conflicts=conflicts,
            finalBoundaries=boundaries,
            confidenceScore=round(base_score, 2),
            confidenceBand=band,
            evidenceRequests=evidence_requests,
            summary=summary,
        )
