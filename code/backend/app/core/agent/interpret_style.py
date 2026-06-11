from __future__ import annotations

from typing import Literal

InterpretStyle = Literal["professional", "plain"]


def normalize_interpret_style(raw: str | None) -> InterpretStyle:
    if (raw or "").strip().lower() == "plain":
        return "plain"
    return "professional"


def plain_interpret_task_closing(max_chars: int = 400) -> str:
    return (
        "读者未必懂命理术语, 但期待简洁专业的解读报告.\n"
        "术语出现时必须附一句白话释义; 禁止罗列盘面原始数据.\n"
        f"全文控制在 {max_chars} 字以内, 避免冗长段落."
    )


def style_mode_block(style: InterpretStyle) -> str:
    if style == "plain":
        return (
            "【AI深度解读】面向普通读者的简洁专业报告.\n"
            "写作目标: 结构清晰、用语简练、结论明确, 兼顾可读与专业感.\n"
            "要求:\n"
            "- 必须严格按以下四段输出, 每段标题单独一行, 使用 markdown 三级标题:\n"
            "  ### 总断\n"
            "  ### 依据\n"
            "  ### 趋势\n"
            "  ### 建议\n"
            "- 总断: 仅 1 句, 直接给出判断与倾向\n"
            "- 依据: 2-3 句或 2-3 条要点, 说明关键卦理/命理逻辑(术语须附白话释义)\n"
            "- 趋势: 2-3 句, 写近期可能走向与主要变数\n"
            "- 建议: 2-4 条短句, 用「- 」列表列出可执行建议\n"
            "- 禁止: 寒暄、套话、聊天口吻(如「好的」「咱们」「我是专家」)\n"
            "- 禁止: 引典籍书名, 堆砌干支/星曜/爻位/宫位等原始盘面数据\n"
            "- 把盘面信息翻译成时机、风险与行动建议, 不要复述盘面结构\n"
            "- 语气稳重简练, 像咨询报告摘要, 不要像对话回复\n"
            "- 禁止免责声明、娱乐参考、AI生成等结尾套话"
        )
    return (
        "【专业解读】面向命理从业者, 输出可核对的专业判词.\n"
        "要求:\n"
        "- 结构: 总断 -> 依据 -> 趋势 -> 应期或注意点 -> 建议边界\n"
        "- 术语准确, 关键结论须对应盘面要素; 逻辑链完整\n"
        "- 可引用典籍思路但勿编造出处\n"
        "- 禁止寒暄、自我介绍、空泛鸡汤、无依据绝对化断语\n"
        "- 开门见山进入分析, 禁止铺垫句\n"
        "- 禁止免责声明、娱乐参考、AI生成等结尾套话"
    )
