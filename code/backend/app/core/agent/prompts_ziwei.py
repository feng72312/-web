from __future__ import annotations

import json
from typing import Any

from app.core.agent.interpret_style import InterpretStyle, style_mode_block


def _palace_lines(palaces: list[dict[str, Any]]) -> str:
    lines = []
    for palace in palaces[:12]:
        major = "、".join(s.get("name", "") for s in palace.get("majorStars") or [])
        lines.append(
            f"{palace.get('name', '')} {palace.get('stemBranch', '')} "
            f"主星:{major or '无'} 大限:{palace.get('decadalRange', '')}"
        )
    return "\n".join(lines) or "(无宫位)"


def build_ziwei_chat_context(
    chart: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    excerpts: list[dict[str, str]],
) -> str:
    inp = chart.get("input") or {}
    meta = chart.get("meta") or {}
    limits = chart.get("limits") or {}
    hit_text = "\n".join(
        f"{idx}. [{hit.get('topic', '')}] {hit.get('summary', '')}"
        for idx, hit in enumerate(knowledge_hits, start=1)
    ) or "(暂无结构化节点)"
    excerpt_text = "\n".join(
        f"{idx}. [{item.get('source', '')}] {item.get('excerpt', '')}"
        for idx, item in enumerate(excerpts, start=1)
    ) or "(暂无摘录)"
    parts = [
        f"问事: {inp.get('question', '')}",
        f"真太阳时: {chart.get('trueSolarTime', '')}",
        f"四柱: {json.dumps(chart.get('fourPillars', {}), ensure_ascii=False)}",
        f"局数: {meta.get('bureau', '')} 命主:{meta.get('soul', '')} 身主:{meta.get('body', '')}",
        f"规则: {json.dumps(chart.get('rulesMeta', {}), ensure_ascii=False)}",
        f"十二宫:\n{_palace_lines(chart.get('palaces') or [])}",
        f"大限: {json.dumps(limits.get('decadal', []), ensure_ascii=False)}",
        f"流年: {json.dumps(limits.get('yearly', {}), ensure_ascii=False)}",
        f"小限: {json.dumps(limits.get('current', {}).get('minor', {}), ensure_ascii=False)}",
        f"结构化节点:\n{hit_text}",
        f"典籍摘录:\n{excerpt_text}",
    ]
    return "\n".join(parts)


def build_ziwei_interpret_prompt(
    chart: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    excerpts: list[dict[str, str]],
    *,
    style: InterpretStyle = "professional",
) -> str:
    context = build_ziwei_chat_context(chart, knowledge_hits, excerpts)
    meta = chart.get("meta") or {}
    if style == "plain":
        task = (
            f"请用白话解读紫微斗数命盘, 首句概括{meta.get('bureau', '')}与命宫主星性情.\n"
            "结合大限、流年、小限说明当前运势, 控制在 500 字以内, 不要编造星曜位置."
        )
    else:
        task = (
            "请按南派三合紫微斗数解读, 以命宫、身宫、三方四正与四化为纲, "
            "结合大限、流年、小限论述.\n"
            "仅依据给定命盘结构, 可引用摘录典籍, 控制在 600 字以内, 不要编造星曜位置."
        )
    return f"{context}\n\n{style_mode_block(style)}\n\n{task}"


def build_ziwei_chat_init_prompt(
    chart: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    excerpts: list[dict[str, str]],
) -> str:
    return (
        build_ziwei_chat_context(chart, knowledge_hits, excerpts)
        + "\n\n你是紫微斗数助手, 以上盘为命主本命盘与运限, 回答须与盘符一致."
    )
