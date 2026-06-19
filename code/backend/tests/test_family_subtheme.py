from __future__ import annotations

from app.core.knowledge.family_subtheme import infer_family_subtheme


def test_death_mother_subtheme() -> None:
    q = "命主母亲于哪年离世?"
    opts = ["A. 1989年", "B. 1990年", "C. 2011年", "D. 2021年"]
    assert infer_family_subtheme(q, opts) == "family-death-mother"


def test_death_father_subtheme() -> None:
    q = "命主父亲于哪年去世?"
    opts = ["A. 1963年", "B. 1964年", "C. 1969年", "D. 1975年"]
    assert infer_family_subtheme(q, opts) == "family-death-father"


def test_wealth_tier_subtheme() -> None:
    q = "此命出生家境如何?"
    opts = [
        "A. 贫穷家庭出身",
        "B. 小康之家出身",
        "C. 富贵家庭出身",
        "D. 大富贵家庭出身",
    ]
    assert infer_family_subtheme(q, opts) == "family-wealth-tier"


def test_wealth_poor_or_rich_question() -> None:
    q = "此命出身贫或富?"
    opts = [
        "A. 贫穷家庭出身",
        "B. 小康之家出身",
        "C. 富贵家庭出身",
        "D. 虽有父母, 童年却被养在孤儿院",
    ]
    assert infer_family_subtheme(q, opts) == "family-wealth-tier"


def test_relation_subtheme() -> None:
    q = "命主与父母的关系、家庭背景如何?"
    opts = [
        "A. 父母恩爱, 家庭和睦",
        "B. 父母吵闹不休",
        "C. 父母离异, 跟父亲",
        "D. 父母离异, 跟母亲",
    ]
    assert infer_family_subtheme(q, opts) == "family-relation"


def test_miyazaki_death_father_from_options() -> None:
    q = "命主出身及家庭情况?"
    opts = [
        "A. 出生后父亲去世，母亲改嫁",
        "B. 父亲为政府高职位，2021年去世",
        "C. 母亲为家庭主妇，父亲为小型企业主",
        "D. 1986年父亲去世，母亲继承父亲产业",
    ]
    assert infer_family_subtheme(q, opts) == "family-death-father"


def test_guangdong_mixed_narrative_is_relation() -> None:
    q = "此命出生家境如何?"
    opts = ["A. 富裕", "B. 贫穷", "C. 父从商母是村干部", "D. 父母当官"]
    assert infer_family_subtheme(q, opts) == "family-relation"


def test_non_family_returns_none() -> None:
    q = "命主学历状况如何?"
    assert infer_family_subtheme(q, ["A. 大学"]) is None

    assert infer_family_subtheme(q, ["A. 大学"]) is None
