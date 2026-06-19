from __future__ import annotations

from app.core.agent.prompts_contest import (
    _build_confidence_guard_block,
    build_contest_mcq_parts,
)


def test_confidence_guard_uses_standard_conservative() -> None:
    judgement = {
        "arbitration": {
            "confidenceBand": "medium",
            "conflicts": ["test"],
        }
    }
    block = _build_confidence_guard_block(judgement)
    assert "保守作答约束" in block
    assert "婚姻题分层保守约束" not in block


def test_marriage_prompt_p5_liunian_format() -> None:
    chart = {
        "gender": "male",
        "birthYear": 1980,
        "pillars": {"day": {"zhi": "子"}},
        "luckTimeline": {"dayun": [], "liunian": []},
    }
    system, user = build_contest_mcq_parts(
        chart,
        "命主哪一年结婚?",
        ["A 2018", "B 2019", "C 2020", "D 2021"],
        judgement={"arbitration": {"confidenceBand": "medium", "conflicts": []}},
    )
    assert "【置信】" in system
    assert "【目标年】" in system
    assert "【婚姻选项规则分】" not in system
    assert "【婚姻选项年份锚点】" not in system
    assert "【配偶星】" not in system
    assert "confidence 非 strong 时至少保留 2 项待选" in user
