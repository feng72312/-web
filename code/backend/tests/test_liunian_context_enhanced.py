from __future__ import annotations

from app.core.agent.prompts_contest import build_contest_mcq_parts
from app.core.knowledge.liunian_context import (
    build_liunian_prompt_block,
    format_liunian_rules_block,
    format_liunian_timeline,
    _needs_liunian_block,
)
from app.core.knowledge.contest_channel_route import has_explicit_timing_signal

SAMPLE_CHART = {
    "dayMaster": "甲",
    "dayMasterWuxing": "木",
    "wuxingCount": {"木": 2, "火": 1, "土": 2, "金": 1, "水": 2},
    "pillars": {
        "year": {"gan": "甲", "zhi": "子", "shishenGan": "比肩", "ganzhi": "甲子"},
        "month": {"gan": "丙", "zhi": "寅", "shishenGan": "食神", "ganzhi": "丙寅"},
        "day": {"gan": "甲", "zhi": "午", "shishenGan": "", "ganzhi": "甲午"},
        "hour": {"gan": "乙", "zhi": "亥", "shishenGan": "劫财", "ganzhi": "乙亥"},
    },
    "dayun": [
        {"index": 1, "ganzhi": "丁卯", "startAge": 8, "endAge": 17, "startYear": 1990},
        {"index": 2, "ganzhi": "戊辰", "startAge": 18, "endAge": 27, "startYear": 2000},
    ],
    "luckTimeline": {
        "dayun": [
            {
                "index": 7,
                "ganzhi": "甲戌",
                "startAge": 35,
                "endAge": 44,
                "startYear": 1988,
                "endYear": 1997,
                "liunian": [
                    {"year": 1990, "ganzhi": "庚午", "pillar": {"shishenGan": "七杀", "hideStems": []}},
                    {"year": 1991, "ganzhi": "辛未", "pillar": {"shishenGan": "正官", "hideStems": []}},
                    {"year": 1992, "ganzhi": "壬申", "pillar": {"shishenGan": "偏印", "hideStems": []}},
                ],
            },
            {
                "index": 1,
                "ganzhi": "丁卯",
                "startAge": 8,
                "endAge": 17,
                "startYear": 1990,
                "liunian": [
                    {"year": 2022, "ganzhi": "壬寅", "pillar": {"shishenGan": "偏印", "hideStems": []}},
                ],
            },
        ]
    },
}


def test_needs_liunian_block_for_year_options() -> None:
    options = ["A. 2018年", "B. 2019年", "C. 2020年", "D. 2021年"]
    assert _needs_liunian_block("此人婚姻状况?", options)


def test_build_liunian_prompt_block_includes_rules_or_timeline() -> None:
    block = build_liunian_prompt_block(
        SAMPLE_CHART,
        "在2022年婚姻如何?",
        options=["A. 2018", "B. 2022", "C. 2024", "D. 2026"],
        force=True,
    )
    if not block:
        return
    assert "流年" in block or "大运" in block


def test_contest_prompt_can_include_liunian_block() -> None:
    system, _user = build_contest_mcq_parts(
        SAMPLE_CHART,
        "在2022年婚姻如何?",
        ["A. 2018年", "B. 2022年", "C. 2024年", "D. 2026年"],
        use_option_elimination=True,
    )
    if "流年岁运规则" in system or "流年时间轴" in system or "大运概览" in system:
        assert "流年" in system or "大运" in system


def test_format_liunian_rules_block_when_enabled() -> None:
    block = format_liunian_rules_block("2022年流年并临冲克")
    if block:
        assert "流年岁运规则" in block


def test_format_liunian_timeline_virtual_age_and_named_dayun_full_segment() -> None:
    q = "虚龄35至44甲戌大运期间，命主最困扰的疾病为?"
    block = format_liunian_timeline(SAMPLE_CHART, q)
    assert "第7运 甲戌" in block
    assert "1990 庚午" in block
    assert "1991 辛未" in block
    assert "1992 壬申" in block
    assert "丁卯" not in block


def test_format_liunian_timeline_year_options_expand_dayun_segment() -> None:
    chart = {
        **SAMPLE_CHART,
        "luckTimeline": {
            "dayun": [
                {
                    "index": 4,
                    "ganzhi": "庚辰",
                    "startAge": 37,
                    "endAge": 46,
                    "startYear": 2010,
                    "endYear": 2019,
                    "liunian": [
                        {"year": 2016, "ganzhi": "丙申", "pillar": {"shishenGan": "食神", "hideStems": []}},
                        {"year": 2017, "ganzhi": "丁酉", "pillar": {"shishenGan": "伤官", "hideStems": []}},
                        {"year": 2018, "ganzhi": "戊戌", "pillar": {"shishenGan": "偏财", "hideStems": []}},
                        {"year": 2019, "ganzhi": "己亥", "pillar": {"shishenGan": "正财", "hideStems": []}},
                        {"year": 2020, "ganzhi": "庚子", "pillar": {"shishenGan": "七杀", "hideStems": []}},
                    ],
                }
            ]
        },
    }
    q = "命主于哪年再婚?"
    opts = ["A. 2017年", "B. 2018年", "C. 2019年", "D. 2020年"]
    block = format_liunian_timeline(chart, q, opts)
    assert "第4运 庚辰" in block
    assert "2016 丙申" in block
    assert ">>2017" in block or "  2017" in block
    assert "2020 庚子" in block


def test_timing_signal_na_nian() -> None:
    assert has_explicit_timing_signal("命主那年结婚?", ["A 已婚", "B 离婚"])
    assert _needs_liunian_block("命主哪年发财?")
