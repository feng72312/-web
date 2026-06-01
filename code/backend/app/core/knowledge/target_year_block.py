"""Structured target-year (大运/流年) inference block for contest MCQ prompts."""

from __future__ import annotations

import re
from typing import Any

from app.benchmark.contest8_rag import infer_question_theme
from app.core.knowledge.luck_chart import get_dayun_timeline
from app.core.knowledge.luck_prompt_util import extract_years_from_question
from app.core.knowledge.models import CompressedContext
from app.core.paipan.interactions import ZHI_CHONG, ZHI_HAI, ZHI_HE
from app.core.paipan.wuxing_map import gan_wuxing, zhi_wuxing

PILLAR_LABELS = {
    "year": "年柱",
    "month": "月柱",
    "day": "日柱",
    "hour": "时柱",
}

# 天干四冲 (常用)
GAN_CLASH = [
    ("甲", "庚"),
    ("乙", "辛"),
    ("丙", "壬"),
    ("丁", "癸"),
]

WUXING_KE = {
    "木": "土",
    "土": "水",
    "水": "火",
    "火": "金",
    "金": "木",
}

SHISHEN_CLUES = {
    "比肩": "同辈竞争、分财、合作波动",
    "劫财": "破财、争夺、投资失利",
    "食神": "饮食、表达、技艺、温和变动",
    "伤官": "变动、口舌、投资、不服管束",
    "偏财": "意外财、父亲、情人、浮财",
    "正财": "工资、妻子、稳定收入",
    "七杀": "压力、官非、病灾、小人",
    "正官": "工作、名誉、丈夫(女命)、官非风险",
    "偏印": "偏门学问、继母、病符",
    "正印": "母亲、学历、文书、贵人、健康调养",
}

THEME_SHISHEN_FOCUS = {
    "流年事件": ("正官", "七杀", "偏财", "正财", "伤官", "食神"),
    "婚姻感情": ("正财", "偏财", "正官", "七杀", "伤官"),
    "子女": ("食神", "伤官", "正官", "七杀"),
    "职业财运": ("正财", "偏财", "正官", "七杀", "食神", "伤官"),
    "健康疾病": ("七杀", "正官", "偏印", "正印", "伤官"),
    "官非": ("七杀", "正官", "伤官"),
    "家庭出身": ("正印", "偏印", "偏财", "正财"),
    "学历": ("正印", "偏印", "食神", "伤官"),
}


def _stem_clash(a: str, b: str) -> bool:
    for x, y in GAN_CLASH:
        if (a, b) in ((x, y), (y, x)):
            return True
    return False


def _stem_ke(a: str, b: str) -> str:
    wx_a, wx_b = gan_wuxing(a), gan_wuxing(b)
    if WUXING_KE.get(wx_a) == wx_b:
        return f"{a}克{b}"
    if WUXING_KE.get(wx_b) == wx_a:
        return f"{b}克{a}"
    return ""


def _branch_relation(a: str, b: str) -> str:
    for x, y in ZHI_CHONG:
        if (a, b) in ((x, y), (y, x)):
            return "冲"
    for x, y in ZHI_HE:
        if (a, b) in ((x, y), (y, x)):
            return "合"
    for x, y in ZHI_HAI:
        if (a, b) in ((x, y), (y, x)):
            return "害"
    if a == b:
        return "伏吟"
    return ""


def _find_dayun_for_year(chart: dict[str, Any], year: int) -> dict[str, Any] | None:
    for dy in get_dayun_timeline(chart):
        start = int(dy.get("startYear") or 0)
        end = int(dy.get("endYear") or 0)
        if start and end and start <= year <= end:
            return dy
    for dy in get_dayun_timeline(chart):
        for ln in dy.get("liunian") or []:
            if int(ln.get("year") or 0) == year:
                return dy
    return None


def _find_liunian(dy: dict[str, Any], year: int) -> dict[str, Any] | None:
    for ln in dy.get("liunian") or []:
        if int(ln.get("year") or 0) == year:
            return ln
    return None


def _resolve_year_luck(
    chart: dict[str, Any], year: int
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    dy = _find_dayun_for_year(chart, year)
    if dy:
        ln = _find_liunian(dy, year)
        if ln:
            return dy, ln
    for dy in get_dayun_timeline(chart):
        ln = _find_liunian(dy, year)
        if ln:
            return dy, ln
    return dy, None


def _natal_pillar_relations(
    chart: dict[str, Any],
    ln_gan: str,
    ln_zhi: str,
) -> list[str]:
    notes: list[str] = []
    pillars = chart.get("pillars") or {}
    day_gz = (pillars.get("day") or {}).get("ganzhi", "")
    for key, label in PILLAR_LABELS.items():
        p = pillars.get(key) or {}
        pg, pz = p.get("gan", ""), p.get("zhi", "")
        if not pg and not pz:
            continue
        parts: list[str] = []
        if pg and ln_gan:
            if _stem_clash(pg, ln_gan):
                parts.append("天干冲")
            ke = _stem_ke(pg, ln_gan)
            if ke:
                parts.append(ke)
        if pz and ln_zhi:
            rel = _branch_relation(pz, ln_zhi)
            if rel:
                parts.append(f"地支{rel}")
        if parts:
            notes.append(f"流年与{label}{pg}{pz}: {','.join(parts)}")
    if day_gz and len(day_gz) >= 2 and ln_gan and ln_zhi:
        if _stem_clash(day_gz[0], ln_gan) or _branch_relation(day_gz[1], ln_zhi) == "冲":
            notes.append("流年与日柱天克地冲或冲日, 多主重大变动或凶灾, 须结合喜忌")
    return notes


def _dayun_liunian_relation(dy_gz: str, ln_gz: str) -> list[str]:
    if not dy_gz or not ln_gz:
        return []
    notes: list[str] = []
    if dy_gz == ln_gz:
        notes.append("岁运并临(干支同), 吉凶看十神性质与喜忌")
    dg, dz = dy_gz[0], dy_gz[1] if len(dy_gz) > 1 else ""
    lg, lz = ln_gz[0], ln_gz[1] if len(ln_gz) > 1 else ""
    if dg and lg:
        ke = _stem_ke(dg, lg)
        if ke:
            notes.append(f"运干岁干: {ke}")
    if dz and lz:
        rel = _branch_relation(dz, lz)
        if rel:
            notes.append(f"运支岁支: {rel}")
    return notes


def _shishen_clues(ln_ss: str, dy_ss: str, theme: str) -> list[str]:
    lines: list[str] = []
    if ln_ss:
        hint = SHISHEN_CLUES.get(ln_ss, "")
        if hint:
            lines.append(f"流年天干十神{ln_ss}: {hint}")
    if dy_ss:
        hint = SHISHEN_CLUES.get(dy_ss, "")
        if hint:
            lines.append(f"大运天干十神{dy_ss}: {hint}")
    focus = THEME_SHISHEN_FOCUS.get(theme, ())
    if ln_ss in focus:
        lines.append(f"本题属{theme}, 流年{ln_ss}为相关十神, 优先对照含此类象意的选项")
    return lines


def _tiaohou_snippet(compressed: CompressedContext | None) -> str:
    if not compressed:
        return ""
    for hit in compressed.hits:
        if hit.topic == "tiaohou":
            text = (hit.summary or "").strip()
            if len(text) > 160:
                text = text[:160] + "..."
            return f"调候要点: {text}"
    return ""


def build_target_year_block(
    chart: dict[str, Any],
    question: str,
    compressed: CompressedContext | None = None,
) -> str:
    years = extract_years_from_question(question)
    if not years:
        return ""
    theme = infer_question_theme(question)
    lines: list[str] = [
        "目标年结构化断语(由排盘计算, 须结合选项甄别, 勿当作最终答案):",
    ]
    for year in years[:3]:
        dy, ln = _resolve_year_luck(chart, year)
        if not dy:
            lines.append(f"- {year}年: 未落入大运表, 请按起运年+虚龄换算")
            continue
        dy_p = dy.get("pillar") or {}
        dy_ss = dy_p.get("shishenGan", "")
        dy_gz = dy.get("ganzhi", "")
        lines.append(
            f"- 目标{year}年 | 大运第{dy.get('index')}运 {dy_gz} "
            f"虚龄{dy.get('startAge')}-{dy.get('endAge')} "
            f"({dy.get('startYear')}-{dy.get('endYear')}) 运干十神{dy_ss}"
        )
        if not ln:
            lines.append(f"  该年流年未在表中, 请查同运内相邻流年干支规律")
            continue
        ln_p = ln.get("pillar") or {}
        ln_ss = ln_p.get("shishenGan", "")
        ln_gz = ln.get("ganzhi", "")
        hide = ln_p.get("hideStems") or []
        lines.append(
            f"  流年 {ln_gz} 虚龄{ln.get('age')} "
            f"天干十神{ln_ss} 藏干{' '.join(hide) if hide else '无'}"
        )
        lg, lz = ln_p.get("gan", ""), ln_p.get("zhi", "")
        rels = _natal_pillar_relations(chart, lg, lz)
        for r in rels[:5]:
            lines.append(f"  {r}")
        dy_ln = _dayun_liunian_relation(dy_gz, ln_gz)
        for r in dy_ln:
            lines.append(f"  岁运: {r}")
        for c in _shishen_clues(ln_ss, dy_ss, theme):
            lines.append(f"  {c}")
    snippet = _tiaohou_snippet(compressed)
    if snippet:
        lines.append(snippet)
    lines.append(f"题型侧重: {theme}")
    return "\n".join(lines)
