"""Structured qishi block for contest MCQ prompts."""

from __future__ import annotations

from typing import Any

from app.core.knowledge.factory import get_knowledge_service
from app.core.knowledge.keys import build_qishi_key
from app.core.knowledge.tiers import hit_to_public

CATEGORY_BY_IMBALANCE = {
    "spread": "tiyong",
    "blocked": "tongguan",
    "clear": "qingqi",
    "murky": "zhuoqi",
}


def _wuxing_spread(chart: dict[str, Any]) -> tuple[str, str, float]:
    wx = chart.get("wuxingCount") or {}
    if not wx:
        return "", "", 0.0
    dominant = max(wx, key=wx.get)
    weakest = min(wx, key=wx.get)
    values = list(wx.values())
    spread = (max(values) - min(values)) if values else 0.0
    return dominant, weakest, float(spread)


def build_qishi_lookup_keys(chart: dict[str, Any]) -> list[dict[str, str]]:
    keys: list[dict[str, str]] = []
    try:
        keys.append(build_qishi_key(chart))
    except ValueError:
        pass
    dominant, weakest, spread = _wuxing_spread(chart)
    if spread >= 3:
        keys.append({"category": CATEGORY_BY_IMBALANCE["spread"]})
    if dominant and weakest:
        keys.append({"category": "tiyong"})
        if spread >= 2:
            keys.append({"category": "tongguan"})
    deduped: list[dict[str, str]] = []
    seen: set[str] = set()
    for key in keys:
        token = str(sorted(key.items()))
        if token in seen:
            continue
        seen.add(token)
        deduped.append(key)
    return deduped


def lookup_qishi_rows(chart: dict[str, Any]) -> list[dict]:
    service = get_knowledge_service()
    if not service.enabled:
        return []
    rows: list[dict] = []
    seen: set[str] = set()
    for key in build_qishi_lookup_keys(chart):
        for row in service.store.lookup("qishi", key):
            rid = str(row.get("id") or "")
            if rid and rid not in seen:
                seen.add(rid)
                rows.append(row)
    return rows


def _qishi_from_judgement(judgement: dict[str, Any] | None) -> tuple[str, str, str]:
    if not judgement:
        return "", "", ""
    for item in judgement.get("evidenceChain") or []:
        rule_id = str(item.get("ruleId") or "")
        if rule_id.startswith("qishi:"):
            return rule_id, str(item.get("conclusion") or ""), str(item.get("quote") or "")
    for row in (judgement.get("arbitration") or {}).get("judgeOpinions") or []:
        if row.get("role") != "qishi":
            continue
        rule_ids = row.get("ruleIds") or []
        return (
            str(rule_ids[0] if rule_ids else ""),
            str(row.get("summary") or ""),
            "",
        )
    return "", "", ""


def build_qishi_prompt_block(
    chart: dict[str, Any],
    *,
    judgement: dict[str, Any] | None = None,
) -> str:
    rule_id, summary, quote = _qishi_from_judgement(judgement)
    if not summary:
        rows = lookup_qishi_rows(chart)
        if rows:
            hit = hit_to_public(rows[0])
            rule_id = hit.id
            summary = hit.summary
            if hit.claims:
                quote = str(hit.claims[0].quote or "")[:360]
    if not summary:
        wx = chart.get("wuxingCount") or {}
        if not wx:
            return ""
        dominant = max(wx, key=wx.get)
        weakest = min(wx, key=wx.get)
        summary = f"五行偏{dominant}弱{weakest}, 须分清浊流通与体用"
        rule_id = f"qishi:dominant:{dominant}"
    lines = [
        "【滴天髓气势】",
        f"ruleId: {rule_id}",
        f"结论: {summary}",
    ]
    if quote:
        lines.append(f"原文: {quote[:300]}")
    dominant, weakest, spread = _wuxing_spread(chart)
    if dominant:
        lines.append(f"盘面五行: 偏{dominant}弱{weakest}, 极差{spread:.0f}")
    lines.append("气势题须先据此判断清浊流通, 再与格局调候互证, 勿单看十神.")
    return "\n".join(lines)
