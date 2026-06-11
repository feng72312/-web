from __future__ import annotations

from typing import Any

from app.core.agent.chat_scope import CHAT_SCOPE_GUARDRAIL
from app.core.agent.interpret_style import (
    InterpretStyle,
    plain_interpret_task_closing,
    style_mode_block,
)


def _card_lines(cards: list[dict[str, Any]]) -> str:
    rows: list[str] = []
    for card in cards:
        orient = "逆位" if card.get("orientation") == "reversed" else "正位"
        rows.append(
            f"位置{card.get('position', '')} {card.get('positionLabel', '')} "
            f"({card.get('positionMeaning', '')}): "
            f"{card.get('nameZh', '')}/{card.get('nameEn', '')} [{orient}] "
            f"牌义: {(card.get('meaningZh') or card.get('meaningEn') or '')[:200]}"
        )
    return "\n".join(rows) or "(无牌)"


def build_tarot_chat_context(
    reading: dict[str, Any],
    excerpts: list[dict[str, str]],
) -> str:
    question = reading.get("input", {}).get("question", "")
    deck = reading.get("deckName") or reading.get("deck", "")
    spread = reading.get("spreadName") or reading.get("spreadId", "")
    excerpt_text = "\n".join(
        f"{idx}. [{item.get('source', '')}] {item.get('excerpt', '')}"
        for idx, item in enumerate(excerpts, start=1)
    ) or "(暂无摘录)"
    thoth_note = ""
    if reading.get("deck") == "thoth":
        thoth_note = (
            "\n注意: 托特牌面图像受版权保护, 本平台仅提供文字牌义解读.\n"
        )
    return (
        f"问事: {question}\n"
        f"牌系: {deck}\n"
        f"牌阵: {spread}\n"
        f"{thoth_note}\n"
        f"抽牌结果:\n{_card_lines(reading.get('cards') or [])}\n\n"
        f"典籍摘录:\n{excerpt_text}"
    )


def build_tarot_interpret_prompt(
    reading: dict[str, Any],
    excerpts: list[dict[str, str]],
    *,
    style: InterpretStyle = "professional",
) -> str:
    context = build_tarot_chat_context(reading, excerpts)
    spread = reading.get("spreadName") or reading.get("spreadId", "")
    if style == "plain":
        task = (
            f"请用大白话给出塔罗占卜摘要, 基于{spread}各位置牌义.\n"
            "把每张牌的意思翻译成生活语言, 直接回答问事的核心启示、风险与建议.\n"
            "不要编造典籍出处, 不要堆砌牌名列表.\n"
            f"{plain_interpret_task_closing(420)}"
        )
    else:
        task = (
            f"请给出专业塔罗解读摘要, 基于{spread}逐位分析牌与牌之间的关联.\n"
            "结合正逆位、位置语义与问事语境, 给出可操作的判断.\n"
            "控制在 450 字以内, 不要编造典籍出处."
        )
    return f"{context}\n\n{style_mode_block(style)}\n\n{task}"


def build_tarot_chat_init_prompt(
    reading: dict[str, Any],
    excerpts: list[dict[str, str]] | None = None,
) -> str:
    context = build_tarot_chat_context(reading, excerpts or [])
    return (
        f"{context}\n\n{CHAT_SCOPE_GUARDRAIL}\n\n"
        "以上是当前塔罗牌阵背景, 请等待用户追问."
    )
