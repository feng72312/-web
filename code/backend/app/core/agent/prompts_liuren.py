from __future__ import annotations

import json
from typing import Any

from app.core.agent.chat_scope import CHAT_SCOPE_GUARDRAIL
from app.core.agent.interpret_style import (
    InterpretStyle,
    plain_interpret_task_closing,
    style_mode_block,
)


def _si_ke_lines(si_ke: dict[str, Any]) -> str:
    lines = []
    for key, label in (("yi", "一课"), ("er", "二课"), ("san", "三课"), ("si", "四课")):
        row = si_ke.get(key) or {}
        lines.append(f"{label}: {row.get('pair', '')} {row.get('general', '')}")
    return "\n".join(lines) or "(无四课)"


def _san_chuan_lines(sc: dict[str, Any]) -> str:
    lines = []
    for key, label in (("chu", "初传"), ("zhong", "中传"), ("mo", "末传")):
        row = sc.get(key) or {}
        lines.append(
            f"{label}: {row.get('zhi', '')} {row.get('general', '')} "
            f"{row.get('liuQin', '')} 旬空{row.get('xunKong', '')}"
        )
    return "\n".join(lines) or "(无三传)"


def build_liuren_chat_context(
    chart: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    excerpts: list[dict[str, str]],
) -> str:
    inp = chart.get("input") or {}
    cat = "事占" if inp.get("category") == "shizhan" else "行占"
    lr = chart.get("liuren") or {}
    jk = chart.get("jinkou") or {}
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
        f"类别: {cat}",
        f"起课法: {inp.get('castMethod', '')}",
        f"真太阳时: {chart.get('trueSolarTime', '')}",
    ]
    if lr:
        parts.extend(
            [
                f"节气: {lr.get('jieqi', '')} 月将: {lr.get('yueJiang', '')}",
                f"占时四柱: {json.dumps(lr.get('fourPillars', {}), ensure_ascii=False)}",
                f"格局: {lr.get('geJu', {}).get('name', '')} {lr.get('geJu', {}).get('sub', '')}",
                f"四课:\n{_si_ke_lines(lr.get('siKe', {}))}",
                f"三传:\n{_san_chuan_lines(lr.get('sanChuan', {}))}",
                f"神煞: {json.dumps(lr.get('shenSha', {}), ensure_ascii=False)}",
            ]
        )
    if jk:
        parts.append(
            f"金口诀: 人元{jk.get('renYuan', '')} 地分{jk.get('difen', '')} "
            f"贵神{jk.get('guiShen', [])} 将神{jk.get('jiangShen', [])}"
        )
    parts.extend([f"结构化节点:\n{hit_text}", f"典籍摘录:\n{excerpt_text}"])
    return "\n".join(parts)


def build_liuren_interpret_prompt(
    chart: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    excerpts: list[dict[str, str]],
    *,
    style: InterpretStyle = "professional",
) -> str:
    context = build_liuren_chat_context(chart, knowledge_hits, excerpts)
    lr = chart.get("liuren") or {}
    ge = lr.get("geJu") or {}
    if style == "plain":
        task = (
            f"请用大白话给出六壬占断摘要, 首句用一句话说明此事当前局面意味着什么"
            f"(后台课体: {ge.get('name', '')}).\n"
            "直接说结果、大致时间窗口与建议.\n"
            f"{plain_interpret_task_closing(420)}"
        )
    else:
        task = (
            f"请按正六壬(月将加时、九宗门)与金口诀综合断事, "
            f"首句写明课体 {ge.get('name', '')} 与初传天将.\n"
            "仅依据占时四柱起课, 勿引用用户本命八字.\n"
            "参考六壬指南心印赋、指掌赋及课体神煞, 控制在 500 字以内, "
            "不要编造典籍出处."
        )
    return f"{context}\n\n{style_mode_block(style)}\n\n{task}"


def build_liuren_chat_init_prompt(
    chart: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    excerpts: list[dict[str, str]],
) -> str:
    return (
        build_liuren_chat_context(chart, knowledge_hits, excerpts)
        + "\n\n你是大六壬助手, 以上盘为占时起课, 与用户八字命盘无关."
        + f"\n\n{CHAT_SCOPE_GUARDRAIL}"
    )
