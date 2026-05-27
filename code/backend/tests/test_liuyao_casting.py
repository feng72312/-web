from app.core.liuyao.casting import coin_tails_to_value, cast_from_numbers
from app.core.liuyao.trigrams import mod6, mod8


def test_coin_tails_mapping():
    assert coin_tails_to_value(3) == 9
    assert coin_tails_to_value(0) == 6
    assert coin_tails_to_value(2) == 8
    assert coin_tails_to_value(1) == 7


def test_mod_helpers():
    assert mod8(8) == 8
    assert mod8(16) == 8
    assert mod6(6) == 6
    assert mod6(12) == 6


def test_number_cast_single():
    lines, note = cast_from_numbers([24])
    assert len(lines) == 6
    assert all(value in (6, 7, 8, 9) for value in lines)
    assert "单数" in note
