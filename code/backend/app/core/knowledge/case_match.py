from __future__ import annotations

import re
from typing import Any

from app.core.knowledge.luck_chart import resolve_active_dayun, resolve_target_year

QUESTION_EVENT_TAGS = {
    "婚": "marriage",
    "嫁": "marriage",
    "妻": "marriage",
    "夫": "marriage",
    "恋": "marriage",
    "财": "wealth",
    "富": "wealth",
    "官": "career",
    "职": "career",
    "业": "career",
    "病": "health",
    "疾": "health",
    "灾": "disaster",
    "祸": "disaster",
    "丧": "bereavement",
    "死": "bereavement",
    "子": "children",
    "女": "children",
    "运": "luck_change",
    "流年": "luck_change",
    "大运": "luck_change",
    "父": "family",
    "母": "family",
    "家": "family",
    "出身": "family",
    "学": "education",
    "读": "education",
    "考": "education",
}

THEME_EVENT_TAGS = {
    "婚姻感情": ("marriage",),
    "子女": ("children",),
    "职业财运": ("wealth", "career"),
    "学历": ("education", "career", "luck_change"),
    "健康疾病": ("health", "disaster"),
    "官非": ("disaster", "career"),
    "田宅": ("wealth",),
    "家庭出身": ("family", "children"),
    "流年事件": ("luck_change",),
    "性格外貌": (),
    "综合": (),
}

BINARY_MARKERS = ("PK\x03\x04", "\u0011\u001a", "_rels/")
CATALOG_MARKERS = ("目录", "ISBN", "出版者", "印刷者", "丛书", "内部资料严禁外传")
CASE_OPENERS = ("乾造", "坤造", "乾造：", "坤造：")
GANZHI_RE = re.compile(r"([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])")


def is_binary_garbage(text: str) -> bool:
    sample = str(text or "")[:500]
    if not sample.strip():
        return True
    for marker in BINARY_MARKERS:
        if marker in sample:
            return True
    ctrl = sum(1 for ch in sample if ord(ch) < 32 and ch not in "\n\r\t")
    if ctrl > max(len(sample) * 0.05, 3):
        return True
    printable = sum(1 for ch in sample if ch.isprintable() or ch in "\n\r\t")
    return printable / max(len(sample), 1) < 0.7


def is_catalog_case(row: dict[str, Any]) -> bool:
    verdict = str(row.get("verdict") or "")
    sample = verdict[:1200]
    if not sample.strip():
        return True
    has_case_opener = any(token in sample for token in CASE_OPENERS)
    if has_case_opener:
        return False
    catalog_hits = sum(1 for marker in CATALOG_MARKERS if marker in sample)
    if catalog_hits >= 2:
        return True
    if "目" in sample[:80] and "录" in sample[:120] and not has_case_opener:
        return True
    observed = str(row.get("observedEvent") or "").strip()
    if observed and observed.isdigit():
        return True
    if re.fullmatch(r"[\W\d_]{3,}", observed or ""):
        return True
    return False


def is_applicable_case(row: dict[str, Any]) -> bool:
    if row.get("doNotApplyReason"):
        return False
    if is_binary_garbage(str(row.get("verdict") or "")):
        return False
    if is_catalog_case(row):
        return False
    tags = row.get("structureTags") or []
    event_tags = row.get("eventTags") or []
    if not tags and not event_tags and not row.get("observedEvent"):
        return False
    return True


def question_event_tags(question: str) -> list[str]:
    text = str(question or "")
    tags: list[str] = []
    for key, value in QUESTION_EVENT_TAGS.items():
        if key in text and value not in tags:
            tags.append(value)
    return tags


def theme_event_tags(chart: dict[str, Any]) -> list[str]:
    meta = chart.get("benchmarkMeta") or {}
    theme = str(meta.get("questionTheme") or "").strip()
    tags: list[str] = []
    for tag in THEME_EVENT_TAGS.get(theme, ()):
        if tag not in tags:
            tags.append(tag)
    return tags


def chart_pillar_key(chart: dict[str, Any]) -> str:
    pillars = chart.get("pillars") or {}
    parts: list[str] = []
    for key in ("year", "month", "day", "hour"):
        pillar = pillars.get(key) or {}
        gz = str(pillar.get("ganzhi") or "")
        if len(gz) == 2:
            parts.append(gz)
    return "".join(parts)


def readable_verdict_excerpt(verdict: str, *, limit: int = 300) -> str:
    text = str(verdict or "").replace("\r", "\n")
    if not text.strip():
        return ""
    for opener in CASE_OPENERS:
        idx = text.find(opener)
        if idx >= 0:
            snippet = text[idx : idx + limit]
            return re.sub(r"\s+", " ", snippet).strip()
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned[:limit]


def case_has_readable_body(row: dict[str, Any]) -> bool:
    excerpt = readable_verdict_excerpt(str(row.get("verdict") or ""))
    return any(token in excerpt for token in CASE_OPENERS) and len(excerpt) >= 12


def match_context_from_chart(chart: dict[str, Any]) -> dict[str, Any]:
    pillars = chart.get("pillars") or {}
    month = pillars.get("month") or {}
    target_year = resolve_target_year(chart)
    active = resolve_active_dayun(chart, target_year)
    luck_ganzhi = str((active or {}).get("ganzhi") or "")
    question = str(chart.get("judgementQuestion") or "")
    question_tags = question_event_tags(question)
    theme_tags = theme_event_tags(chart)
    merged_tags: list[str] = []
    for tag in question_tags + theme_tags:
        if tag not in merged_tags:
            merged_tags.append(tag)
    return {
        "day_gan": str(chart.get("dayMaster") or ""),
        "month_zhi": str(month.get("zhi") or ""),
        "pillar_key": chart_pillar_key(chart),
        "target_year": target_year,
        "luck_ganzhi": luck_ganzhi,
        "question_tags": merged_tags,
        "question_theme": str((chart.get("benchmarkMeta") or {}).get("questionTheme") or ""),
    }


def _event_tag_score(row: dict[str, Any], question_tags: list[str]) -> int:
    row_tags = [str(tag) for tag in row.get("eventTags") or []]
    if not row_tags or not question_tags:
        return 0
    overlap = sum(1 for tag in row_tags if tag in question_tags)
    if overlap == 0:
        return 0
    base = overlap * 4
    if len(row_tags) >= 5:
        base = max(1, base - (len(row_tags) - 4))
    return base


def score_case_match(row: dict[str, Any], chart: dict[str, Any]) -> int:
    if not is_applicable_case(row):
        return 0
    ctx = match_context_from_chart(chart)
    score = 0
    pillar_key = ctx["pillar_key"]
    for tag in row.get("structureTags") or []:
        text = str(tag)
        if text.startswith("pillars:") and pillar_key:
            if text.split(":", 1)[1] == pillar_key:
                score += 10
            continue
        day_gan = ctx["day_gan"]
        month_zhi = ctx["month_zhi"]
        if day_gan and day_gan in text:
            score += 2
        if month_zhi and month_zhi in text:
            score += 2

    score += _event_tag_score(row, ctx["question_tags"])

    target_year = ctx["target_year"]
    if target_year is not None:
        years = row.get("eventYear") or []
        if target_year in years:
            score += 4

    luck_ganzhi = ctx["luck_ganzhi"]
    if luck_ganzhi:
        triggers = row.get("luckTrigger") or []
        if luck_ganzhi in triggers:
            score += 3

    observed = str(row.get("observedEvent") or "")
    question = str(chart.get("judgementQuestion") or "")
    if observed and question:
        for key in QUESTION_EVENT_TAGS:
            if key in question and key in observed:
                score += 2
                break

    if case_has_readable_body(row):
        score += 2

    chart_pattern = str(row.get("chartPattern") or "")
    if chart_pattern and chart_pattern in question:
        score += 2

    return score


def extract_years_from_text(text: str) -> list[int]:
    years: list[int] = []
    for match in re.finditer(r"(19\d{2}|20\d{2})", text):
        year = int(match.group(1))
        if 1900 <= year <= 2099 and year not in years:
            years.append(year)
    return years[:12]


def extract_luck_triggers(text: str) -> list[str]:
    triggers: list[str] = []
    ganzhi_re = re.compile(r"([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])")
    for match in re.finditer(r"(?:大运|行运|岁运)[^。\n]{0,24}?" + ganzhi_re.pattern, text):
        gz = match.group(1)
        if gz not in triggers:
            triggers.append(gz)
    for gz in ganzhi_re.findall(text):
        if len(triggers) >= 6:
            break
        if gz not in triggers:
            triggers.append(gz)
    return triggers[:6]
