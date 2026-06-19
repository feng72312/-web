from __future__ import annotations

from app.core.agent.prompts_contest import build_contest_mcq_parts
from app.core.knowledge.tiaohou_context import build_tiaohou_prompt_block

SAMPLE_CHART = {
    "dayMaster": "甲",
    "dayMasterWuxing": "木",
    "wuxingCount": {"木": 2, "火": 1, "土": 2, "金": 1, "水": 2},
    "pillars": {
        "year": {"gan": "甲", "zhi": "子", "shishenGan": "比肩"},
        "month": {"gan": "丙", "zhi": "寅", "shishenGan": "食神"},
        "day": {"gan": "甲", "zhi": "午", "shishenGan": ""},
        "hour": {"gan": "乙", "zhi": "亥", "shishenGan": "劫财"},
    },
    "dayun": [{"ganzhi": "丁卯", "startAge": 8, "endAge": 17, "startYear": 1990}],
}


def test_build_tiaohou_prompt_block_contains_core_fields() -> None:
    block = build_tiaohou_prompt_block(SAMPLE_CHART)
    if not block:
        return
    assert "穷通宝鉴调候" in block
    assert "日干甲" in block
    assert "月支寅" in block
    assert "透干" in block


def test_contest_prompt_includes_tiaohou_block() -> None:
    system, _user = build_contest_mcq_parts(
        SAMPLE_CHART,
        "此命事业如何?",
        ["A. 选项一", "B. 选项二", "C. 选项三", "D. 选项四"],
        use_option_elimination=True,
    )
    if "穷通宝鉴调候" in system:
        assert "调候" in system
