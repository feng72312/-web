from __future__ import annotations

from app.core.judgement.judges import SuiYunJudge
from app.core.knowledge.geju_special import detect_geju_special_patterns
from app.core.knowledge.keys import build_suiyun_key
from app.core.knowledge.luck_chart import (
    enrich_chart_for_judgement,
    find_dayun_for_year,
    resolve_active_dayun,
    resolve_target_year,
)

DAYUN_TIMELINE = [
    {
        "index": 1,
        "ganzhi": "丁卯",
        "startAge": 8,
        "endAge": 17,
        "startYear": 1990,
        "endYear": 1999,
        "liunian": [{"year": 1995, "ganzhi": "乙亥"}],
    },
    {
        "index": 2,
        "ganzhi": "戊辰",
        "startAge": 18,
        "endAge": 27,
        "startYear": 2000,
        "endYear": 2009,
        "liunian": [{"year": 2005, "ganzhi": "乙酉"}],
    },
]

BASE_CHART = {
    "dayMaster": "甲",
    "dayMasterWuxing": "木",
    "pillars": {
        "year": {"gan": "甲", "zhi": "子"},
        "month": {"gan": "丙", "zhi": "寅"},
        "day": {"gan": "甲", "zhi": "午"},
        "hour": {"gan": "乙", "zhi": "亥"},
    },
    "dayun": [DAYUN_TIMELINE[0]],
    "luckTimeline": {"dayun": DAYUN_TIMELINE},
}

NO_ROOT_WEAK_WEALTH_CHART = {
    "dayMaster": "甲",
    "dayMasterWuxing": "木",
    "wuxingCount": {"木": 1, "火": 1, "土": 1, "金": 4, "水": 1},
    "pillars": {
        "year": {"gan": "庚", "zhi": "申", "shishenGan": "七杀", "shishenZhi": ["七杀", "偏财"]},
        "month": {"gan": "辛", "zhi": "酉", "shishenGan": "正官", "shishenZhi": ["正官"]},
        "day": {"gan": "甲", "zhi": "申", "shishenGan": "", "shishenZhi": ["七杀", "偏财"]},
        "hour": {"gan": "庚", "zhi": "午", "shishenGan": "七杀", "shishenZhi": ["伤官", "正财"]},
    },
}


def test_find_dayun_for_year_by_range() -> None:
    hit = find_dayun_for_year(BASE_CHART, 2005)
    assert hit is not None
    assert hit["ganzhi"] == "戊辰"


def test_resolve_active_dayun_prefers_target_year() -> None:
    chart = enrich_chart_for_judgement(
        BASE_CHART,
        question="2005年事业如何",
        benchmark_meta={"targetYear": 2005},
    )
    active = resolve_active_dayun(chart, resolve_target_year(chart))
    assert active is not None
    assert active["ganzhi"] == "戊辰"
    assert chart["activeDayun"]["ganzhi"] == "戊辰"


def test_build_suiyun_key_uses_active_dayun() -> None:
    chart = enrich_chart_for_judgement(BASE_CHART, benchmark_meta={"targetYear": 2005})
    key = build_suiyun_key(chart)
    assert key["ganzhi"] == "戊辰"


def test_suiyun_judge_summary_mentions_target_year() -> None:
    chart = enrich_chart_for_judgement(BASE_CHART, benchmark_meta={"targetYear": 2005})
    verdict = SuiYunJudge().judge(chart)
    assert "2005" in verdict.summary
    assert "戊辰" in verdict.summary


def test_congcai_requires_no_root_when_weak() -> None:
    patterns = detect_geju_special_patterns(NO_ROOT_WEAK_WEALTH_CHART)
    assert "congcai" in patterns
    assert "congsha" in patterns
