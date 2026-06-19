"""Structured tiaohou block for contest MCQ prompts."""

from __future__ import annotations

import re
from typing import Any

from app.core.knowledge.factory import get_knowledge_service
from app.core.knowledge.keys import (
    build_tiaohou_fallback_keys,
    build_tiaohou_key,
    ZHI_TO_MONTH_LABEL,
)
from app.core.knowledge.models import CompressedContext
from app.core.knowledge.tiers import hit_to_public

YONGSHEN_PATTERNS = (
    re.compile(r"先取([甲乙丙丁戊己庚辛壬癸、]{1,12})"),
    re.compile(r"次用([甲乙丙丁戊己庚辛壬癸、]{1,12})"),
    re.compile(r"用([甲乙丙丁戊己庚辛壬癸、]{1,12})"),
    re.compile(r"得([甲乙丙丁戊己庚辛壬癸])([甲乙丙丁戊己庚辛壬癸])逢"),
    re.compile(r"喜([甲乙丙丁戊己庚辛壬癸火水木金土、]{2,16})"),
)


def _exposed_stems(chart: dict[str, Any]) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    labels = {"year": "年", "month": "月", "day": "日", "hour": "时"}
    for key, label in labels.items():
        gan = str((chart.get("pillars") or {}).get(key, {}).get("gan") or "").strip()
        if gan:
            rows.append((label, gan))
    return rows


def _extract_yongshen_hints(text: str) -> list[str]:
    hints: list[str] = []
    for pattern in YONGSHEN_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        if match.lastindex and match.lastindex >= 2:
            hints.append(f"得{match.group(1)}{match.group(2)}逢")
        else:
            hints.append(match.group(1))
    deduped: list[str] = []
    seen: set[str] = set()
    for hint in hints:
        if hint not in seen:
            seen.add(hint)
            deduped.append(hint)
    return deduped[:4]


def lookup_tiaohou_rows(chart: dict[str, Any]) -> list[dict]:
    service = get_knowledge_service()
    if not service.enabled:
        return []
    try:
        key = build_tiaohou_key(chart)
    except ValueError:
        return []
    rows = service.store.lookup("tiaohou", key)
    if rows:
        return rows
    pillars = chart.get("pillars") or {}
    day_gan = str(chart.get("dayMaster") or pillars.get("day", {}).get("gan") or "")
    month_zhi = str(pillars.get("month", {}).get("zhi") or "")
    for fb_key in build_tiaohou_fallback_keys(day_gan, month_zhi):
        rows = service.store.lookup("tiaohou", fb_key)
        if rows:
            return rows
    return []


def _lookup_tiaohou_hit(chart: dict[str, Any]) -> tuple[str, str, str]:
    rows = lookup_tiaohou_rows(chart)
    if not rows:
        return "", "", ""
    hit = hit_to_public(rows[0])
    quote = ""
    if hit.claims:
        quote = str(hit.claims[0].quote or "")[:420]
    return hit.id, hit.summary, quote


def _tiaohou_from_judgement(judgement: dict[str, Any] | None) -> tuple[str, str, str]:
    if not judgement:
        return "", "", ""
    for item in judgement.get("evidenceChain") or []:
        rule_id = str(item.get("ruleId") or "")
        if rule_id.startswith("tiaohou:"):
            return rule_id, str(item.get("conclusion") or ""), str(item.get("quote") or "")
    for row in (judgement.get("arbitration") or {}).get("judgeOpinions") or []:
        if row.get("role") != "tiaohou":
            continue
        rule_ids = row.get("ruleIds") or []
        return (
            str(rule_ids[0] if rule_ids else ""),
            str(row.get("summary") or ""),
            "",
        )
    return "", "", ""


def _tiaohou_from_compressed(compressed: CompressedContext | None) -> tuple[str, str, str]:
    if not compressed:
        return "", "", ""
    for hit in compressed.hits:
        if hit.topic != "tiaohou":
            continue
        quote = ""
        if hit.claims:
            quote = str(hit.claims[0].quote or "")[:420]
        return hit.id, hit.summary, quote
    return "", "", ""


def build_tiaohou_prompt_block(
    chart: dict[str, Any],
    *,
    judgement: dict[str, Any] | None = None,
    compressed: CompressedContext | None = None,
) -> str:
    rule_id, summary, quote = _tiaohou_from_judgement(judgement)
    if not summary:
        rule_id, summary, quote = _tiaohou_from_compressed(compressed)
    if not summary:
        rule_id, summary, quote = _lookup_tiaohou_hit(chart)
    if not summary:
        return ""

    pillars = chart.get("pillars") or {}
    day_gan = str(chart.get("dayMaster") or pillars.get("day", {}).get("gan") or "")
    month_zhi = str(pillars.get("month", {}).get("zhi") or "")
    month_label = ZHI_TO_MONTH_LABEL.get(month_zhi, "")

    stems = _exposed_stems(chart)
    stem_line = " ".join(f"{label}{gan}" for label, gan in stems) if stems else "(无透干)"
    source_text = quote or summary
    yongshen_hints = _extract_yongshen_hints(source_text)
    yongshen_line = "、".join(yongshen_hints) if yongshen_hints else "见原文取舍"

    lines = [
        "【穷通宝鉴调候】(主裁典籍, 优先级高于命例与常识臆测)",
        f"日干{day_gan} | 月支{month_zhi}({month_label}) | ruleId={rule_id or 'unknown'}",
        f"调候摘要: {summary[:180]}",
        f"透干: {stem_line}",
        f"用神提示: {yongshen_line}",
    ]
    if quote:
        lines.append(f"原文摘录: {quote[:360]}")
    boundary = ""
    if judgement:
        for row in (judgement.get("arbitration") or {}).get("judgeOpinions") or []:
            if row.get("role") == "tiaohou" and row.get("boundary"):
                boundary = str(row.get("boundary"))
                break
    if boundary:
        lines.append(f"断语边界: {boundary[:120]}")
    lines.append("调候题须先核对喜用忌与透干救应, 再排格局流年; 勿跳过本节直接猜选项.")
    return "\n".join(lines)
