import pytest

from app.core.ziwei.judgement.limit_judge import LimitJudge
from app.core.ziwei.judgement.topic_judge import TopicResult

pytest.importorskip("iztro_py")


def _sample_chart_with_limits() -> dict:
    return {
        "palaces": [
            {"name": "命宫", "earthlyBranch": "子", "majorStars": [{"name": "紫微"}]},
            {"name": "夫妻", "earthlyBranch": "午", "majorStars": [{"name": "贪狼"}]},
        ],
        "meta": {"soulPalaceBranch": "子"},
        "rulesMeta": {"chartSchool": "sanhe"},
        "limits": {
            "yearly": {
                "layer": "yearly",
                "available": True,
                "targetYear": 2026,
                "heavenlyStem": "丙",
                "earthlyBranch": "午",
                "stemBranch": "丙午",
                "palaceNames": ["夫妻"],
                "mutagens": ["忌"],
                "mutagenStars": [{"name": "太阴", "mutagen": "忌"}],
            },
            "current": {
                "decadal": {
                    "layer": "decadal",
                    "available": True,
                    "stemBranch": "甲辰",
                    "palaceNames": ["官禄"],
                    "mutagens": [],
                },
                "minor": {
                    "layer": "minor",
                    "available": True,
                    "palaceNames": ["财帛"],
                    "mutagens": [],
                },
            },
        },
    }


def test_limit_judge_builds_event_chain_for_yearly_marriage_theme() -> None:
    chart = _sample_chart_with_limits()
    topic = TopicResult(
        topic_id="marriage",
        topic_label="婚恋感情",
        target_palaces=["夫妻", "福德", "迁移"],
        confidence=0.8,
        rule_id="topic:marriage",
    )
    verdict = LimitJudge().judge(chart, target_year=2026, topic=topic)
    events = verdict.flags.get("eventChain") or []
    assert events
    yearly = next(item for item in events if item.get("layer") == "yearly")
    assert yearly.get("theme") == "婚恋"
    assert "夫妻" in yearly.get("natalHits") or "夫妻" in yearly.get("palaces")
    assert yearly.get("hasJiMutagen") is True
    assert "事件链" in verdict.summary


def test_limit_judge_evidence_request_includes_limit_topic() -> None:
    chart = _sample_chart_with_limits()
    topic = TopicResult(
        topic_id="career",
        topic_label="事业官禄",
        target_palaces=["官禄", "命宫"],
        confidence=0.7,
        rule_id="topic:career",
    )
    req = LimitJudge().evidence_request(chart, topic)
    assert req.topic == "limit"
    assert "官禄" in req.palaceScope
    assert "流年" in req.query
