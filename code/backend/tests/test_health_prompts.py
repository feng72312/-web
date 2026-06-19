from __future__ import annotations

from app.core.agent.prompts_contest import build_contest_mcq_parts


def _chart() -> dict:
    return {
        "gender": "male",
        "birthYear": 1970,
        "pillars": {"day": {"zhi": "子"}},
        "luckTimeline": {"dayun": [], "liunian": []},
    }


def test_health_year_event_prompt_format() -> None:
    system, user = build_contest_mcq_parts(
        _chart(),
        "命主在哪一年意外受伤大腿骨折？",
        ["A. 1998年", "B. 2010年", "C. 2018年", "D. 2022年"],
    )
    assert "禁止仅因七杀/官杀透干就断重病" in system
    assert "【病灾象】" in system
    assert "【健康选项年份锚点】" in system
    assert "病灾象" in user


def test_health_dayun_span_prompt_format() -> None:
    system, user = build_contest_mcq_parts(
        _chart(),
        "虚龄35至44甲戌大运期间，最困扰命主的疾病为?",
        ["A 呼吸系统", "B 消化系统", "C 泌尿系统", "D 其它疾病"],
    )
    assert "【运限病象】" in system
    assert "【选项对照】" in system
    assert "虚龄大运锚点" in user


def test_health_status_prompt_format() -> None:
    system, user = build_contest_mcq_parts(
        _chart(),
        "游先生52岁目前健康状况如何？",
        ["A 身强体健", "B 四肢无力", "C 肠胃心肺机能不佳", "D 已经去世"],
    )
    assert "【选项对照】" in system
    assert "禁止仅因七杀/官杀透干就断重病" in system
    assert "先读各选项字面症状" in user


def test_health_diagnosis_prompt_format() -> None:
    system, user = build_contest_mcq_parts(
        _chart(),
        "请问命主在一岁前被诊断出那一种疾病？",
        ["A. 鼻子", "B. 心脏有孔", "C. 肺炎", "D. 地中海贫血症"],
    )
    assert "【五行脏腑】" in system
    assert "选项字面病名" in user
