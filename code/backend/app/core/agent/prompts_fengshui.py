from __future__ import annotations

import json
from typing import Any

from app.core.agent.interpret_style import InterpretStyle, style_mode_block


def _direction_lines(directions: list[dict[str, Any]]) -> str:
    ji = [
        f"{row.get('label', '')} {row.get('direction', '')}({row.get('trigram', '')})"
        for row in directions
        if row.get("auspicious")
    ]
    xiong = [
        f"{row.get('label', '')} {row.get('direction', '')}({row.get('trigram', '')})"
        for row in directions
        if not row.get("auspicious")
    ]
    return f"吉方: {'、'.join(ji) or '(无)'}\n凶方: {'、'.join(xiong) or '(无)'}"


def _xuankong_lines(xk: dict[str, Any]) -> str:
    period = xk.get("period") or {}
    lines = [
        f"元运: {period.get('label', '')} ({period.get('yuan', '')})",
        f"坐向: {xk.get('label', '')}",
        f"山星{xk.get('shanFly', '')}, 向星{xk.get('xiangFly', '')}",
    ]
    combined = xk.get("combinedPan") or []
    if combined:
        grid = " | ".join(f"{row.get('palace', '')}:{row.get('label', '')}" for row in combined)
        lines.append(f"运山向合盘: {grid}")
    if xk.get("flowYear"):
        lines.append(f"流年: {xk.get('flowYear')}")
    return "\n".join(lines)


def build_fengshui_chat_context(
    chart: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    excerpts: list[dict[str, str]],
) -> str:
    inp = chart.get("input") or {}
    method = inp.get("method", "bazhai")
    scene = {"residence": "住宅", "shop": "店铺", "office": "办公室"}.get(
        inp.get("scene", ""), inp.get("scene", "")
    )
    hit_text = "\n".join(
        f"{idx}. [{hit.get('topic', '')}] {hit.get('summary', '')}"
        for idx, hit in enumerate(knowledge_hits, start=1)
    ) or "(暂无结构化节点)"
    excerpt_text = "\n".join(
        f"{idx}. [{item.get('source', '')}] {item.get('excerpt', '')}"
        for idx, item in enumerate(excerpts, start=1)
    ) or "(暂无摘录)"
    advice = chart.get("advice") or []
    parts = [
        f"问事: {inp.get('question', '')}",
        f"场景: {scene}",
        f"流派: {'玄空飞星' if method == 'xuankong' else '八宅'}",
    ]

    if method == "xuankong":
        xk = chart.get("xuankong") or {}
        parts.extend(
            [
                f"建成/入伙年: {inp.get('buildYear', '')}",
                f"流年年份: {inp.get('flowYear', '(未指定)')}",
                _xuankong_lines(xk),
            ]
        )
    else:
        ming = chart.get("mingGua") or {}
        zhai = chart.get("zhaiGua") or {}
        parts.extend(
            [
                f"出生年: {inp.get('birthYear', '')} 性别: {'男' if inp.get('gender') == 1 else '女'}",
                f"命卦: {ming.get('alias', '')} {ming.get('groupLabel', '')}",
                f"宅卦: {zhai.get('alias', '')} {zhai.get('groupLabel', '')} {zhai.get('label', '')}",
                f"人宅相配: {'是' if chart.get('compatible') else '否'}",
                _direction_lines(chart.get("directions") or []),
            ]
        )

    if advice:
        parts.append("布局建议:\n" + "\n".join(f"- {line}" for line in advice))
    parts.extend([f"结构化节点:\n{hit_text}", f"典籍摘录:\n{excerpt_text}"])
    return "\n".join(part for part in parts if part)


def build_fengshui_interpret_prompt(
    chart: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    excerpts: list[dict[str, str]],
    *,
    style: InterpretStyle = "professional",
) -> str:
    context = build_fengshui_chat_context(chart, knowledge_hits, excerpts)
    method = (chart.get("input") or {}).get("method", "bazhai")
    if method == "xuankong":
        role = "玄空飞星解读助手"
        rules = (
            "1. 先说明元运、坐向与山星/向星顺逆.\n"
            "2. 按运-山-向合盘解读各宫组合, 区分人丁(山)与财运(向).\n"
            "3. 结合用户问事给出布局建议, 注明需现场核实之处.\n"
            "4. 不编造未给出的峦头细节.\n"
        )
    else:
        role = "八宅风水解读助手"
        rules = (
            "1. 先说明命卦、宅卦与人宅是否相配.\n"
            "2. 分别说明四大吉方与四凶方在卧室、大门、灶位上的取用.\n"
            "3. 结合用户问事给出可操作的布局建议, 避免空泛.\n"
            "4. 不编造典籍未支持的具体峦头细节; 不确定处请说明.\n"
        )
    return (
        f"你是{role}, 请基于以下排盘结果与典籍摘录作答.\n"
        f"要求:\n{rules}"
        f"{style_mode_block(style)}\n"
        f"排盘上下文:\n{context}"
    )


def build_fengshui_chat_init_prompt(
    chart: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    excerpts: list[dict[str, str]],
) -> str:
    context = build_fengshui_chat_context(chart, knowledge_hits, excerpts)
    method = (chart.get("input") or {}).get("method", "bazhai")
    focus = "玄空飞星运山向" if method == "xuankong" else "八宅吉凶方位与人宅匹配"
    return (
        f"你是风水对话助手, 已加载以下排盘与典籍上下文.\n"
        f"后续回答请紧扣{focus}, 可追问具体房间或坐向.\n"
        f"上下文:\n{context}\n"
        f"结构化节点 JSON:\n{json.dumps(knowledge_hits, ensure_ascii=False)}"
    )
