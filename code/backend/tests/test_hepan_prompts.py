from __future__ import annotations

from app.core.agent.prompts_hepan import build_hepan_interpret_prompt


def _sample_hepan() -> dict:
    return {
        "scene": "partnership",
        "discipline": "bazi",
        "question": "请论两人商业合作互补性与风险",
        "summaryTags": ["日主五行相生"],
        "crossNotes": [
            {
                "id": "bazi_day_master_wuxing",
                "level": "fit",
                "dimension": "wuxing",
                "title": "主容五行相生",
                "detail": "甲木生丙火, 有助.",
                "source": "bazi",
            }
        ],
        "personA": {
            "name": "甲",
            "gender": 1,
            "baziChart": {
                "dayMaster": "甲",
                "input": {"gender": 1},
                "pillars": {"day": {"ganzhi": "甲子"}},
            },
        },
        "personB": {
            "name": "乙",
            "gender": 0,
            "baziChart": {
                "dayMaster": "丙",
                "input": {"gender": 0},
                "pillars": {"day": {"ganzhi": "丙午"}},
            },
        },
    }


def test_hepan_plain_prompt_forbids_chatty_opening() -> None:
    prompt = build_hepan_interpret_prompt(_sample_hepan(), [], [], style="plain")
    assert "禁止寒暄" in prompt
    assert "不要任何开场白" in prompt
    assert "你是八字合盘专家" not in prompt
    assert "你是紫微斗数合盘专家" not in prompt


def test_hepan_plain_prompt_starts_with_fit_section_instruction() -> None:
    prompt = build_hepan_interpret_prompt(_sample_hepan(), [], [], style="plain")
    assert "契合点" in prompt
    assert "报告体" in prompt
