from __future__ import annotations

from app.core.liuyao.judgement.topic_judge import classify_topic
from app.core.liuyao.judgement.yong_shen_judge import judge_yong_shen


def _sample_chart() -> dict:
    return {
        "shiYing": {"shi": 3, "ying": 6},
        "lines": [
            {"position": 1, "liuqin": "父母", "stem": "甲", "branch": "子"},
            {"position": 2, "liuqin": "兄弟", "stem": "乙", "branch": "丑"},
            {"position": 3, "liuqin": "官鬼", "stem": "丙", "branch": "寅", "isShi": True},
            {"position": 4, "liuqin": "妻财", "stem": "丁", "branch": "卯"},
            {"position": 5, "liuqin": "子孙", "stem": "戊", "branch": "辰"},
            {"position": 6, "liuqin": "父母", "stem": "己", "branch": "巳", "isYing": True},
        ],
    }


def test_wealth_yong_shen_rule():
    topic = classify_topic("求财生意如何")
    result = judge_yong_shen(_sample_chart(), "求财生意如何", topic)
    assert result.yong_shen == "妻财"
    assert result.position == 4
    assert result.source == "rule"
    assert result.confidence >= 0.5


def test_career_yong_shen_rule():
    topic = classify_topic("工作升职机会")
    result = judge_yong_shen(_sample_chart(), "工作升职机会", topic)
    assert result.yong_shen == "官鬼"
    assert result.position == 3
    assert result.source == "rule"


def test_exam_yong_shen_rule():
    topic = classify_topic("考试能否通过")
    result = judge_yong_shen(_sample_chart(), "考试能否通过", topic)
    assert result.yong_shen == "父母"
    assert result.position in {1, 6}


def test_travel_uses_shi_line_liuqin():
    topic = classify_topic("这次出行顺利吗")
    result = judge_yong_shen(_sample_chart(), "这次出行顺利吗", topic)
    assert result.position == 3
    assert result.yong_shen == "官鬼"
    assert result.source == "rule"


def test_missing_liuqin_fallback():
    chart = {
        "shiYing": {"shi": 2, "ying": 5},
        "lines": [
            {"position": 1, "liuqin": "父母"},
            {"position": 2, "liuqin": "兄弟", "isShi": True},
            {"position": 3, "liuqin": "兄弟"},
            {"position": 4, "liuqin": "兄弟"},
            {"position": 5, "liuqin": "兄弟", "isYing": True},
            {"position": 6, "liuqin": "兄弟"},
        ],
    }
    topic = classify_topic("求财能否盈利")
    result = judge_yong_shen(chart, "求财能否盈利", topic)
    assert result.source == "rule"
    assert "不上卦" in result.reason or result.yong_shen == "兄弟"
    assert result.yong_shen == "兄弟"


def test_rule_result_has_topic_metadata():
    result = judge_yong_shen(_sample_chart(), "求财")
    assert result.topic_id == "wealth"
    assert result.rule_id.startswith("topic:")
