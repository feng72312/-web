from __future__ import annotations

from app.core.liuyao.judgement.topic_judge import classify_topic


def test_wealth_topic():
    result = classify_topic("这次投资能不能赚钱")
    assert result.topic_id == "wealth"
    assert result.candidate_yong_shen == "妻财"
    assert result.confidence >= 0.5


def test_career_topic():
    result = classify_topic("明年能否升职")
    assert result.topic_id == "career"
    assert result.candidate_yong_shen == "官鬼"


def test_exam_topic():
    result = classify_topic("考试能否录取")
    assert result.topic_id == "exam"
    assert result.candidate_yong_shen == "父母"


def test_marriage_topic():
    result = classify_topic("感情能否结婚")
    assert result.topic_id == "marriage"
    assert result.candidate_yong_shen == "妻财"


def test_illness_topic():
    result = classify_topic("最近身体不舒服")
    assert result.topic_id == "illness"
    assert result.candidate_yong_shen == "官鬼"


def test_children_topic():
    result = classify_topic("怀孕是否顺利")
    assert result.topic_id == "children"
    assert result.candidate_yong_shen == "子孙"


def test_general_topic_low_confidence():
    result = classify_topic("随便问问")
    assert result.topic_id == "general"
    assert result.confidence < 0.5


def test_self_illness_priority():
    result = classify_topic("我自占病能否痊愈")
    assert result.topic_id in {"self_illness", "illness"}
    assert result.candidate_yong_shen in {"世爻", "官鬼"}
