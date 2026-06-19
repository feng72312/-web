from __future__ import annotations

from app.core.knowledge.qishi_context import (
    build_qishi_lookup_keys,
    build_qishi_prompt_block,
)


def _sample_chart() -> dict:
    return {
        "dayMaster": "甲",
        "pillars": {
            "month": {"gan": "丙", "zhi": "寅", "shishenGan": "食神"},
            "day": {"gan": "甲", "zhi": "子"},
        },
        "wuxingCount": {"木": 4, "火": 2, "土": 1, "金": 0, "水": 1},
    }


def test_build_qishi_lookup_keys_spread() -> None:
    keys = build_qishi_lookup_keys(_sample_chart())
    categories = {row.get("category") for row in keys}
    assert "tiyong" in categories or "tongguan" in categories


def test_build_qishi_prompt_block_fallback() -> None:
    block = build_qishi_prompt_block(_sample_chart())
    assert "滴天髓气势" in block
    assert "ruleId:" in block
