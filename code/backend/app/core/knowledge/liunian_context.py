from __future__ import annotations

import re
from typing import Any

from app.core.knowledge.models import CompressedContext, KnowledgeHit
from app.core.knowledge.luck_chart import get_dayun_timeline
from app.core.knowledge.target_year_block import build_target_year_block
from app.core.knowledge.keys_liunian import build_liunian_lookup_keys
from app.core.knowledge.factory import get_knowledge_service
from app.core.knowledge.tiers import hit_to_public
from app.core.paipan.interactions import ZHI_CHONG, ZHI_HAI, ZHI_HE

LIUNIAN_THEME_TRIGGERS = frozenset(
    {"流年事件", "婚姻感情", "健康疾病", "官非", "职业财运"}
)


def _needs_liunian_block(
    question: str,
    options: list[str] | None = None,
    *,
    force: bool = False,
) -> bool:
    if force:
        return True
    text = question or ""
    if extract_years_from_question(text):
        return True
    if parse_virtual_age_span(text):
        return True
    keys = (
        "流年",
        "大运",
        "虚龄",
        "运程",
        "哪一年",
        "哪年",
        "那年",
        "何时",
        "岁运",
        "并临",
        "太岁",
        "年发生",
    )
    if any(k in text for k in keys):
        return True
    if options:
        from app.core.knowledge.mcq_reasoning_mode import is_year_option_mcq

        if is_year_option_mcq(options):
            return True
    from app.benchmark.contest8_rag import infer_question_theme

    if infer_question_theme(text) in LIUNIAN_THEME_TRIGGERS:
        return True
    return False


def is_liunian_event_question(question: str) -> bool:
    from app.benchmark.contest8_rag import infer_question_theme

    return infer_question_theme(question) == "流年事件" or bool(
        re.search(r"\d{4}年", question)
    )


from app.core.knowledge.luck_prompt_util import (
    extract_years_from_options,
    extract_years_from_question,
    parse_dayun_ganzhi_from_question,
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


def _dayun_overlaps_age_span(
    dy: dict[str, Any], age_span: tuple[int, int] | None
) -> bool:
    if not age_span:
        return True
    a0, a1 = age_span
    start_age = int(dy.get("startAge") or 0)
    end_age = int(dy.get("endAge") or 0)
    return not (end_age < a0 or start_age > a1)


def _dayun_matches_named_ganzhi(dy: dict[str, Any], ganzhi: str) -> bool:
    if not ganzhi:
        return True
    return str(dy.get("ganzhi") or "") == ganzhi


def _dayun_has_target_years(dy: dict[str, Any], years_wanted: set[int]) -> bool:
    if not years_wanted:
        return False
    for ln in dy.get("liunian") or []:
        if int(ln.get("year") or 0) in years_wanted:
            return True
    return False


def format_liunian_timeline(
    chart: dict[str, Any],
    question: str,
    options: list[str] | None = None,
) -> str:
    years_wanted = set(extract_years_from_question(question))
    years_wanted |= set(extract_years_from_options(options))
    age_span = parse_virtual_age_span(question)
    dayun_ganzhi = parse_dayun_ganzhi_from_question(question)
    want_named_dayun_segment = bool(age_span or dayun_ganzhi)
    lines: list[str] = []
    natal = _natal_summary(chart)
    if natal:
        lines.append(f"本命四柱: {natal}")

    for dy in get_dayun_timeline(chart):
        if not _dayun_overlaps_age_span(dy, age_span):
            continue
        if not _dayun_matches_named_ganzhi(dy, dayun_ganzhi):
            continue
        start_age = int(dy.get("startAge") or 0)
        end_age = int(dy.get("endAge") or 0)
        dy_label = (
            f"第{dy.get('index')}运 {dy.get('ganzhi')} "
            f"虚龄{start_age}-{end_age} ({dy.get('startYear')}-{dy.get('endYear')})"
        )
        show_full_segment = want_named_dayun_segment or (
            bool(years_wanted) and _dayun_has_target_years(dy, years_wanted)
        )
        ln_lines: list[str] = []
        for ln in dy.get("liunian") or []:
            year = int(ln.get("year") or 0)
            if show_full_segment:
                highlight = bool(years_wanted and year in years_wanted)
                ln_lines.append(
                    _format_liunian_row(ln, chart, highlight=highlight)
                )
            elif years_wanted:
                if year not in years_wanted:
                    continue
                ln_lines.append(
                    _format_liunian_row(ln, chart, highlight=True)
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


def format_dayun_overview(chart: dict[str, Any]) -> str:
    lines: list[str] = ["大运概览(结构化排盘):"]
    timeline = get_dayun_timeline(chart)
    if not timeline:
        return ""
    for dy in timeline:
        lines.append(
            f"- 第{dy.get('index')}运 {dy.get('ganzhi')} "
            f"虚龄{dy.get('startAge')}-{dy.get('endAge')} "
            f"({dy.get('startYear')}-{dy.get('endYear')})"
        )
    return "\n".join(lines)


def format_liunian_rules_block(question: str, chart: dict[str, Any] | None = None) -> str:
    service = get_knowledge_service()
    if not service.enabled:
        return ""
    lines: list[str] = ["【流年岁运规则】(主裁辅助, 择年/运程题必对照)"]
    for key in build_liunian_lookup_keys(question):
        rows = service.store.lookup("liunian", key)
        if not rows:
            continue
        hit = hit_to_public(rows[0])
        category = str(key.get("category") or hit.id)
        lines.append(f"- [{category}] {hit.summary}")
        if hit.claims:
            quote = str(hit.claims[0].quote or "")[:220]
            if quote:
                lines.append(f"  原文: {quote}")
    if len(lines) <= 1:
        return ""
    lines.append("须先定目标年大运, 再叠流年十神与冲合, 勿跳过本节直接猜选项.")
    if chart:
        active = str(chart.get("activeDayunGanzhi") or chart.get("activeDayun") or "")
        target_year = chart.get("targetYear")
        if active:
            lines.append(f"当前/active大运: {active}")
        if target_year:
            lines.append(f"题干目标年: {target_year}")
    return "\n".join(lines)


def _suiyun_from_judgement(judgement: dict[str, Any] | None) -> str:
    if not judgement:
        return ""
    for row in (judgement.get("arbitration") or {}).get("judgeOpinions") or []:
        if row.get("role") != "suiyun":
            continue
        summary = str(row.get("summary") or "")
        rule_ids = row.get("ruleIds") or []
        suffix = f" [ruleIds={','.join(rule_ids[:4])}]" if rule_ids else ""
        return f"判盘链岁运: {summary}{suffix}"
    return ""


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
    *,
    options: list[str] | None = None,
    judgement: dict[str, Any] | None = None,
    force: bool = False,
) -> str:
    if not _needs_liunian_block(question, options, force=force):
        return ""
    blocks: list[str] = []
    rules = format_liunian_rules_block(question, chart)
    if rules:
        blocks.append(rules)
    suiyun_line = _suiyun_from_judgement(judgement)
    if suiyun_line:
        blocks.append(suiyun_line)
    timeline = format_liunian_timeline(chart, question, options)
    if timeline:
        blocks.append(timeline)
    elif force:
        overview = format_dayun_overview(chart)
        if overview:
            blocks.append(overview)
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
