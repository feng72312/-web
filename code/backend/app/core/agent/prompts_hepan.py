from __future__ import annotations

import json
from typing import Any

from app.core.agent.interpret_style import InterpretStyle, style_mode_block
from app.core.hepan.scene import SCENE_LABELS


def _hepan_style_mode_block(style: InterpretStyle) -> str:
    if style == "plain":
        return (
            "【白话解读】面向普通读者, 输出合盘报告体.\n"
            "要求:\n"
            "- 开门见山: 首句直接进入「契合点」正文, 禁止寒暄、套话、自我介绍、角色说明\n"
            "- 禁止出现: 「好的」「没问题」「我是你的…专家」「咱们」「这次用的是…术数」"
            "「不整那些虚头巴脑」等聊天式开场\n"
            "- 用小标题分三段: 契合点 / 需注意 / 相处或合作建议\n"
            "- 用语通俗但克制; 术语少用, 必要时括号简释; 不引典籍书名; 不堆砌盘面数据\n"
            "- 全文像正式解读报告, 不要像对话回复"
        )
    return (
        f"{style_mode_block(style)}\n"
        "- 开门见山进入分析, 禁止寒暄、自我介绍、说明所用术数等铺垫句"
    )


def _format_cross_notes(notes: list[dict[str, Any]]) -> str:
    if not notes:
        return "(\u65e0\u7ed3\u6784\u5316\u8981\u70b9)"
    lines: list[str] = []
    for idx, note in enumerate(notes, start=1):
        level = note.get("level", "")
        title = note.get("title", "")
        detail = note.get("detail", "")
        lines.append(f"{idx}. [{level}] {title}: {detail}")
    return "\n".join(lines)


def _format_excerpts(excerpts: list[dict[str, str]]) -> str:
    if not excerpts:
        return "(\u6682\u65e0\u6458\u5f55)"
    return "\n".join(
        f"{idx}. [{item.get('source', '')}] {item.get('excerpt', '')}"
        for idx, item in enumerate(excerpts, start=1)
    )


def _person_brief(hepan: dict[str, Any], key: str, label: str) -> str:
    person = hepan.get(key) or {}
    bazi = person.get("baziChart") or {}
    pillars = bazi.get("pillars") or {}
    day = pillars.get("day") or {}
    inp = bazi.get("input") or {}
    gender = "\u7537" if int(inp.get("gender", 1)) == 1 else "\u5973"
    name = person.get("name") or label
    ziwei = person.get("ziweiChart") or {}
    meta = ziwei.get("meta") or {}
    ziwei_line = ""
    if meta:
        ziwei_line = (
            f" \u5c40{meta.get('bureau', '')} "
            f"\u547d\u4e3b{meta.get('soul', '')}"
        )
    return (
        f"{name}({gender}) "
        f"\u65e5\u4e3b{bazi.get('dayMaster', '')} "
        f"\u65e5\u67f1{day.get('ganzhi', '')}"
        f"{ziwei_line}"
    )


def build_hepan_context(
    hepan: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    excerpts: list[dict[str, str]],
) -> str:
    scene = hepan.get("scene", "")
    discipline = hepan.get("discipline", "")
    scene_label = SCENE_LABELS.get(scene, scene)
    hit_text = "\n".join(
        f"{idx}. [{hit.get('topic', '')}] {hit.get('summary', '')}"
        for idx, hit in enumerate(knowledge_hits, start=1)
    ) or "(\u6682\u65e0\u8282\u70b9)"
    label_a = "\u7532"
    label_b = "\u4e59"
    parts = [
        f"\u573a\u666f: {scene_label}",
        f"\u672f\u6570: {discipline}",
        f"\u95ee\u4e8b: {hepan.get('question', '')}",
        f"\u7532\u65b9: {_person_brief(hepan, 'personA', label_a)}",
        f"\u4e59\u65b9: {_person_brief(hepan, 'personB', label_b)}",
        f"\u6807\u7b7e: {', '.join(hepan.get('summaryTags') or [])}",
        f"\u5408\u76d8\u8981\u70b9:\n{_format_cross_notes(hepan.get('crossNotes') or [])}",
        f"\u8282\u9009\u6458\u5f55:\n{_format_excerpts(excerpts)}",
        f"\u7ed3\u6784\u5316\u8282\u70b9:\n{hit_text}",
    ]
    return "\n".join(parts)


def build_hepan_interpret_prompt(
    hepan: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    excerpts: list[dict[str, str]],
    *,
    style: InterpretStyle = "professional",
) -> str:
    context = build_hepan_context(hepan, knowledge_hits, excerpts)
    discipline = hepan.get("discipline", "bazi")
    discipline_label = "\u516b\u5b57" if discipline == "bazi" else "\u7d2b\u5fae\u6597\u6570"
    scene_label = SCENE_LABELS.get(hepan.get("scene", ""), "")
    if style == "plain":
        task = (
            f"请基于下列合盘要点, 用白话写{scene_label}合盘解读.\n"
            f"首句直接从「契合点」开始写, 不要任何开场白.\n"
            f"术数({discipline_label})已在后台确定, 正文不必再说明."
        )
    else:
        task = (
            f"请基于下列合盘要点, 按{discipline_label}合盘思路论述.\n"
            "首句直接进入分析, 不要开场白."
        )
    return (
        f"{_hepan_style_mode_block(style)}\n"
        "\u8981\u6c42:\n"
        "1. \u5fc5\u987b\u57fa\u4e8e\u5408\u76d8\u8981\u70b9\u8bba\u8ff0, \u4e0d\u5f97\u7f16\u9020\u76d8\u5916\u4e8b\u5b9e.\n"
        "2. \u5206\u4e09\u6bb5: \u5951\u5408\u70b9 / \u9700\u6ce8\u610f / \u76f8\u5904\u6216\u5408\u4f5c\u5efa\u8bae.\n"
        "3. \u907f\u514d\u7edd\u5bf9\u5316\u7ed3\u8bba(\u5982\u5fc5\u5b9a\u79bb\u5a5a).\n\n"
        f"{task}\n\n"
        f"{context}"
    )


def build_hepan_chat_init_prompt(
    hepan: dict[str, Any],
    knowledge_hits: list[dict[str, Any]],
    excerpts: list[dict[str, str]],
) -> str:
    context = build_hepan_context(hepan, knowledge_hits, excerpts)
    return (
        "\u4f60\u662f\u5408\u76d8\u5206\u6790\u52a9\u624b, \u5df2\u52a0\u8f7d\u4ee5\u4e0b\u53cc\u4eba\u5408\u76d8\u4e0a\u4e0b\u6587.\n"
        "\u56de\u7b54\u65f6\u4ec5\u57fa\u4e8e\u5df2\u7ed9\u76d8\u8c61\u4e0e\u8981\u70b9, \u53ef\u8ffd\u95ee\u7ec6\u8282.\n\n"
        f"{context}\n\n"
        f"\u539f\u59cb\u6570\u636e\u6458\u8981:\n{json.dumps({'summaryTags': hepan.get('summaryTags')}, ensure_ascii=False)}"
    )
