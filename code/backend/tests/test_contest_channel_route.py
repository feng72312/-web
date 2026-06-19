from __future__ import annotations

from app.core.knowledge.contest_channel_route import (
    has_explicit_timing_signal,
    is_static_dominant_without_timing,
    is_yingqi_question,
    resolve_contest_votes,
    uses_full_judgement_chain,
)
from app.core.knowledge.luck_prompt_util import parse_dayun_ganzhi_from_question
from app.core.knowledge.mcq_reasoning_mode import should_structured_mcq_reasoning
from app.core.knowledge.target_year_block import build_virtual_age_dayun_anchor


def test_full_judgement_marriage_health() -> None:
    assert uses_full_judgement_chain("命主婚姻状况如何?", ["A 已婚", "B 离婚"])
    assert uses_full_judgement_chain("命主健康如何?", ["A 好", "B 差"])
    assert uses_full_judgement_chain("2017年结婚情况?", ["A", "B", "C", "D"])


def test_yingqi_not_marriage_even_with_year() -> None:
    assert not is_yingqi_question("2017年结婚情况?", ["A", "B", "C", "D"])
    assert uses_full_judgement_chain("2017年结婚情况?", ["A", "B", "C", "D"])


def test_yingqi_liunian_and_virtual_age() -> None:
    # health/disease questions stay on full judgement chain even with virtual age
    health_q = "\u865a\u9f8435\u81f344\u7532\u620c\u5927\u8fd0\u671f\u95f4\uff0c\u6700\u56f0\u6270\u547d\u4e3b\u7684\u75be\u75c5\u4e3a?"
    assert uses_full_judgement_chain(health_q, ["A", "B", "C", "D"])
    assert not is_yingqi_question(health_q, ["A", "B", "C", "D"])
    q = "\u865a\u9f8435\u81f344\u7532\u620c\u5927\u8fd0\u671f\u95f4\uff0c\u547d\u4e3b\u8d22\u8fd0\u5982\u4f55?"
    opts = ["A a", "B b", "C c", "D d"]
    assert is_yingqi_question(q, opts)
    assert not uses_full_judgement_chain(q, opts)
    assert parse_dayun_ganzhi_from_question(q) == "\u7532\u620c"


def test_yingqi_year_options() -> None:
    opts = ["A 2010\u5e74", "B 2017\u5e74", "C 2022\u5e74", "D 1995\u5e74"]
    assert is_yingqi_question("\u547d\u4e3b\u4e8e\u54ea\u4e00\u5e74\u6709\u5bb6\u5b85\u642c\u8fc1?", opts)


def test_yingqi_na_nian_signal() -> None:
    assert has_explicit_timing_signal("\u547d\u4e3b\u90a3\u5e74\u7ed3\u5a5a?", ["A", "B", "C", "D"])


def test_static_education_uses_light_channel() -> None:
    q = "\u547d\u4e3b\u8bfb\u4e66\u53ca\u5b66\u5386\u60c5\u51b5\u5982\u4f55?"
    opts = ["A \u5927\u4e13", "B \u5927\u5b66", "C \u4e2d\u5b66", "D \u535a\u58eb"]
    assert is_static_dominant_without_timing(q, opts)
    assert not is_yingqi_question(q, opts)
    assert should_structured_mcq_reasoning(q, opts)


def test_education_with_year_options_uses_yingqi() -> None:
    q = "\u6b64\u547d\u7684\u5b66\u5386\u5982\u4f55\uff1f"
    opts = [
        "A \u4e2d\u4e03\u6bd5\u4e1a",
        "B 2002\u5e74\u5347\u5b66\u5185\u5730\uff0c2006\u5e74\u5927\u5b66\u6bd5\u4e1a",
        "C \u9884\u79d1\u540e\u5347\u672c\u5730\u5927\u5b66\uff0c2004\u5e74\u5927\u5b66\u6bd5\u4e1a",
        "D \u4e2d\u4e94\u540e\uff0c1998\u5e74\u51fa\u56fd\u7559\u5b66",
    ]
    assert has_explicit_timing_signal(q, opts)
    assert is_yingqi_question(q, opts)
    assert not is_static_dominant_without_timing(q, opts)
    assert should_structured_mcq_reasoning(q, opts)


def test_static_family_with_year_options_stays_yingqi() -> None:
    q = "\u547d\u4e3b\u7236\u4eb2\u4e8e\u54ea\u5e74\u53bb\u4e16?"
    opts = ["A 1959 \u5df1\u4ea5\u5e74", "B 1963 \u7678\u536f\u5e74", "C 1964", "D 1969"]
    assert has_explicit_timing_signal(q, opts)
    assert is_yingqi_question(q, opts)
    assert should_structured_mcq_reasoning(q, opts)


def test_static_children_long_form_no_timing() -> None:
    q = "\u547d\u4e3b\u5176\u5b50\u5973\u60c5\u51b5\u5982\u4f55"
    opts = ["A a", "B b", "C c", "D d"]
    assert not is_yingqi_question(q, opts)
    assert not should_structured_mcq_reasoning(q, opts)


def test_static_family_uses_light_structured() -> None:
    q = "\u6b64\u547d\u51fa\u8eab\u8d2b\u6216\u5bcc?"
    opts = ["A \u5b64\u513f\u9662", "B \u8d2b\u7a77", "C \u5c0f\u5eb7", "D \u5927\u5bcc"]
    assert is_static_dominant_without_timing(q, opts)
    assert not is_yingqi_question(q, opts)
    assert should_structured_mcq_reasoning(q, opts)


def test_resolve_contest_votes_full_default_three() -> None:
    q = "命主婚姻状况如何?"
    assert resolve_contest_votes(q, ["A a", "B b"], 1) == 3
    assert resolve_contest_votes(q, ["A a", "B b"], 2) == 2


def test_resolve_contest_votes_yingqi_stays_one() -> None:
    q = "命主哪一年发财?"
    opts = ["A 2018", "B 2019", "C 2020", "D 2021"]
    assert resolve_contest_votes(q, opts, 1) == 1


def test_virtual_age_anchor_sample_chart() -> None:
    chart = {
        "luckTimeline": {
            "dayun": [
                {
                    "index": 7,
                    "ganzhi": "甲戌",
                    "startAge": 35,
                    "endAge": 44,
                    "startYear": 1988,
                    "endYear": 1997,
                    "pillar": {"shishenGan": "七杀"},
                }
            ]
        }
    }
    q = "\u865a\u9f8435\u81f344\u7532\u620c\u5927\u8fd0\u671f\u95f4\uff0c\u6700\u56f0\u6270\u547d\u4e3b\u7684\u75be\u75c5\u4e3a?"
    block = build_virtual_age_dayun_anchor(chart, q)
    assert "第7运 甲戌" in block
    assert "虚龄35-44" in block
    assert "1988" in block

