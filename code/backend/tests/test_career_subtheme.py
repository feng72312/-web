from __future__ import annotations

from app.core.knowledge.career_subtheme import infer_career_subtheme


def test_major_industry_subtheme() -> None:
    q = "命主大学时期读什么科系？"
    opts = ["A. 美术", "B. 理工", "C. 会计", "D. 法律"]
    assert infer_career_subtheme(q, opts) == "major-industry"


def test_wealth_subtheme() -> None:
    q = "命主目前身家？"
    opts = [
        "A. 身家超过千万",
        "B. 收入平平",
        "C. 收入顺遂",
        "D. 欠债超过1千万",
    ]
    assert infer_career_subtheme(q, opts) == "wealth"


def test_wealth_fortune_question() -> None:
    q = "命主财运?"
    opts = [
        "A 普通财运",
        "B 婚后财运好",
        "C 财源广",
        "D 地产奴隶",
    ]
    assert infer_career_subtheme(q, opts) == "wealth"


def test_career_status_subtheme() -> None:
    q = "命主目前的职业是什么？"
    opts = [
        "A 自己经商",
        "B 公司职员",
        "C 偏门放贷",
        "D 无固定工作",
    ]
    assert infer_career_subtheme(q, opts) == "career-status"


def test_career_year_event_subtheme() -> None:
    q = "命主哪年工作上有新突破？"
    opts = ["A 2014年", "B 2016年", "C 2018年", "D 2021年"]
    assert infer_career_subtheme(q, opts) == "career-year-event"


def test_career_year_event_entrepreneur() -> None:
    q = "命主因与上司不稳定而辞职创业，哪年？"
    opts = ["A1991", "B1992", "C1993", "D1994"]
    assert infer_career_subtheme(q, opts) == "career-year-event"


def test_non_career_returns_none() -> None:
    assert infer_career_subtheme("命主学历如何?", ["A. 大学"]) is None
