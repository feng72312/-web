from __future__ import annotations

from app.core.utils.naming_engine import (
    compute_wuge,
    favored_wuxing_from_chart,
    radical_wuxing,
    shuli_luck,
    shuli_wuxing,
)


def test_shuli_wuxing_and_luck() -> None:
    assert shuli_wuxing(13) == "火"
    assert shuli_wuxing(18) == "金"
    assert shuli_luck(13) == "吉"
    assert shuli_luck(4) == "凶"


def test_radical_wuxing() -> None:
    assert radical_wuxing("氵") == "水"
    assert radical_wuxing("木") == "木"


def test_compute_wuge_single_surname() -> None:
    overrides = {"张": 11, "三": 3}
    result = compute_wuge("张", "三", stroke_overrides=overrides)
    grids = {row["grid"]: row["strokes"] for row in result["grids"]}
    assert grids["天格"] == 12
    assert grids["人格"] == 14
    assert grids["地格"] == 3
    assert grids["总格"] == 14


def test_favored_wuxing_from_chart() -> None:
    chart = {
        "dayMasterWuxing": "木",
        "wuxingCount": {"木": 4, "火": 1, "土": 1, "金": 1, "水": 1},
    }
    profile = favored_wuxing_from_chart(chart)
    assert profile["strength"] == "偏强"
    assert "火" in profile["favoredWuxing"]
