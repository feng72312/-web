from __future__ import annotations

import json
from typing import Any

from app.core.agent.interpret_style import InterpretStyle, style_mode_block
from app.core.agent.prompts_fusion import STANCE_SUFFIX


def _case_lines(cases: list[dict[str, Any]]) -> str:
    if not cases:
        return "(\u6682\u65e0\u5360\u9a8c\u8bfe\u4f8b)"
    lines = []
    for idx, case in enumerate(cases, start=1):
        cond = case.get("conditions") or {}
        lines.append(
            f"{idx}. [{case.get('questionType', '')}] "
            f"\u5bab{cond.get('palace', '')} \u661f{cond.get('starIds', [])} "
            f"\u65ad: {case.get('verdict', '')}"
        )
    return "\n".join(lines)


def build_xingming_chat_context(
    chart: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    excerpts: list[dict[str, str]],
    cases: list[dict[str, Any]],
    cross_charts: dict[str, Any] | None = None,
) -> str:
    inp = chart.get("input") or {}
    hit_text = "\n".join(
        f"{idx}. [{hit.get('topic', '')}] {hit.get('summary', '')}"
        for idx, hit in enumerate(knowledge_hits, start=1)
    ) or "(\u6682\u65e0\u8282\u70b9)"
    excerpt_text = "\n".join(
        f"{idx}. [{item.get('source', '')}] {item.get('excerpt', '')}"
        for idx, item in enumerate(excerpts, start=1)
    ) or "(\u6682\u65e0\u6458\u5f55)"
    body_lines = "\n".join(
        f"{b.get('label', '')} {b.get('mansion', '')}\u5bbf "
        f"{b.get('longitude', '')}\u5ea6 \u843d{b.get('palace', '')}"
        for b in chart.get("bodies") or []
    )
    parts = [
        f"\u95ee\u4e8b: {inp.get('question', '')}",
        f"\u771f\u592a\u9633\u65f6: {chart.get('trueSolarTime', '')}",
        f"\u56db\u67f1: {json.dumps(chart.get('fourPillars', {}), ensure_ascii=False)}",
        f"\u547d\u5bab: {json.dumps(chart.get('mingPalace', {}), ensure_ascii=False)}",
        f"\u592a\u5c81\u9650\u8fd0: {json.dumps(chart.get('limits', {}), ensure_ascii=False)}",
        f"\u4e03\u653f\u56db\u4f59:\n{body_lines}",
        f"\u5360\u9a8c\u8bfe\u4f8b:\n{_case_lines(cases)}",
        f"\u8282\u70b9:\n{hit_text}",
        f"\u5178\u7c4d:\n{excerpt_text}",
    ]
    if cross_charts:
        if cross_charts.get("baziChart"):
            dm = (cross_charts["baziChart"].get("dayMaster") or {}).get("gan", "")
            parts.append(f"\u5b50\u5e73\u65e5\u4e3b\u53c2\u8003: {dm}")
        if cross_charts.get("ziweiChart"):
            palaces = cross_charts["ziweiChart"].get("palaces") or []
            if palaces:
                major = palaces[0].get("majorStars") or []
                names = "\u3001".join(s.get("name", "") for s in major)
                parts.append(f"\u7d2b\u5fae\u547d\u5bab\u53c2\u8003: {names}")
    return "\n".join(parts)


def build_xingming_interpret_prompt(
    chart: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    excerpts: list[dict[str, str]],
    cases: list[dict[str, Any]],
    *,
    cross_charts: dict[str, Any] | None = None,
    style: InterpretStyle = "professional",
) -> str:
    context = build_xingming_chat_context(
        chart, knowledge_hits, excerpts, cases, cross_charts
    )
    if style == "plain":
        task = (
            "\u8bf7\u7528\u767d\u8bdd\u6309\u679c\u8001\u661f\u547d\u8bba\u547d\u5bab\u4e03\u653f\u56db\u4f59\u4e0e\u592a\u5c81\u9650\u8fd0."
            "\u5148\u5f15\u5360\u9a8c\u8bfe\u4f8b\u6216\u5178\u7c4d\u6458\u5f55\uff0c\u518d\u8bba\u76d8\u3002"
            "\u65e0\u8bfe\u4f8b\u5339\u914d\u987b\u6807\u660e\u63a8\u6d4b\u3002\u4e0d\u7f16\u9020\u5e94\u9a8c\u3002\u7ea6 500 \u5b57."
        )
    else:
        task = (
            "\u8bf7\u6309\u679c\u8001\u661f\u5b97\u4e03\u653f\u56db\u4f59\u89e3\u8bfb\u547d\u5bab\u3001\u592a\u5c81\u4e0e\u9650\u8fd0\u3002"
            "\u5fc5\u987b\u5148\u5f15\u5360\u9a8c\u8bfe\u4f8b/\u5178\u7c4d\uff0c\u518d\u7ed3\u5408\u661f\u4f4d\u3002"
            "\u4e0e\u7d2b\u5fae\u3001\u5b50\u5e73\u53c2\u8003\u5206\u5217\u89c6\u89d2\uff0c\u52ff\u6b66\u65ad\u5408\u5e76\u3002\u7ea6 600 \u5b57."
        )
    return f"{context}\n\n{style_mode_block(style)}\n\n{task}{STANCE_SUFFIX}"


def build_xingming_chat_init_prompt(
    chart: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    excerpts: list[dict[str, str]],
    cases: list[dict[str, Any]],
    cross_charts: dict[str, Any] | None = None,
) -> str:
    return (
        "\u4f60\u662f\u661f\u547d\u5360\u9a8c(\u679c\u8001\u4e03\u653f\u56db\u4f59)\u52a9\u624b\u3002"
        "\u4ec5\u4f9d\u636e\u4e0b\u65b9\u547d\u76d8\u4e0e\u5360\u9a8c\u8bfe\u4f8b\u56de\u7b54\uff0c\u4e0d\u7f16\u9020\u661f\u4f4d\u3002\n\n"
        + build_xingming_chat_context(chart, knowledge_hits, excerpts, cases, cross_charts)
    )
