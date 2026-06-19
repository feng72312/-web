from __future__ import annotations

import json
from typing import Any

from app.core.agent.chat_scope import CHAT_SCOPE_GUARDRAIL
from app.core.agent.interpret_style import (
    InterpretStyle,
    plain_interpret_task_closing,
    ziwei_style_mode_block,
)


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


def _judgement_lines(judgement: dict[str, Any] | None) -> str:
    if not judgement:
        return "(暂无裁判链)"
    lines = []
    topic = judgement.get("topic") or {}
    if topic:
        lines.append(
            f"占事: {topic.get('topicLabel', '')} ({topic.get('topicId', '')})"
        )
    for row in judgement.get("judges") or []:
        lines.append(f"[{row.get('role', '')}] {row.get('summary', '')}")
    arb = judgement.get("arbitration") or {}
    if arb.get("summary"):
        lines.append(f"仲裁: {arb.get('summary')}")
    if arb.get("conflicts"):
        lines.append(f"冲突: {'; '.join(arb.get('conflicts') or [])}")
    summary = judgement.get("tieredEvidenceSummary") or {}
    if summary.get("note"):
        lines.append(f"证据: {summary.get('note')}")
    return "\n".join(lines) or "(暂无裁判链)"


def build_ziwei_interpret_prompt(
    chart: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    excerpts: list[dict[str, str]],
    *,
    style: InterpretStyle = "professional",
    judgement: dict[str, Any] | None = None,
) -> str:
    context = build_ziwei_chat_context(chart, knowledge_hits, excerpts)
    judgement_text = _judgement_lines(judgement)
    guardrail = (
        "表达约束: 不得编造星曜位置; 不得把单星口诀当全盘结论; "
        "不得把命例当规则; 不得混用未声明法派; 证据不足须明确说明."
    )
    meta = chart.get("meta") or {}
    bureau_hint = meta.get("bureau", "") or "未知"
    if style == "plain":
        task = (
            "请按上方四段式大纲, 输出一份从零基础读者视角可读的完整紫微批命.\n"
            f"第一部分可结合局象「{bureau_hint}」概括整体气质.\n"
            "必须依据下方裁判链结论与典籍摘录.\n"
            f"{plain_interpret_task_closing(2000)}"
        )
    else:
        task = (
            "请按上方四段式大纲, 输出一份可核对的专业紫微批命.\n"
            "以南派三合为纲, 结合命宫身宫、三方四正、四化与大限流年论述.\n"
            "仅依据给定命盘结构与裁判链结论表达, 控制在 2200 字以内, 不要编造星曜位置."
        )
    return (
        f"{context}\n\n裁判链:\n{judgement_text}\n\n{guardrail}\n\n"
        f"{ziwei_style_mode_block(style)}\n\n{task}"
    )


def build_ziwei_chat_init_prompt(
    chart: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    excerpts: list[dict[str, str]],
) -> str:
    return (
        build_ziwei_chat_context(chart, knowledge_hits, excerpts)
        + "\n\n你是紫微斗数助手, 以上盘为命主本命盘与运限, 回答须与盘符一致."
        + f"\n\n{CHAT_SCOPE_GUARDRAIL}"
    )
