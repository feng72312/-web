from __future__ import annotations

from typing import Any

from app.core.ziwei.judgement._helpers import PALACE_ALIASES, chart_school, soul_palace
from app.core.ziwei.judgement.models import EvidenceRequest, ZiweiJudgeVerdict
from app.core.ziwei.judgement.topic_judge import TopicResult

THEME_BY_TOPIC = {
    "marriage": "婚恋",
    "career": "事业",
    "wealth": "财运",
    "health": "健康",
    "family": "家庭",
    "general": "综合",
}


def _expand_palace_names(names: list[str]) -> set[str]:
    expanded: set[str] = set()
    for name in names:
        expanded.add(name)
        for canonical, aliases in PALACE_ALIASES.items():
            if name in aliases or name == canonical:
                expanded.add(canonical)
                expanded.update(aliases)
    return expanded


def _layer_palaces(scope: dict[str, Any] | None) -> list[str]:
    if not scope or not scope.get("available", True):
        return []
    names = scope.get("palaceNames") or []
    if isinstance(names, str):
        return [names] if names else []
    palace = scope.get("palaceName") or scope.get("palace")
    if palace:
        return [str(palace)]
    return [str(item) for item in names if item]


def _natal_key_palaces(chart: dict[str, Any], topic: TopicResult | None) -> set[str]:
    names: list[str] = ["命宫"]
    if topic:
        names.extend(topic.target_palaces)
    soul = soul_palace(chart)
    if soul and soul.get("name"):
        names.append(str(soul["name"]))
    return _expand_palace_names(names)


def _has_ji_mutagen(scope: dict[str, Any] | None) -> bool:
    if not scope:
        return False
    mutagens = scope.get("mutagens") or []
    stars = scope.get("mutagenStars") or []
    if any(str(item) == "忌" for item in mutagens):
        return True
    return any(str(row.get("mutagen") or "") == "忌" for row in stars if isinstance(row, dict))


def _build_event(
    *,
    trigger: str,
    theme: str,
    layer: str,
    palaces: list[str],
    natal_hits: list[str],
    has_ji: bool,
    target_year: int | None,
) -> dict[str, Any]:
    confidence = "medium"
    if natal_hits and has_ji:
        confidence = "strong"
    elif not natal_hits:
        confidence = "weak"
    return {
        "trigger": trigger,
        "theme": theme,
        "layer": layer,
        "palaces": palaces,
        "natalHits": natal_hits,
        "hasJiMutagen": has_ji,
        "targetYear": target_year,
        "confidence": confidence,
    }


class LimitJudge:
    def judge(
        self,
        chart: dict[str, Any],
        *,
        target_year: int | None = None,
        topic: TopicResult | None = None,
    ) -> ZiweiJudgeVerdict:
        limits = chart.get("limits") or {}
        current = limits.get("current") or {}
        active = limits.get("active") or {}
        theme = THEME_BY_TOPIC.get(topic.topic_id if topic else "general", "综合")
        natal_keys = _natal_key_palaces(chart, topic)
        events: list[dict[str, Any]] = []
        summaries: list[str] = []

        decadal_scope = current.get("decadal") or active.get("decadal") or {}
        yearly_scope = limits.get("yearly") or active.get("yearly") or {}
        minor_scope = current.get("minor") or {}

        for layer, scope, label in (
            ("decadal", decadal_scope, "大限"),
            ("yearly", yearly_scope, "流年"),
            ("minor", minor_scope, "小限"),
        ):
            palaces = _layer_palaces(scope)
            if not palaces and not scope.get("stemBranch"):
                continue
            natal_hits = [name for name in palaces if name in natal_keys]
            has_ji = _has_ji_mutagen(scope)
            stem_branch = str(scope.get("stemBranch") or "")
            palace_text = ",".join(palaces) if palaces else "未知"
            summaries.append(f"{label}{stem_branch}({palace_text})")
            if natal_hits or has_ji:
                events.append(
                    _build_event(
                        trigger=label,
                        theme=theme,
                        layer=layer,
                        palaces=palaces,
                        natal_hits=natal_hits,
                        has_ji=has_ji,
                        target_year=target_year or scope.get("targetYear"),
                    )
                )

        if target_year:
            summaries.append(f"目标年{target_year}")

        if not summaries:
            return ZiweiJudgeVerdict(
                role="limit",
                classic="太微赋",
                summary="运限数据不足, 无法建立事件链",
                stance="neutral",
                ruleIds=["limit:insufficient"],
                confidenceBand="weak",
                conclusionKind="insufficient_evidence",
            )

        stance = "neutral"
        if events:
            if any(event.get("hasJiMutagen") and event.get("natalHits") for event in events):
                stance = "unfavorable"
            elif any(event.get("natalHits") for event in events):
                stance = "mixed"

        band = "medium"
        if not events:
            band = "weak"
        elif any(event.get("confidence") == "strong" for event in events):
            band = "strong"

        boundary = "限运结论须与本命关键宫分区合参, 不得单流年定论"
        event_summary = "; ".join(
            f"{event['trigger']}引动{','.join(event['natalHits']) or '运限宫'}"
            f"({event['theme']})"
            for event in events[:4]
        )
        summary = "; ".join(summaries)
        if event_summary:
            summary = f"{summary}; 事件链: {event_summary}"

        rule_ids = [f"limit:{event['layer']}:{event['theme']}" for event in events[:4]]
        if not rule_ids:
            rule_ids = ["limit:scope_boundary"]

        return ZiweiJudgeVerdict(
            role="limit",
            classic="太微赋",
            summary=summary,
            stance=stance,
            ruleIds=rule_ids,
            confidenceBand=band,
            boundary=boundary,
            flags={
                "eventChain": events,
                "natalKeyPalaces": sorted(natal_keys),
                "school": chart_school(chart),
            },
        )

    def evidence_request(
        self,
        chart: dict[str, Any],
        topic: TopicResult | None,
    ) -> EvidenceRequest:
        theme = THEME_BY_TOPIC.get(topic.topic_id if topic else "general", "综合")
        palaces = list(topic.target_palaces[:4]) if topic else ["命宫"]
        limits = chart.get("limits") or {}
        yearly = limits.get("yearly") or {}
        query_parts = ["紫微", "大限", "流年", theme]
        if yearly.get("stemBranch"):
            query_parts.append(str(yearly["stemBranch"]))
        query_parts.extend(f"{palace}宫" for palace in palaces[:2])
        return EvidenceRequest(
            ruleId=f"limit:{theme}",
            topic="limit",
            palaceScope=palaces,
            school=chart_school(chart),
            query=" ".join(query_parts),
            classicWhitelist=["太微赋", "紫微斗数全书"],
            authorityTiers=["S", "A"],
        )
