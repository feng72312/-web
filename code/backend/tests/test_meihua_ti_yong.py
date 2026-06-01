from app.core.meihua.ti_yong import build_chart_parts, resolve_ti_yong


def test_static_lower_ti_upper_yong():
    lines = [7, 7, 7, 8, 8, 8]
    ti, yong, moving, is_static, _ = resolve_ti_yong(lines)
    assert is_static is True
    assert moving == []
    assert ti.name == "乾"
    assert yong.name == "坤"


def test_moving_in_lower():
    lines = [7, 7, 9, 8, 8, 8]
    ti, yong, moving, is_static, _ = resolve_ti_yong(lines)
    assert is_static is False
    assert moving == [3]
    assert yong.name == "乾"
    assert ti.name == "坤"


def test_moving_in_upper():
    lines = [7, 7, 7, 8, 8, 9]
    ti, yong, moving, is_static, _ = resolve_ti_yong(lines)
    assert moving == [6]
    assert yong.name == "艮"
    assert ti.name == "乾"


def test_override_moving_position():
    lines = [7, 7, 7, 7, 7, 7]
    parts = build_chart_parts(lines, moving_override=5)
    assert parts["moving"] == [5]
    assert parts["is_static"] is False
    assert parts["yong"].name == "乾"
    assert parts["ti"].name == "乾"
