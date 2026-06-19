from __future__ import annotations

from typing import Any

from app.core.ziwei.judgement._helpers import (
    MAJOR_STAR_NAMES,
    body_palace_name,
    major_star_names,
    soul_palace,
)
from app.core.ziwei.judgement.models import EvidenceRequest, ZiweiJudgeVerdict


def _brightness_band(palace: dict[str, Any] | None, star_name: str) -> str:
    if not palace:
        return "unknown"
    for star in palace.get("majorStars") or []:
        if str(star.get("name") or "") == star_name:
            brightness = str(star.get("brightness") or "")
            if any(token in brightness for token in ("庙", "旺")):
                return "strong"
            if any(token in brightness for token in ("陷", "落")):
                return "weak"
            return "balanced"
    if star_name in (palace.get("borrowedMajorStars") or []):
        opposite = palace.get("oppositeEvidence") or {}
        return _brightness_band({"majorStars": opposite.get("majorStars") and []}, star_name)
    summary = str(palace.get("brightnessSummary") or "")
    if star_name in summary:
        if any(token in summary for token in ("庙", "旺")):
            return "strong"
        if any(token in summary for token in ("陷", "落")):
            return "weak"
    return "balanced"


class StarJudge:
    def judge(self, chart: dict[str, Any]) -> ZiweiJudgeVerdict:
        soul = soul_palace(chart) or {}
        body_name = body_palace_name(chart)
        soul_stars = major_star_names(soul)
        summaries: list[str] = []
        rule_ids: list[str] = []
        stances: list[str] = []

        for star in soul_stars[:4]:
            band = _brightness_band(soul, star)
            stance = "favorable" if band == "strong" else "unfavorable" if band == "weak" else "neutral"
            stances.append(stance)
            summaries.append(f"命宫{star}亮度{band}")
            rule_ids.append(f"ziwei_star:{star}")

        if body_name and body_name != str(soul.get("name") or ""):
            pmap = {row.get("name"): row for row in chart.get("palaces") or []}
            body = pmap.get(body_name) or {}
            body_stars = major_star_names(body)
            if body_stars:
                summaries.append(f"身宫{body_name}主星{'、'.join(body_stars[:3])}")
                rule_ids.append(f"ziwei_body:{body_name}")

        if not summaries:
            return ZiweiJudgeVerdict(
                role="star",
                classic="太微赋",
                summary="命宫无主星, 须参对宫借星与三方四正, 不得单星口诀定论",
                stance="neutral",
                ruleIds=["ziwei_star:empty_soul"],
                confidenceBand="weak",
                boundary="空宫借星时星曜结论置信度受限",
                flags={"emptySoul": True},
            )

        overall = "neutral"
        if stances.count("favorable") >= max(1, len(stances) // 2):
            overall = "favorable"
        elif stances.count("unfavorable") >= max(1, len(stances) // 2):
            overall = "unfavorable"

        return ZiweiJudgeVerdict(
            role="star",
            classic="太微赋",
            summary="; ".join(summaries),
            stance=overall,
            ruleIds=rule_ids,
            confidenceBand="medium" if len(soul_stars) == 1 else "strong",
            boundary="星曜结论须与宫位主题及四化合参, 不得泛化为全盘定论",
            flags={"soulStars": soul_stars, "bodyPalace": body_name},
        )

    def evidence_request(self, chart: dict[str, Any]) -> EvidenceRequest:
        soul = soul_palace(chart) or {}
        stars = major_star_names(soul) or list(MAJOR_STAR_NAMES[:3])
        query = " ".join(f"紫微{star}" for star in stars[:4])
        return EvidenceRequest(
            ruleId="star:natal_major",
            topic="star",
            starScope=stars[:4],
            query=query,
            classicWhitelist=["太微赋", "细论星情"],
        )
