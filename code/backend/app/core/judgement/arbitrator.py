from __future__ import annotations

from app.core.judgement.models import ArbitrationResult, JudgeVerdict


def _append_conflict(conflicts: list[str], message: str) -> None:
    if message and message not in conflicts:
        conflicts.append(message)


def _interaction_stress(interactions: JudgeVerdict | None) -> bool:
    if interactions is None:
        return False
    if interactions.stance == "unfavorable":
        return True
    text = interactions.summary or ""
    return "冲" in text or "害" in text


def _interaction_support(interactions: JudgeVerdict | None) -> bool:
    if interactions is None:
        return False
    if interactions.stance == "favorable":
        return True
    text = interactions.summary or ""
    return "合" in text and "冲" not in text and "害" not in text


def _detect_conflicts(verdicts: list[JudgeVerdict]) -> list[str]:
    conflicts: list[str] = []
    by_role = {v.role: v for v in verdicts if v.role != "case"}
    month = by_role.get("month")
    tiaohou = by_role.get("tiaohou")
    geju = by_role.get("geju")
    qishi = by_role.get("qishi")
    suiyun = by_role.get("suiyun")
    interactions = by_role.get("interactions")

    if month and geju:
        if month.stance == "unfavorable" and geju.stance == "favorable":
            _append_conflict(
                conflicts,
                "日主失令偏弱而格局成格, 须分层次: 命局有格而运岁须扶身",
            )
        if month.stance == "favorable" and geju.stance == "unfavorable":
            _append_conflict(
                conflicts,
                "日主得令而格局未成, 宜先论破格救应再论体用",
            )
    if month and tiaohou:
        if month.stance == "unfavorable" and tiaohou.stance == "favorable":
            _append_conflict(
                conflicts,
                "身偏弱而调候已备, 须并列寒暖与扶抑, 勿单以调候代旺衰",
            )

    if tiaohou and geju:
        if tiaohou.stance == "favorable" and geju.stance == "unfavorable":
            _append_conflict(
                conflicts,
                "调候裁判认为有用神方向, 但格局裁判认为条件不足, 需岁运扶助才显",
            )
    if geju and qishi and geju.summary and qishi.summary:
        if "偏" in qishi.summary and "成格" in geju.summary:
            _append_conflict(conflicts, "气势偏枯与格局成败判断存在张力, 须并列说明")
    if interactions and geju:
        if interactions.stance == "unfavorable" and "成" in geju.summary:
            _append_conflict(conflicts, "合冲刑害示波折, 但格局裁判仍见成格, 须分层次表述")
        if interactions.stance == "unfavorable" and geju.stance == "favorable":
            _append_conflict(conflicts, "刑冲害与格局喜神方向存在张力, 不可单以冲论凶")
    shishen = by_role.get("shishen")
    if shishen and interactions:
        if interactions.stance == "unfavorable" and "六亲" in shishen.summary:
            _append_conflict(
                conflicts,
                "十神六亲与刑冲合害并见, 须分宫位引动与合冲压力, 勿混为一谈",
            )
    if tiaohou and interactions and _interaction_stress(interactions):
        if tiaohou.stance == "favorable":
            _append_conflict(
                conflicts,
                "调候见用神方向, 但原局刑冲害牵动, 宜先论救应再论顺逆",
            )
        elif tiaohou.stance == "unfavorable" and _interaction_support(interactions):
            _append_conflict(
                conflicts,
                "调候仍偏枯, 不宜因六合就忽视寒暖调候",
            )
    if suiyun and interactions:
        if suiyun.stance == "favorable" and _interaction_stress(interactions):
            _append_conflict(
                conflicts,
                "岁运见顺, 但原局刑冲害仍在, 须分命局结构与本运应期两层",
            )
        if suiyun.stance == "unfavorable" and _interaction_support(interactions):
            _append_conflict(
                conflicts,
                "原局合神有情, 但岁运仍见压力, 不可只凭合论吉",
            )
        if suiyun.stance == "unfavorable" and interactions.stance == "unfavorable":
            _append_conflict(
                conflicts,
                "岁运与原局刑冲压力叠加, 应期波动偏大, 断语宜留余地",
            )
    if tiaohou and suiyun:
        if tiaohou.stance == "favorable" and suiyun.stance == "unfavorable":
            _append_conflict(
                conflicts,
                "调候喜神方向与岁运压力不一致, 须分寒暖调候与大运流年两层",
            )
        if tiaohou.stance == "unfavorable" and suiyun.stance == "favorable":
            _append_conflict(
                conflicts,
                "命局调候仍欠, 但当前岁运有扶, 宜分原局体质与当下运势",
            )
    return conflicts


def _boundaries(verdicts: list[JudgeVerdict], conflicts: list[str]) -> list[str]:
    bounds: list[str] = []
    for v in verdicts:
        if v.boundary:
            bounds.append(v.boundary)
    for c in conflicts:
        bounds.append(c)
    case = next((v for v in verdicts if v.role == "case"), None)
    if case:
        bounds.append(case.boundary or case.summary)
    return bounds


def _confidence(verdicts: list[JudgeVerdict], conflicts: list[str]) -> tuple[float, str]:
    primary = [v for v in verdicts if v.role != "case"]
    if not primary:
        return 0.3, "weak"
    strong = sum(1 for v in primary if v.confidenceBand == "strong")
    medium = sum(1 for v in primary if v.confidenceBand == "medium")
    score = (strong * 0.9 + medium * 0.6) / max(len(primary), 1)
    if conflicts:
        score *= 0.75
    if score >= 0.75:
        return round(score, 2), "strong"
    if score >= 0.5:
        return round(score, 2), "medium"
    return round(score, 2), "weak"


def apply_no_primary_confidence_cap(
    arbitration: ArbitrationResult,
    primary_count: int,
) -> ArbitrationResult:
    if primary_count > 0:
        return arbitration
    downgrades = {"strong": "medium", "medium": "weak", "weak": "weak"}
    new_band = downgrades.get(arbitration.confidenceBand, "weak")
    new_score = min(float(arbitration.confidenceScore or 0.0), 0.45)
    if new_band == arbitration.confidenceBand and new_score == arbitration.confidenceScore:
        return arbitration
    return arbitration.model_copy(
        update={"confidenceBand": new_band, "confidenceScore": new_score},
    )


class ClassicArbitrator:
    def arbitrate(self, verdicts: list[JudgeVerdict], evidence_requests: list) -> ArbitrationResult:
        primary = [v for v in verdicts if v.role != "case"]
        conflicts = _detect_conflicts(verdicts)
        score, band = _confidence(verdicts, conflicts)
        return ArbitrationResult(
            judgeOpinions=verdicts,
            conflicts=conflicts,
            finalBoundaries=_boundaries(verdicts, conflicts),
            confidenceScore=score,
            confidenceBand=band,
            evidenceRequests=evidence_requests,
        )
