from __future__ import annotations

from app.core.interpret.segments import build_interpret_segments


def test_low_anchor_ratio_downgrades_confidence() -> None:
    summary = "这是一段无锚点的推断性文字.\n\n另一段也没有 ruleId."
    bundle = build_interpret_segments(summary, None, confidence_band="strong")
    assert bundle["stats"]["anchoredRatio"] < 0.3
    assert bundle["confidenceBand"] in ("medium", "weak")


def test_router_style_guard_note() -> None:
    bundle = build_interpret_segments(
        "专业断语 [ruleId:tiaohou:甲:寅]",
        {
            "evidenceChain": [
                {"ruleId": "tiaohou:甲:寅", "conclusion": "调候:test", "primaryClassic": "穷通"},
            ],
        },
        confidence_band="strong",
    )
    assert bundle["stats"]["anchored"] >= 1
