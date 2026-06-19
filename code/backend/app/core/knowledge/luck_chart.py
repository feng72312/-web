"""Resolve dayun+liunian rows from contest/API chart payloads."""

from __future__ import annotations

from typing import Any


def get_dayun_timeline(chart: dict[str, Any]) -> list[dict[str, Any]]:
    """Prefer luckTimeline.dayun (full liunian); fallback to top-level dayun."""
    timeline = chart.get("luckTimeline") or {}
    rows = timeline.get("dayun")
    if rows:
        return list(rows)
    return list(chart.get("dayun") or [])


def resolve_target_year(chart: dict[str, Any]) -> int | None:
    for key in ("targetYear", "target_year"):
        value = chart.get(key)
        if value:
            return int(value)
    meta = chart.get("meta") or {}
    if meta.get("targetYear"):
        return int(meta["targetYear"])
    benchmark = chart.get("benchmarkMeta") or {}
    if benchmark.get("targetYear"):
        return int(benchmark["targetYear"])
    judgement = chart.get("judgementContext") or {}
    if judgement.get("targetYear"):
        return int(judgement["targetYear"])
    return None


def find_dayun_for_year(chart: dict[str, Any], year: int) -> dict[str, Any] | None:
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


def resolve_active_dayun(
    chart: dict[str, Any],
    target_year: int | None = None,
) -> dict[str, Any] | None:
    timeline = get_dayun_timeline(chart)
    if not timeline:
        return None
    year = target_year if target_year is not None else resolve_target_year(chart)
    if year is not None:
        hit = find_dayun_for_year(chart, year)
        if hit:
            return hit
    return timeline[0]


def enrich_chart_for_judgement(
    chart: dict[str, Any],
    *,
    question: str = "",
    benchmark_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    enriched = dict(chart)
    target_year = resolve_target_year(enriched)
    if target_year is None and benchmark_meta and benchmark_meta.get("targetYear"):
        target_year = int(benchmark_meta["targetYear"])
    if target_year is None and question:
        from app.core.knowledge.year_infer import infer_target_year

        inferred = infer_target_year(question)
        if inferred:
            target_year = inferred
    if target_year is not None:
        enriched["targetYear"] = target_year
    if benchmark_meta:
        enriched["benchmarkMeta"] = benchmark_meta
    if question:
        enriched["judgementQuestion"] = question.strip()
    active = resolve_active_dayun(enriched, target_year)
    if active:
        enriched["activeDayun"] = {
            "index": active.get("index"),
            "ganzhi": active.get("ganzhi"),
            "startAge": active.get("startAge"),
            "endAge": active.get("endAge"),
            "startYear": active.get("startYear"),
            "endYear": active.get("endYear"),
        }
    return enriched
