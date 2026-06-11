from __future__ import annotations

from typing import Any

from app.core.agent.chat_scope import CHAT_SCOPE_GUARDRAIL
from app.core.agent.interpret_style import (
    InterpretStyle,
    plain_interpret_task_closing,
    style_mode_block,
)


def build_yong_shen_prompt(chart: dict[str, Any], question: str) -> str:
    ben = chart.get("benGua", {})
    lines = chart.get("lines", [])
    liuqin_rows = [
        f"第{line['position']}爻 {line['stem']}{line['branch']} {line['liuqin']}"
        for line in lines
    ]
    return (
        "你是六爻纳甲专家, 请根据问事内容推断用神.\n"
        "只输出 JSON, 不要 markdown, 格式:\n"
        '{"yongShen":"父母|兄弟|子孙|妻财|官鬼","position":1,"reason":"..."}\n'
        "position 必须是卦中该六亲所在爻位(1-6).\n\n"
        f"问事: {question}\n"
        f"本卦: {ben.get('name', '')}\n"
        f"卦宫: {ben.get('palace', '')}({ben.get('palaceElement', '')})\n"
        "六亲:\n"
        + "\n".join(liuqin_rows)
    )


def build_liuyao_interpret_prompt(
    chart: dict[str, Any],
    yong_shen: dict[str, Any],
    excerpts: list[dict[str, str]],
    *,
    style: InterpretStyle = "professional",
) -> str:
    context = build_liuyao_chat_context(chart, yong_shen, excerpts)
    ys = yong_shen.get("yongShen", "")
    if style == "plain":
        task = (
            "请用大白话解释这次占卜对问事的启示.\n"
            f"后台以{ys}为核心参考(正文请用日常语言说明「这件事主要看什么」, "
            "不要只写用神二字).\n"
            "直接回答结果倾向与建议.\n"
            f"{plain_interpret_task_closing(380)}"
        )
    else:
        task = (
            f"请给出六爻断语摘要, 首句必须写明: 本卦以{ys}爻为用神.\n"
            "解盘理念参考《增删卜易》, 结合月建日辰、世应、动爻与生克.\n"
            "控制在 400 字以内, 不要编造典籍出处."
        )
    return f"{context}\n\n{style_mode_block(style)}\n\n{task}"


def build_liuyao_chat_context(
    chart: dict[str, Any],
    yong_shen: dict[str, Any],
    excerpts: list[dict[str, str]],
) -> str:
    ben = chart.get("benGua", {})
    bian = chart.get("bianGua")
    moving = chart.get("movingLines", [])
    lines = chart.get("lines", [])
    line_text = "\n".join(
        f"第{item['position']}爻 {item['stem']}{item['branch']} "
        f"{item['liuqin']} {item['liushen']}"
        f"{' 世' if item.get('isShi') else ''}"
        f"{' 应' if item.get('isYing') else ''}"
        f"{' 动' if item.get('isMoving') else ''}"
        for item in lines
    )
    excerpt_text = "\n".join(
        f"{idx}. [{item.get('source', '')}] {item.get('excerpt', '')}"
        for idx, item in enumerate(excerpts, start=1)
    ) or "(暂无摘录)"
    bian_text = bian.get("name", "无") if bian else "无"
    question = chart.get("input", {}).get("question", "")
    return (
        f"问事: {question}\n"
        f"本卦: {ben.get('name', '')}\n"
        f"变卦: {bian_text}\n"
        f"动爻: {moving}\n"
        f"月建: {chart.get('monthJian', '')} 日辰: {chart.get('dayChen', '')}\n"
        f"用神: {yong_shen.get('yongShen', '')} (第{yong_shen.get('position', '')}爻)\n"
        f"用神理由: {yong_shen.get('reason', '')}\n"
        f"六爻:\n{line_text}\n\n"
        f"典籍摘录:\n{excerpt_text}"
    )


def build_liuyao_chat_init_prompt(
    chart: dict[str, Any],
    yong_shen: dict[str, Any],
    excerpts: list[dict[str, str]] | None = None,
) -> str:
    context = build_liuyao_chat_context(chart, yong_shen, excerpts or [])
    return (
        f"{context}\n\n{CHAT_SCOPE_GUARDRAIL}\n\n"
        "以上是当前六爻卦象背景, 请等待用户追问."
    )
