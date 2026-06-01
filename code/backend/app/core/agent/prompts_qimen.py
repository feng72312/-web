from __future__ import annotations

import json
from typing import Any

from app.core.agent.interpret_style import InterpretStyle, style_mode_block


def _palace_lines(chart: dict[str, Any]) -> str:
    lines = []
    for p in chart.get("palaces", []):
        lines.append(
            f"{p.get('name', '')}: 地{p.get('earth', '')} 天{p.get('heaven', '')} "
            f"人{p.get('human', '')} {p.get('star', '')} {p.get('door', '')} {p.get('god', '')}"
        )
    return "\n".join(lines) or "(无九宫数据)"


def _birth_profile_block(birth_profile: dict[str, Any] | None) -> str:
    if not birth_profile:
        return ""
    parts = [
        birth_profile.get("summary", ""),
        birth_profile.get("year", ""),
        birth_profile.get("month", ""),
        birth_profile.get("day", ""),
        birth_profile.get("hour", ""),
        birth_profile.get("gender", ""),
    ]
    text = " ".join(p for p in parts if p).strip()
    if not text:
        return ""
    return (
        f"\n用户本命参考(仅作 AI 辅助, 不参与起局): {text}\n"
        "断局仍以起局时刻盘为准, 勿用本命替代时盘用神.\n"
    )


def build_qimen_chat_context(
    chart: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    excerpts: list[dict[str, str]],
    birth_profile: dict[str, Any] | None = None,
) -> str:
    ju = chart.get("ju", {})
    zf = chart.get("zhiFuZhiShi", {})
    inp = chart.get("input", {})
    cat = "事占" if inp.get("category") == "shizhan" else "行占"
    hit_text = "\n".join(
        f"{idx}. [{hit.get('topic', '')}] {hit.get('summary', '')}"
        for idx, hit in enumerate(knowledge_hits, start=1)
    ) or "(暂无结构化节点)"
    excerpt_text = "\n".join(
        f"{idx}. [{item.get('source', '')}] {item.get('excerpt', '')}"
        for idx, item in enumerate(excerpts, start=1)
    ) or "(暂无摘录)"
    bp = birth_profile or chart.get("birthProfile")
    return (
        f"问事: {inp.get('question', '')}\n"
        f"类别: {cat}\n"
        f"方位: {inp.get('direction', '')}\n"
        f"起局: {ju.get('juName', '')} 节气{ju.get('jieqi', '')}\n"
        f"真太阳时: {chart.get('trueSolarTime', '')}\n"
        f"四柱: {json.dumps(chart.get('fourPillars', {}), ensure_ascii=False)}\n"
        f"值符: {zf.get('zhiFuStar', '')} {zf.get('zhiFuGong', '')} 干{zf.get('zhiFuGan', '')}\n"
        f"值使: {zf.get('zhiShiDoor', '')} {zf.get('zhiShiGong', '')}\n"
        f"九宫:\n{_palace_lines(chart)}\n"
        f"{_birth_profile_block(bp)}"
        f"结构化节点:\n{hit_text}\n"
        f"典籍摘录:\n{excerpt_text}"
    )


def build_qimen_interpret_prompt(
    chart: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    excerpts: list[dict[str, str]],
    birth_profile: dict[str, Any] | None = None,
    *,
    style: InterpretStyle = "professional",
) -> str:
    context = build_qimen_chat_context(
        chart, knowledge_hits, excerpts, birth_profile=birth_profile
    )
    ju = chart.get("ju", {})
    if style == "plain":
        task = (
            f"请用纯白话给出奇门占断摘要, 首句用一句话说明{ju.get('juName', '')}局对问事意味着什么.\n"
            "直接说吉凶、时机与行动建议, 控制在 400 字以内, 不要编造典籍出处."
        )
    else:
        task = (
            f"请按时家奇门拆补盘断事, 首句写明: {ju.get('juName', '')}、"
            f"值符值使落宫.\n"
            "参考奇门法窍门星神与事占/行占用神, 结合方位与问事.\n"
            "勿引用用户八字, 控制在 500 字以内, 不要编造典籍出处."
        )
    return f"{context}\n\n{style_mode_block(style)}\n\n{task}"


def build_qimen_chat_init_prompt(
    chart: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    excerpts: list[dict[str, str]],
    birth_profile: dict[str, Any] | None = None,
) -> str:
    return (
        build_qimen_chat_context(
            chart, knowledge_hits, excerpts, birth_profile=birth_profile
        )
        + "\n\n你是奇门遁甲助手, 以上盘为起局时刻排盘, 与用户八字无关."
    )
