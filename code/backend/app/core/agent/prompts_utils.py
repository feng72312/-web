from __future__ import annotations

from typing import Any

from app.core.agent.interpret_style import plain_interpret_task_closing, style_mode_block

_OUTPUT_RULES = (
    "输出要求: 可用 Markdown(### 小标题、**加粗**、> 引用). "
    "不要输出 --- 分割线. "
    "不要提及任何 AI 模型、服务商或「以上内容由…生成」类免责声明.\n"
)


def _excerpt_block(excerpts: list[dict[str, str]]) -> str:
    if not excerpts:
        return "(无典籍摘录)"
    lines = []
    for index, row in enumerate(excerpts[:6], start=1):
        source = row.get("source") or row.get("file_name") or ""
        text = (row.get("text") or row.get("content") or row.get("excerpt") or "").strip()
        lines.append(f"{index}. [{source}] {text[:400]}")
    return "\n".join(lines)


def _utils_style_block(style: str | None) -> str:
    if style == "plain":
        return f"\n{style_mode_block('plain')}\n{plain_interpret_task_closing(380)}\n"
    return ""


def build_zhuge_interpret_prompt(
    result: dict[str, Any],
    excerpts: list[dict[str, str]],
    *,
    style: str | None = None,
) -> str:
    style_hint = "零基础大白话" if style == "plain" else "专业"
    return (
        f"你是诸葛神数解读助手, 用{style_hint}语气.\n"
        "规则: 不得修改签号; 先引签文原文, 再结合问事给建议.\n\n"
        f"报字: {result.get('chars', '')}\n"
        f"签号: {result.get('qianNo', '')}\n"
        f"签文: {result.get('qianText', '')}\n\n"
        f"典籍摘录:\n{_excerpt_block(excerpts)}\n"
        f"{_utils_style_block(style)}"
        f"{_OUTPUT_RULES}"
    )


def build_jiemeng_interpret_prompt(
    dream: str,
    matches: list[dict[str, str]],
    excerpts: list[dict[str, str]],
    *,
    style: str | None = None,
) -> str:
    style_hint = "零基础大白话" if style == "plain" else "专业"
    match_lines = "\n".join(
        f"- [{m.get('section', '')}] {m.get('text', '')}" for m in matches[:6]
    ) or "(无条目匹配)"
    return (
        f"你是周公解梦解读助手, 用{style_hint}语气.\n"
        "规则: 优先依据匹配条目与典籍摘录, 勿编造未出现的断语.\n\n"
        f"梦境描述: {dream}\n\n"
        f"条目匹配:\n{match_lines}\n\n"
        f"典籍摘录:\n{_excerpt_block(excerpts)}\n"
        f"{_utils_style_block(style)}"
        f"{_OUTPUT_RULES}"
    )


def build_cewen_interpret_prompt(
    chars: str,
    question: str,
    excerpts: list[dict[str, str]],
    *,
    style: str | None = None,
) -> str:
    style_hint = "零基础大白话" if style == "plain" else "专业"
    return (
        f"你是测字解读助手, 依《测字秘牒》体例, 用{style_hint}语气.\n"
        "规则: 结合字形象意与典籍摘录, 一事一测, 勿断言铁板神数.\n\n"
        f"所测字: {chars}\n"
        f"问事: {question or '(未填)'}\n\n"
        f"典籍摘录:\n{_excerpt_block(excerpts)}\n"
        f"{_utils_style_block(style)}"
        f"{_OUTPUT_RULES}"
    )


def _naming_analysis_block(analysis: dict[str, Any]) -> str:
    lines = [f"全名: {analysis.get('fullName', '')}"]
    wuge = analysis.get("wuge") or {}
    for row in wuge.get("grids") or []:
        lines.append(
            f"- {row.get('grid', '')}: {row.get('strokes', '')} "
            f"({row.get('wuxing', '')}/{row.get('luck', '')})"
        )
    profile = analysis.get("baziProfile") or {}
    if profile:
        lines.append(
            f"八字: 日主{profile.get('dayMasterWuxing', '')} "
            f"{profile.get('strength', '')}, "
            f"宜补 {', '.join(profile.get('favoredWuxing') or [])}, "
            f"忌偏 {', '.join(profile.get('avoidWuxing') or [])}"
        )
    for row in analysis.get("charWuxing") or []:
        wx = row.get("radicalWuxing") or "未详"
        lines.append(f"- {row.get('char', '')} 部首五行 {wx}")
    shuowen = analysis.get("shuowen") or []
    for row in shuowen[:8]:
        ch = row.get("char", "")
        exp = (row.get("explanation") or "").strip()
        if ch and exp:
            lines.append(f"- 《说文》{ch}: {exp[:120]}")
    return "\n".join(lines) or "(无结构化分析)"


def build_naming_interpret_prompt(
    analysis: dict[str, Any],
    question: str,
    excerpts: list[dict[str, str]],
    *,
    style: str | None = None,
) -> str:
    style_hint = "零基础大白话" if style == "plain" else "专业"
    return (
        f"你是传统姓名学顾问, 用{style_hint}语气.\n"
        "规则: 结合《说文解字》《释名》等典籍摘录, 五格数理, 字义音形与八字喜忌(若有), "
        "给出取名或评名建议. 勿编造典籍未出现的断语, 勿绝对化吉凶.\n\n"
        f"问事: {question or '请综合评析此名并给出优化建议'}\n\n"
        f"结构化分析:\n{_naming_analysis_block(analysis)}\n\n"
        f"典籍摘录:\n{_excerpt_block(excerpts)}\n"
        f"{_utils_style_block(style)}"
        f"{_OUTPUT_RULES}"
    )
