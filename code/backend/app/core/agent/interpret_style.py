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
            "【深度解读】面向普通读者, 输出正式报告体.\n"
            "要求:\n"
            "- 开门见山: 首句直接进入结论, 禁止寒暄、套话、自我介绍\n"
            "- 禁止: 「好的」「咱们」「我是你的专家」等聊天式口吻\n"
            "- 用小标题分四段: 核心判断 / 关键依据 / 趋势与时机 / 行动建议\n"
            "- 用语通俗但克制; 术语少用, 必要时括号简释; 不引典籍书名; 不堆砌盘面数据\n"
            "- 全文像正式解读报告, 不要像对话回复"
        )
    return (
        "【专业解读】面向命理从业者, 输出可核对的专业判词.\n"
        "要求:\n"
        "- 结构: 总断 -> 依据 -> 趋势 -> 应期或注意点 -> 建议边界\n"
        "- 术语准确, 关键结论须对应盘面要素; 逻辑链完整\n"
        "- 可引用典籍思路但勿编造出处\n"
        "- 禁止寒暄、自我介绍、空泛鸡汤、无依据绝对化断语\n"
        "- 开门见山进入分析, 禁止铺垫句"
    )
