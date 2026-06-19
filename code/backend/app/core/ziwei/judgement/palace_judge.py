from __future__ import annotations

from typing import Any

from app.core.ziwei.judgement._helpers import (
    TRIAD_BY_PALACE,
    major_star_names,
    resolve_palace,
)
from app.core.ziwei.judgement.models import EvidenceRequest, ZiweiJudgeVerdict
from app.core.ziwei.judgement.topic_judge import TopicResult


def _stance_from_strength(strength: str, risk_flags: list[str]) -> str:
    if "mutagen_ji" in risk_flags:
        return "unfavorable"
    if strength in {"strong", "balanced"}:
        return "favorable"
    if strength in {"weak", "empty"}:
        return "unfavorable"
    return "mixed"


def _band_from_strength(strength: str, risk_flags: list[str]) -> str:
    if strength == "strong" and "mutagen_ji" not in risk_flags:
        return "strong"
    if strength in {"weak", "empty"} or "mutagen_ji" in risk_flags:
        return "weak"
    return "medium"


class PalaceJudge:
    def judge(self, chart: dict[str, Any], topic: TopicResult) -> ZiweiJudgeVerdict:
        pmap = {row.get("name"): row for row in chart.get("palaces") or []}
        summaries: list[str] = []
        stances: list[str] = []
        bands: list[str] = []
        rule_ids: list[str] = []
        flags: dict[str, Any] = {"palaces": {}}

        for canonical in topic.target_palaces[:4]:
            palace = resolve_palace(pmap, canonical)
            if not palace:
                continue
            name = str(palace.get("name") or canonical)
            strength = str(palace.get("palaceStrength") or "balanced")
            risk = list(palace.get("riskFlags") or [])
            majors = major_star_names(palace)
            borrowed = bool(palace.get("borrowedFromOpposite"))
            triad = palace.get("triadEvidence") or []
            triad_names = [str(item.get("name") or "") for item in triad if item.get("name")]
            stance = _stance_from_strength(strength, risk)
            band = _band_from_strength(strength, risk)
            stances.append(stance)
            bands.append(band)
            star_text = "、".join(majors) if majors else ("借对宫" + "、".join(palace.get("borrowedMajorStars") or []) if borrowed else "无主星")
            summaries.append(
                f"{name}: 主星{star_text}, 强度{strength}, 三方{','.join(triad_names) or '无'}"
            )
            rule_ids.append(f"ziwei_palace:{canonical}")
            flags["palaces"][name] = {
                "strength": strength,
                "riskFlags": risk,
                "borrowedFromOpposite": borrowed,
            }

        if not summaries:
            return ZiweiJudgeVerdict(
                role="palace",
                summary="无法定位主题宫位",
                stance="neutral",
                conclusionKind="insufficient_evidence",
                confidenceBand="weak",
            )

        overall_stance = "mixed"
        if all(item == "favorable" for item in stances):
            overall_stance = "favorable"
        elif all(item == "unfavorable" for item in stances):
            overall_stance = "unfavorable"
        elif "favorable" in stances and "unfavorable" in stances:
            overall_stance = "mixed"

        band_scores = {"strong": 3, "medium": 2, "weak": 1}
        avg_band = min(bands, key=lambda item: band_scores.get(item, 2))

        boundary = ""
        if topic.topic_id != "general" and "命宫" not in topic.target_palaces:
            boundary = f"本结论限{topic.topic_label}主题, 不替代命宫整体格局"

        return ZiweiJudgeVerdict(
            role="palace",
            classic="太微赋",
            summary="; ".join(summaries),
            stance=overall_stance,
            ruleIds=rule_ids,
            confidenceBand=avg_band,
            boundary=boundary,
            flags=flags,
        )

    def evidence_request(self, chart: dict[str, Any], topic: TopicResult) -> EvidenceRequest:
        palaces = topic.target_palaces[:3]
        query_parts = [f"紫微{palace}宫" for palace in palaces]
        query_parts.append(topic.topic_label)
        return EvidenceRequest(
            ruleId=topic.rule_id or "palace:topic",
            topic="palace",
            palaceScope=palaces,
            query=" ".join(query_parts),
            classicWhitelist=["太微赋", "紫微斗数全书"],
        )
