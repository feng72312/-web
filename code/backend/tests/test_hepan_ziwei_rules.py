from __future__ import annotations

import pytest

from app.core.hepan.ziwei_rules import build_ziwei_cross_notes


def _palace(name: str, branch: str, stars):
    return {
        "name": name,
        "earthlyBranch": branch,
        "stemBranch": f"\u7532{branch}",
        "majorStars": [{"name": s, "brightness": "\u5e99", "type": "major"} for s in stars],
        "minorStars": [],
        "adjectiveStars": [],
    }


def _ziwei_chart(palaces: list[dict]) -> dict:
    return {
        "input": {"gender": 1},
        "meta": {"bureau": "\u6c34\u4e8c\u5c40", "soul": "\u5de8\u95e8"},
        "palaces": palaces,
    }


def test_ziwei_cross_notes_non_empty() -> None:
    base = [
        _palace("\u547d\u5bab", "\u5b50", ["\u7d2b\u5fae"]),
        _palace("\u592b\u59bb", "\u5348", ["\u592a\u9633"]),
        _palace("\u798f\u5fb7", "\u8fb0", ["\u5929\u540c"]),
    ]
    chart_a = _ziwei_chart(base)
    chart_b = _ziwei_chart(
        [
            _palace("\u547d\u5bab", "\u4e11", ["\u5929\u673a"]),
            _palace("\u592b\u59bb", "\u672a", ["\u592a\u9633"]),
            _palace("\u798f\u5fb7", "\u9149", ["\u592a\u9633"]),
        ]
    )
    notes = build_ziwei_cross_notes(chart_a, chart_b, "marriage")
    assert notes
    assert all(n["source"] == "ziwei" for n in notes)


@pytest.mark.skipif(True, reason="requires iztro engine integration")
def test_ziwei_engine_integration() -> None:
    pass
