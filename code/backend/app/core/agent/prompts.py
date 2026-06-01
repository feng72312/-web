from __future__ import annotations

import json
from typing import Any

from app.core.agent.interpret_style import InterpretStyle, style_mode_block

from app.core.knowledge.models import CompressedContext, KnowledgeHit


def _format_knowledge_hits(hits: list[KnowledgeHit]) -> str:
    if not hits:
        return "(暂无结构化典籍节点)"
    lines: list[str] = []
    for idx, hit in enumerate(hits, start=1):
        agreement = hit.agreementLevel
        safe = "可直引" if hit.safeAutoAnswer else "需结合论"
        lines.append(
            f"{idx}. [{hit.topic}/{agreement}/{safe}] {hit.summary}"
        )
        for claim in hit.claims[:2]:
            source = claim.classic or claim.sourceFile
            quote = claim.quote[:180]
            lines.append(f"   - [{source}] {quote}")
    return "\n".join(lines)


def _format_excerpts(excerpts: list[dict[str, str]]) -> str:
    if not excerpts:
        return "(暂无按需检索原文)"
    lines: list[str] = []
    for idx, item in enumerate(excerpts, start=1):
        source = item.get("source", "未知来源")
        excerpt = item.get("excerpt", "")
        lines.append(f"{idx}. [{source}] {excerpt}")
    return "\n".join(lines)


def _gender_label(gender: Any) -> str:
    if gender == 1:
        return "男"
    if gender == 0:
        return "女"
    return "未知"


def _format_sections(chart: dict[str, Any]) -> str:
    sections = chart.get("sections", [])
    if not sections:
        return "(暂无分析模块输出)"
    lines: list[str] = []
    for section in sections:
        section_id = section.get("id", "")
        name = section.get("name", section_id)
        data = section.get("data", {})
        lines.append(f"- {name}: {json.dumps(data, ensure_ascii=False)}")
    return "\n".join(lines)


def build_chart_context(
    chart: dict[str, Any],
    compressed: CompressedContext | None = None,
    rag_excerpts: list[dict[str, str]] | None = None,
    *,
    legacy_excerpts: list[dict[str, str]] | None = None,
) -> str:
    inp = chart.get("input", {})
    pillars = chart.get("pillars", {})
    name = inp.get("name") or "未命名"
    gender = _gender_label(inp.get("gender"))
    hits = compressed.hits if compressed else []
    excerpts = rag_excerpts if rag_excerpts is not None else (legacy_excerpts or [])
    return (
        f"你是一位精通子平八字的命理师, 请基于以下结构化命盘资料作答.\n"
        f"要求: 只使用给定资料推理, 不要编造典籍出处; 用语清晰, 用中文回答; "
        f"争议条目须并列说明, 不可强行合一; "
        f"推断现实事件时须结合大运流年与用神喜忌, 勿脱离命盘臆测; "
        f"直接输出解读正文, 不要加 MODE 标记或 markdown 标题.\n\n"
        f"命主: {name}\n"
        f"性别: {gender}\n"
        f"日主: {chart.get('dayMaster')} ({chart.get('dayMasterWuxing')})\n"
        f"四柱: 年{pillars.get('year', {}).get('ganzhi', '')} "
        f"月{pillars.get('month', {}).get('ganzhi', '')} "
        f"日{pillars.get('day', {}).get('ganzhi', '')} "
        f"时{pillars.get('hour', {}).get('ganzhi', '')}\n"
        f"分析模块:\n{_format_sections(chart)}\n\n"
        f"结构化典籍结论:\n{_format_knowledge_hits(hits)}\n\n"
        f"补充原文摘录:\n{_format_excerpts(excerpts)}"
    )


def build_chat_init_prompt(
    chart: dict[str, Any],
    compressed: CompressedContext | None = None,
    rag_excerpts: list[dict[str, str]] | None = None,
    *,
    legacy_excerpts: list[dict[str, str]] | None = None,
) -> str:
    context = build_chart_context(
        chart,
        compressed=compressed,
        rag_excerpts=rag_excerpts,
        legacy_excerpts=legacy_excerpts,
    )
    return f"{context}\n\n以上是当前命盘背景资料, 请等待用户提问."


def build_interpret_prompt(
    chart: dict[str, Any],
    compressed: CompressedContext | None = None,
    rag_excerpts: list[dict[str, str]] | None = None,
    *,
    legacy_excerpts: list[dict[str, str]] | None = None,
    style: InterpretStyle = "professional",
) -> str:
    context = build_chart_context(
        chart,
        compressed=compressed,
        rag_excerpts=rag_excerpts,
        legacy_excerpts=legacy_excerpts,
    )
    if style == "plain":
        task = (
            "请用纯白话给出命理解读摘要: 直接回答问事或论命要点, "
            "说明趋势与建议; 控制在 350 字以内."
        )
    else:
        task = (
            "请给出一份命理解读摘要, 重点包括: 格局倾向, 体用关系, 用神喜忌方向, "
            "以及需要结合大运进一步确认的点. 控制在 300 字以内."
        )
    return f"{context}\n\n{style_mode_block(style)}\n\n{task}"
