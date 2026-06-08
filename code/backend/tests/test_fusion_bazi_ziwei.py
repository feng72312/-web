from __future__ import annotations

from app.core.fusion.merge_bazi_ziwei import merge_bazi_ziwei_letters, theme_prefers_ziwei


def test_merge_agree() -> None:
    letter, ch = merge_bazi_ziwei_letters("B", "B", "2011年发生何事")
    assert letter == "B"
    assert ch == "agree"


def test_merge_liunian_bazi() -> None:
    letter, ch = merge_bazi_ziwei_letters("A", "C", "2011年发生何事")
    assert letter == "A"
    assert ch == "bazi"


def test_merge_marriage_ziwei() -> None:
    letter, ch = merge_bazi_ziwei_letters("A", "C", "命主婚姻状况如何")
    assert letter == "C"
    assert ch == "ziwei"


def test_theme_prefers_ziwei() -> None:
    assert theme_prefers_ziwei("健康如何") is True
    assert theme_prefers_ziwei("2020年发生何事") is False
