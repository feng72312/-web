from __future__ import annotations

import json

from app.core.agent.chat_scope import CHAT_SCOPE_GUARDRAIL
from app.core.agent.interpret_style import InterpretStyle
from app.core.agent.prompts import build_interpret_prompt
from app.core.agent.prompts_liuyao import build_liuyao_interpret_prompt
from typing import Any

_FUSION_CHART_JSON_LIMIT = 12_000
_FUSION_SUMMARY_LIMIT = 4_000

STANCE_SUFFIX = (
    "\n\n文末必须单独一行, 格式严格为: 倾向:吉 或 倾向:凶 或 倾向:平 或 倾向:未定"
)


def build_bazi_channel_prompt(
    chart: dict[str, Any],
    question: str,
    *,
    compressed=None,
    rag_excerpts: list[dict[str, str]] | None = None,
    style: InterpretStyle = "professional",
) -> str:
    base = build_interpret_prompt(
        chart,
        compressed=compressed,
        rag_excerpts=rag_excerpts,
        style=style,
    )
    return (
        f"{base}\n\n"
        f"用户问事: {question}\n"
        f"请从八字命局、大运流年角度回答, 控制在 350 字以内."
        f"{STANCE_SUFFIX}"
    )


def build_liuyao_channel_prompt(
    chart: dict[str, Any],
    yong_shen: dict[str, Any],
    excerpts: list[dict[str, str]],
    question: str,
    *,
    style: InterpretStyle = "professional",
) -> str:
    base = build_liuyao_interpret_prompt(chart, yong_shen, excerpts, style=style)
    return (
        f"{base}\n\n"
        f"问事重点: {question}\n"
        f"请就此事占断, 控制在 350 字以内."
        f"{STANCE_SUFFIX}"
    )


def parse_stance(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("倾向:"):
            value = line.split(":", 1)[-1].strip()
            if value in ("吉", "凶", "平", "未定"):
                return value
    return "未定"


def _compact_chart_json(chart_snapshot: dict[str, Any]) -> str:
    text = json.dumps(chart_snapshot or {}, ensure_ascii=False)
    if len(text) <= _FUSION_CHART_JSON_LIMIT:
        return text
    compact = {
        "input": chart_snapshot.get("input"),
        "dayMaster": chart_snapshot.get("dayMaster"),
        "meta": chart_snapshot.get("meta"),
        "moduleHint": chart_snapshot.get("moduleHint"),
        "truncated": True,
    }
    text = json.dumps(compact, ensure_ascii=False)
    return text[:_FUSION_CHART_JSON_LIMIT]


def build_fusion_chat_init_prompt(sources: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    for index, source in enumerate(sources, start=1):
        module_label = str(source.get("moduleLabel") or "").strip()
        title = str(source.get("title") or "").strip()
        module_id = str(source.get("moduleId") or "").strip()
        lines = [
            f"## 素材 {index}: {module_label} - {title}",
            f"模块标识: {module_id}",
        ]
        question = str(source.get("question") or "").strip()
        if question:
            lines.append(f"问事: {question}")
        chart_snapshot = source.get("chartSnapshot")
        if not isinstance(chart_snapshot, dict):
            chart_snapshot = {}
        lines.append(f"结构化盘面 JSON:\n{_compact_chart_json(chart_snapshot)}")
        summary_plain = str(source.get("summaryPlain") or "").strip()
        if summary_plain:
            lines.append(
                f"AI 深度解读摘要:\n{summary_plain[:_FUSION_SUMMARY_LIMIT]}"
            )
        summary_pro = str(source.get("summaryProfessional") or "").strip()
        if summary_pro:
            lines.append(
                f"命理师专用解读摘要:\n{summary_pro[:_FUSION_SUMMARY_LIMIT]}"
            )
        blocks.append("\n".join(lines))

    instruction = (
        "你是紫云命理天文馆的多盘融合顾问. 以下为用户本次选择的多个术数盘面素材. "
        "请先分别识别每个盘的体系与适用边界, 再综合分析同向点, 冲突点, 优先级与可追问方向. "
        "八字偏气运结构, 五行十神, 大运流年; 紫微偏宫位星曜, 人生领域映射; "
        "不要把不同体系硬凑为同一术语. "
        "若多个盘结论同向, 指出共同支撑; 若冲突, 说明冲突来自体系视角差异, 时间范围差异还是问事焦点差异; "
        "不要编造盘面没有的数据. "
        "用户后续追问时, 继续以结构化盘面为主, 已有 AI 摘要为辅."
    )
    body = "\n\n".join(blocks)
    return f"{instruction}\n\n{body}\n\n{CHAT_SCOPE_GUARDRAIL}"
