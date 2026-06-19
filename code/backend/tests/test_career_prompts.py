from __future__ import annotations

from app.core.agent.prompts_contest import build_contest_mcq_parts


def test_career_wealth_prompt_format() -> None:
    chart = {
        "gender": "male",
        "birthYear": 1980,
        "pillars": {"day": {"zhi": "子"}},
        "luckTimeline": {"dayun": [], "liunian": []},
    }
    system, user = build_contest_mcq_parts(
        chart,
        "命主目前身家？",
        [
            "A. 身家超过千万",
            "B. 收入平平",
            "C. 收入顺遂",
            "D. 欠债超过1千万",
        ],
    )
    assert "财旺不等于发财" in system
    assert "【财星体用】" in system
    assert "【选项排除】" in system
    assert "勿见财就断发财" in user


def test_career_status_prompt_format() -> None:
    chart = {
        "gender": "male",
        "birthYear": 1980,
        "pillars": {"day": {"zhi": "子"}},
        "luckTimeline": {"dayun": [], "liunian": []},
    }
    system, user = build_contest_mcq_parts(
        chart,
        "命主目前的职业是什么？",
        ["A 自己经商", "B 公司职员", "C 偏门放贷", "D 无固定工作"],
    )
    assert "禁止仅因七杀/正官透干就选公务员" in system
    assert "【选项对照】" in system
    assert "先读各选项字面职业" in user


def test_career_year_event_prompt_format() -> None:
    chart = {
        "gender": "male",
        "birthYear": 1980,
        "pillars": {"day": {"zhi": "子"}},
        "luckTimeline": {"dayun": [], "liunian": []},
    }
    system, user = build_contest_mcq_parts(
        chart,
        "命主哪年工作上有新突破？",
        ["A 2014年", "B 2016年", "C 2018年", "D 2021年"],
    )
    assert "【目标年/运限】" in system
    assert "逐选项核对大运流年" in user


def test_career_major_prompt_format() -> None:
    chart = {
        "gender": "female",
        "birthYear": 1988,
        "pillars": {"day": {"zhi": "子"}},
        "luckTimeline": {"dayun": [], "liunian": []},
    }
    system, user = build_contest_mcq_parts(
        chart,
        "命主大学时期读什么科系？",
        ["A. 美术", "B. 理工", "C. 会计", "D. 法律"],
    )
    assert "【五行科系】" in system
    assert "同一五行多个行业须逐项对照" in user
