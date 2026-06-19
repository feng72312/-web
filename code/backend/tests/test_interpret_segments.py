from __future__ import annotations

from app.core.interpret.segments import build_interpret_segments


def test_build_interpret_segments_anchored_and_inference() -> None:
    judgement = {
        "evidenceChain": [
            {
                "ruleId": "tiaohou:甲:寅",
                "primaryClassic": "穷通宝鉴",
                "conclusion": "调候: 春木需火",
            }
        ],
        "arbitration": {
            "judgeOpinions": [
                {
                    "role": "geju",
                    "classic": "子平真诠",
                    "ruleIds": ["geju:month:正官"],
                    "summary": "月令正官",
                }
            ]
        },
    }
    refs = [
        {"ruleId": "tiaohou:甲:寅", "classic": "穷通宝鉴"},
        {"ruleId": "geju:month:正官", "classic": "子平真诠"},
    ]
    summary = (
        "格局以正官为主, 宜守正用印. [ruleId:geju:month:正官]\n\n"
        "调候需火助身. [ruleId:tiaohou:甲:寅]\n\n"
        "(推断) 近年宜稳健, 勿急进."
    )
    bundle = build_interpret_segments(
        summary,
        judgement,
        rule_id_refs=refs,
        confidence_band="strong",
    )
    segments = bundle["segments"]
    assert len(segments) == 3
    assert segments[0]["kind"] == "anchored"
    assert segments[0]["ruleIdRefs"][0]["ruleId"] == "geju:month:正官"
    assert segments[2]["kind"] == "inference"
    assert bundle["stats"]["anchored"] == 2
    assert bundle["stats"]["inference"] == 1
    assert bundle["confidenceBand"] == "strong"


def test_build_interpret_segments_downgrades_when_mostly_inference() -> None:
    bundle = build_interpret_segments(
        "段落一.\n\n段落二.\n\n(推断) 段落三.",
        None,
        confidence_band="strong",
    )
    assert bundle["stats"]["inference"] == 3
    assert bundle["confidenceBand"] == "medium"


def test_build_interpret_segments_strips_inline_tags() -> None:
    bundle = build_interpret_segments(
        "日主偏弱需印比. [ruleId:qishi:dominant:木]",
        None,
        rule_id_refs=[{"ruleId": "qishi:dominant:木"}],
    )
    segment = bundle["segments"][0]
    assert "[ruleId:" not in segment["text"]
    assert segment["ruleIdRefs"][0]["verified"] is True
