from __future__ import annotations

import re


def extract_years_from_question(question: str) -> list[int]:
    found: list[int] = []
    for m in re.finditer(r"(19|20)\d{2}", question):
        y = int(m.group(0))
        if 1900 <= y <= 2100:
            found.append(y)
    return sorted(set(found))


def parse_virtual_age_span(question: str) -> tuple[int, int] | None:
    m = re.search(r"虚龄\s*(\d+)\s*至\s*(\d+)", question)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


def resolve_target_year_from_chart(
    chart: dict[str, Any],
    question: str,
) -> int | None:
    """First explicit Gregorian year in stem, else midpoint year of virtual-age dayun."""
    years = extract_years_from_question(question)
    if years:
        return years[0]
    span = parse_virtual_age_span(question)
    if not span:
        return None
    from app.core.knowledge.luck_chart import get_dayun_timeline

    mid_age = (span[0] + span[1]) // 2
    for dy in get_dayun_timeline(chart):
        sa = dy.get("startAge")
        ea = dy.get("endAge")
        sy = dy.get("startYear")
        if sa is None or ea is None or sy is None:
            continue
        sa_i, ea_i, sy_i = int(sa), int(ea), int(sy)
        if sa_i <= mid_age <= ea_i:
            return sy_i + (mid_age - sa_i)
    return None
