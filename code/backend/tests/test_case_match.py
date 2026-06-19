from __future__ import annotations

from app.core.knowledge.case_match import (
    case_has_readable_body,
    is_applicable_case,
    is_binary_garbage,
    is_catalog_case,
    readable_verdict_excerpt,
    score_case_match,
)

SAMPLE_CHART = {
    "dayMaster": "丁",
    "pillars": {
        "year": {"ganzhi": "丙寅"},
        "month": {"ganzhi": "丙寅", "zhi": "寅"},
        "day": {"ganzhi": "丁卯"},
        "hour": {"ganzhi": "辛未"},
    },
    "judgementQuestion": "此人婚姻状况如何?",
    "benchmarkMeta": {"questionTheme": "婚姻感情"},
    "targetYear": 1998,
    "luckTimeline": {
        "dayun": [
            {
                "ganzhi": "丙寅",
                "startYear": 1990,
                "endYear": 1999,
                "liunian": [{"year": 1998, "ganzhi": "戊寅"}],
            }
        ]
    },
}


def test_is_binary_garbage_detects_docx_header() -> None:
    assert is_binary_garbage("PK\x03\x04\x14\x00\x00\x00")


def test_is_catalog_case_detects_book_index() -> None:
    row = {
        "verdict": "目录 函测命例 ISBN 出版者 中国周易文化出版社",
        "observedEvent": "1779767159",
    }
    assert is_catalog_case(row) is True


def test_is_applicable_case_skips_do_not_apply() -> None:
    row = {
        "verdict": "乾造 甲子 丙寅 丁卯 辛未",
        "structureTags": ["pillars:甲子丙寅丁卯辛未"],
        "eventTags": ["marriage"],
        "doNotApplyReason": "binary_or_unreadable",
    }
    assert is_applicable_case(row) is False


def test_score_case_match_prefers_pillar_and_theme_tags() -> None:
    row = {
        "verdict": "乾造：丙寅 丙寅 丁卯 辛未 1998年结婚",
        "structureTags": ["pillars:丙寅丙寅丁卯辛未", "gan_bias:丁"],
        "eventTags": ["marriage"],
        "eventYear": [1998],
        "luckTrigger": ["丙寅"],
        "observedEvent": "婚姻",
    }
    score = score_case_match(row, SAMPLE_CHART)
    assert score >= 18


def test_score_case_match_penalizes_tag_spam() -> None:
    spam = {
        "verdict": "乾造 甲子 丙寅 丁卯 辛未",
        "structureTags": [],
        "eventTags": ["marriage", "wealth", "career", "health", "disaster", "bereavement"],
        "observedEvent": "合集",
    }
    focused = {
        "verdict": "乾造 甲子 丙寅 丁卯 辛未",
        "structureTags": [],
        "eventTags": ["marriage"],
        "observedEvent": "婚姻",
    }
    chart = {
        **SAMPLE_CHART,
        "judgementQuestion": "婚姻如何",
        "benchmarkMeta": {"questionTheme": "婚姻感情"},
    }
    assert score_case_match(focused, chart) > score_case_match(spam, chart)


def test_readable_verdict_excerpt_starts_at_case_opener() -> None:
    text = "目录 前言\r乾造：丙寅 丙寅 丁卯 辛未\r一、断旺衰"
    excerpt = readable_verdict_excerpt(text)
    assert excerpt.startswith("乾造")
    assert case_has_readable_body({"verdict": text}) is True


def test_score_case_match_returns_zero_for_binary() -> None:
    row = {
        "verdict": "PK\x03\x04",
        "structureTags": [],
        "eventTags": [],
    }
    assert score_case_match(row, SAMPLE_CHART) == 0
