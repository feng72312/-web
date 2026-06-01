from __future__ import annotations

import re
from typing import Any

from app.core.knowledge.models import CompressedContext, KnowledgeHit
from app.core.knowledge.luck_chart import get_dayun_timeline
from app.core.knowledge.target_year_block import build_target_year_block
from app.core.paipan.interactions import ZHI_CHONG, ZHI_HAI, ZHI_HE

def _needs_liunian_block(question: str) -> bool:
    text = question or ""
    if extract_years_from_question(text):
        return True
    keys = (
        "流年",
        "大运",
        "虚龄",
        "运程",
        "哪一年",
        "何时",
        "岁运",
        "并临",
        "太岁",
        "年发生",
    )
    return any(k in text for k in keys)


def is_liunian_event_question(question: str) -> bool:
    from app.benchmark.contest8_rag import infer_question_theme

    return infer_question_theme(question) == "流年事件" or bool(
        re.search(r"\d{4}年", question)
    )


from app.core.knowledge.luck_prompt_util import (
    extract_years_from_question,
    parse_virtual_age_span,
)


def _natal_summary(chart: dict[str, Any]) -> str:
    pillars = chart.get("pillars") or {}
    parts = []
    for key in ("year", "month", "day", "hour"):
        p = pillars.get(key) or {}
        gz = p.get("ganzhi", "")
        ss = p.get("shishenGan", "")
        if gz:
            parts.append(f"{key}柱{gz}({ss})")
    return " ".join(parts) if parts else ""


def _natal_zhi_set(chart: dict[str, Any]) -> set[str]:
    pillars = chart.get("pillars") or {}
    out: set[str] = set()
    for key in ("year", "month", "day", "hour"):
        zhi = (pillars.get(key) or {}).get("zhi", "")
        if zhi:
            out.add(zhi)
    return out


def _liunian_vs_natal(chart: dict[str, Any], ganzhi: str) -> str:
    if len(ganzhi) < 2:
        return ""
    ln_zhi = ganzhi[1]
    natal = _natal_zhi_set(chart)
    if ln_zhi not in natal:
        notes: list[str] = []
        for a, b in ZHI_CHONG:
            if ln_zhi in (a, b) and (a in natal or b in natal):
                notes.append("冲本命")
                break
        for a, b in ZHI_HE:
            if ln_zhi in (a, b) and (a in natal or b in natal):
                notes.append("合本命")
                break
        for a, b in ZHI_HAI:
            if ln_zhi in (a, b) and (a in natal or b in natal):
                notes.append("害本命")
                break
        return " ".join(notes)
    return "伏吟支"


def _format_liunian_row(
    ln: dict[str, Any],
    chart: dict[str, Any],
    *,
    highlight: bool = False,
) -> str:
    pillar = ln.get("pillar") or {}
    ss = pillar.get("shishenGan") or ""
    hide = pillar.get("hideStems") or []
    hide_txt = " ".join(hide) if hide else ""
    year = ln.get("year")
    gz = ln.get("ganzhi", "")
    rel = _liunian_vs_natal(chart, gz) if highlight else ""
    rel_txt = f" {rel}" if rel else ""
    prefix = ">>" if highlight else "  "
    return f"{prefix}{year} {gz} 天干十神{ss} 藏干{hide_txt}{rel_txt}"


def format_liunian_timeline(chart: dict[str, Any], question: str) -> str:
    years_wanted = set(extract_years_from_question(question))
    age_span = parse_virtual_age_span(question)
    lines: list[str] = []
    natal = _natal_summary(chart)
    if natal:
        lines.append(f"本命四柱: {natal}")

    for dy in get_dayun_timeline(chart):
        start_age = int(dy.get("startAge") or 0)
        end_age = int(dy.get("endAge") or 0)
        in_age_span = False
        if age_span:
            a0, a1 = age_span
            in_age_span = not (end_age < a0 or start_age > a1)
        dy_label = (
            f"第{dy.get('index')}运 {dy.get('ganzhi')} "
            f"虚龄{start_age}-{end_age} ({dy.get('startYear')}-{dy.get('endYear')})"
        )
        ln_lines: list[str] = []
        for ln in dy.get("liunian") or []:
            year = int(ln.get("year") or 0)
            if years_wanted and year not in years_wanted:
                if not age_span or not in_age_span:
                    continue
            if age_span and not in_age_span:
                continue
            if years_wanted or age_span:
                highlight = bool(years_wanted and year in years_wanted)
                ln_lines.append(
                    _format_liunian_row(ln, chart, highlight=highlight)
                )
            elif len(ln_lines) < 3:
                ln_lines.append(_format_liunian_row(ln, chart))
        if ln_lines:
            lines.append(dy_label)
            lines.extend(ln_lines)

    if not lines and get_dayun_timeline(chart):
        lines.append("(请用大运起运年+虚龄换算题干年份, 查表中对应流年干支与十神)")
    if not lines:
        return ""
    return "流年时间轴(结构化排盘, 必用):\n" + "\n".join(lines)


def format_liunian_knowledge_hits(hits: list[KnowledgeHit]) -> str:
    parts: list[str] = []
    dayun_rows = [h for h in hits if h.topic == "dayun"]
    if dayun_rows:
        parts.append("大运判断要点(知识图谱):")
        for hit in dayun_rows:
            cat = (hit.lookupKey or {}).get("category") or hit.id
            parts.append(f"- [{cat}] {hit.summary}")
    ln_rows = [h for h in hits if h.topic == "liunian"]
    if ln_rows:
        parts.append("流年判断要点(知识图谱):")
        for hit in ln_rows:
            cat = (hit.lookupKey or {}).get("category") or hit.id
            parts.append(f"- [{cat}] {hit.summary}")
    return "\n".join(parts)


def load_liunian_fewshot() -> list[dict[str, Any]]:
    from pathlib import Path
    import json

    path = Path(__file__).resolve().parents[3] / "data" / "contest8_fewshot_liunian.json"
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("examples") or data if isinstance(data, list) else [])


def build_liunian_prompt_block(
    chart: dict[str, Any],
    question: str,
    compressed: CompressedContext | None = None,
) -> str:
    if not _needs_liunian_block(question):
        return ""
    blocks: list[str] = []
    timeline = format_liunian_timeline(chart, question)
    if timeline:
        blocks.append(timeline)
    target_block = build_target_year_block(chart, question, compressed)
    if target_block:
        blocks.append(target_block)
    if compressed:
        text = format_liunian_knowledge_hits(compressed.hits)
        if text:
            blocks.append(text)
    if not blocks:
        return ""
    return "\n\n".join(blocks)
