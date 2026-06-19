from __future__ import annotations

from typing import Any

from app.core.ziwei.judgement.models import EvidenceRequest, ZiweiJudgeVerdict


class MutagenJudge:
    def judge(self, chart: dict[str, Any]) -> ZiweiJudgeVerdict:
        events: list[dict[str, str]] = []
        for palace in chart.get("palaces") or []:
            palace_name = str(palace.get("name") or "")
            for row in palace.get("mutagenStars") or []:
                events.append(
                    {
                        "scope": "natal",
                        "fromPalace": palace_name,
                        "toPalace": palace_name,
                        "mutagenType": str(row.get("mutagen") or ""),
                        "star": str(row.get("name") or ""),
                        "direction": "自化" if True else "飞入",
                    }
                )
            flying = palace.get("flyingMutagens") or {}
            for outbound in flying.get("outbound") or []:
                events.append(
                    {
                        "scope": "natal",
                        "fromPalace": palace_name,
                        "toPalace": str(outbound.get("targetPalace") or ""),
                        "mutagenType": str(outbound.get("mutagen") or ""),
                        "star": str(outbound.get("star") or ""),
                        "direction": "飞出",
                    }
                )
            for inbound in flying.get("inbound") or []:
                events.append(
                    {
                        "scope": "natal",
                        "fromPalace": str(inbound.get("sourcePalace") or ""),
                        "toPalace": palace_name,
                        "mutagenType": str(inbound.get("mutagen") or ""),
                        "star": str(inbound.get("star") or ""),
                        "direction": "飞入",
                    }
                )

        if not events:
            return ZiweiJudgeVerdict(
                role="mutagen",
                classic="太微赋",
                summary="未检出结构化四化飞星, 仅可论生年四化与宫干飞化",
                stance="neutral",
                ruleIds=["mutagen:none_detected"],
                confidenceBand="weak",
            )

        ji_events = [item for item in events if item.get("mutagenType") == "忌"]
        lu_events = [item for item in events if item.get("mutagenType") == "禄"]
        summaries = []
        rule_ids = []
        for item in events[:8]:
            summaries.append(
                f"{item['scope']} {item['fromPalace']}{item['direction']}{item['mutagenType']}入{item['toPalace']}({item['star']})"
            )
            rule_ids.append(
                f"ziwei_mutagen:{item['fromPalace']}:{item['mutagenType']}:{item['toPalace']}"
            )

        stance = "neutral"
        if ji_events and not lu_events:
            stance = "unfavorable"
        elif lu_events and not ji_events:
            stance = "favorable"
        elif ji_events and lu_events:
            stance = "mixed"

        band = "medium"
        if len(ji_events) >= 2:
            band = "weak"
        elif lu_events and len(lu_events) >= 2:
            band = "strong"

        return ZiweiJudgeVerdict(
            role="mutagen",
            classic="太微赋",
            summary="; ".join(summaries),
            stance=stance,
            ruleIds=rule_ids[:6],
            confidenceBand=band,
            flags={"events": events[:12], "jiCount": len(ji_events), "luCount": len(lu_events)},
        )

    def evidence_request(self, chart: dict[str, Any]) -> EvidenceRequest:
        parts = ["紫微四化", "飞星"]
        for palace in chart.get("palaces") or []:
            for row in palace.get("mutagenStars") or []:
                parts.append(f"{row.get('name')}{row.get('mutagen')}")
        return EvidenceRequest(
            ruleId="mutagen:natal",
            topic="mutagen",
            query=" ".join(parts[:8]),
            classicWhitelist=["太微赋", "大德山人"],
        )
