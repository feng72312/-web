from __future__ import annotations

from typing import Literal

InterpretStyle = Literal["professional", "plain"]


def normalize_interpret_style(raw: str | None) -> InterpretStyle:
    if (raw or "").strip().lower() == "plain":
        return "plain"
    return "professional"


def style_mode_block(style: InterpretStyle) -> str:
    if style == "plain":
        return (
            "【白话解读】读者是完全不懂命理的小白.\n"
            "要求: 用日常口语; 尽量不用术语; 若必须用则括号简短解释; "
            "直接回答问事结果、时机与建议; 不要引典籍书名; 不要堆砌盘面数据; "
            "可分段, 语气自然."
        )
    return (
        "【专业解读】读者是命理从业者.\n"
        "要求: 可使用专业术语; 结合盘面要素逐层分析; 逻辑清晰便于核对; "
        "可引用典籍思路但勿编造出处."
    )
