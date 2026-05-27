from __future__ import annotations

import json
from typing import Any


def _format_excerpts(excerpts: list[dict[str, str]]) -> str:
    if not excerpts:
        return "(暂无典籍摘录)"
    lines: list[str] = []
    for idx, item in enumerate(excerpts, start=1):
        source = item.get("source", "未知来源")
        excerpt = item.get("excerpt", "")
        lines.append(f"{idx}. [{source}] {excerpt}")
    return "\n".join(lines)


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


def build_chart_context(chart: dict[str, Any], excerpts: list[dict[str, str]]) -> str:
    inp = chart.get("input", {})
    pillars = chart.get("pillars", {})
    name = inp.get("name") or "未命名"
    return (
        f"你是一位精通子平八字的命理师, 请基于以下结构化命盘资料作答.\n"
        f"要求: 只使用给定资料推理, 不要编造典籍出处; 用语清晰, 用中文回答; "
        f"直接输出解读正文, 不要加 MODE 标记或 markdown 标题.\n\n"
        f"命主: {name}\n"
        f"日主: {chart.get('dayMaster')} ({chart.get('dayMasterWuxing')})\n"
        f"四柱: 年{pillars.get('year', {}).get('ganzhi', '')} "
        f"月{pillars.get('month', {}).get('ganzhi', '')} "
        f"日{pillars.get('day', {}).get('ganzhi', '')} "
        f"时{pillars.get('hour', {}).get('ganzhi', '')}\n"
        f"分析模块:\n{_format_sections(chart)}\n\n"
        f"典籍摘录:\n{_format_excerpts(excerpts)}"
    )


def build_chat_init_prompt(chart: dict[str, Any], excerpts: list[dict[str, str]] | None = None) -> str:
    context = build_chart_context(chart, excerpts or [])
    return f"{context}\n\n以上是当前命盘背景资料, 请等待用户提问."


def build_interpret_prompt(chart: dict[str, Any], excerpts: list[dict[str, str]]) -> str:
    context = build_chart_context(chart, excerpts)
    return (
        f"{context}\n\n"
        f"请给出一份命理解读摘要, 重点包括: 格局倾向, 体用关系, 用神喜忌方向, "
        f"以及需要结合大运进一步确认的点. 控制在 300 字以内."
    )
