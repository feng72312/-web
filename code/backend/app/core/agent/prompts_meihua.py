from __future__ import annotations

from typing import Any

from app.core.agent.interpret_style import InterpretStyle, style_mode_block


def build_meihua_interpret_prompt(
    chart: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    excerpts: list[dict[str, str]],
    *,
    style: InterpretStyle = "professional",
) -> str:
    context = build_meihua_chat_context(chart, knowledge_hits, excerpts)
    ti = chart.get("tiGua", {})
    yong = chart.get("yongGua", {})
    if style == "plain":
        task = (
            f"请用纯白话给出梅花占断摘要, 首句说明体卦{ti.get('name', '')}与用卦{yong.get('name', '')} "
            f"对问事意味着什么.\n"
            "直接说结果与建议, 控制在 350 字以内, 不要编造典籍出处."
        )
    else:
        task = (
            f"请给出梅花易数断语摘要, 首句必须写明: "
            f"体卦{ti.get('name', '')}({ti.get('element', '')}), "
            f"用卦{yong.get('name', '')}({yong.get('element', '')}), "
            f"体用关系为{chart.get('tiYongRelation', '')}.\n"
            "解盘参考邵雍梅花易数体用生克, 结合动爻、变卦、互卦与问事.\n"
            "控制在 400 字以内, 不要编造典籍出处."
        )
    return f"{context}\n\n{style_mode_block(style)}\n\n{task}"


def build_meihua_chat_context(
    chart: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    excerpts: list[dict[str, str]],
) -> str:
    ben = chart.get("benGua", {})
    bian = chart.get("bianGua")
    hu = chart.get("huGua")
    lines = chart.get("lines", [])
    line_text = "\n".join(
        f"第{item['position']}爻 {'阳' if item.get('isYang') else '阴'}"
        f"{' 动' if item.get('isMoving') else ''}"
        for item in lines
    )
    hit_text = "\n".join(
        f"{idx}. [{hit.get('topic', '')}] {hit.get('summary', '')}"
        for idx, hit in enumerate(knowledge_hits, start=1)
    ) or "(暂无结构化节点)"
    excerpt_text = "\n".join(
        f"{idx}. [{item.get('source', '')}] {item.get('excerpt', '')}"
        for idx, item in enumerate(excerpts, start=1)
    ) or "(暂无摘录)"
    bian_text = bian.get("name", "无") if bian else "无"
    hu_text = hu.get("name", "无") if hu else "无"
    question = chart.get("input", {}).get("question", "")
    static_note = "静卦(下体上用)" if chart.get("isStatic") else ""
    return (
        f"问事: {question}\n"
        f"本卦: {ben.get('name', '')}\n"
        f"变卦: {bian_text}\n"
        f"互卦: {hu_text}\n"
        f"动爻: {chart.get('movingLines', [])} {static_note}\n"
        f"体卦: {chart.get('tiGua', {})}\n"
        f"用卦: {chart.get('yongGua', {})}\n"
        f"体用: {chart.get('tiYongRelation', '')}\n"
        f"爻象:\n{line_text}\n\n"
        f"结构化典籍:\n{hit_text}\n\n"
        f"向量检索摘录:\n{excerpt_text}"
    )


def build_meihua_chat_init_prompt(
    chart: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    excerpts: list[dict[str, str]],
) -> str:
    return (
        build_meihua_chat_context(chart, knowledge_hits, excerpts)
        + "\n\n你是梅花易数助手, 回答须紧扣体用生克与已给卦象, 勿引入纳甲六亲."
    )
