from __future__ import annotations

from app.core.knowledge.health_subtheme import infer_health_subtheme


def test_health_year_event_subtheme() -> None:
    q = "命主在哪一年意外受伤大腿骨折？"
    opts = ["A. 1998年", "B. 2010年", "C. 2018年", "D. 2022年"]
    assert infer_health_subtheme(q, opts) == "health-year-event"


def test_health_dayun_span_subtheme() -> None:
    q = "虚龄35至44甲戌大运期间，最困扰命主的疾病为?"
    opts = ["A 呼吸系统", "B 消化系统", "C 泌尿系统", "D 其它疾病"]
    assert infer_health_subtheme(q, opts) == "health-dayun-span"


def test_health_diagnosis_subtheme() -> None:
    q = "命主在2014年曾接受手术，手术器官？"
    opts = ["A 心脏", "B 脑部", "C 双肺", "D 肾脏"]
    assert infer_health_subtheme(q, opts) == "health-diagnosis"


def test_health_status_subtheme() -> None:
    q = "游先生52岁目前健康状况如何？"
    opts = [
        "A 身强体健",
        "B 四肢无力",
        "C 肠胃心肺机能不佳",
        "D 已经去世",
    ]
    assert infer_health_subtheme(q, opts) == "health-status"


def test_health_status_year_narrative_options() -> None:
    q = "命主健康状况?"
    opts = [
        "A.2011年血癌",
        "B.2013年手术",
        "C.2016年确诊癌症",
        "D.2020年确诊新冠",
    ]
    assert infer_health_subtheme(q, opts) == "health-status"


def test_non_health_returns_none() -> None:
    assert infer_health_subtheme("命主学历如何?", ["A. 大学"]) is None
