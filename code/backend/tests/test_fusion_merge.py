from __future__ import annotations

from app.core.fusion.classify import classify_question
from app.core.fusion.merge import merge_mcq_letters, merge_verdicts
from app.core.fusion.models import ChannelVerdict


def test_classify_event_detail() -> None:
    assert classify_question("命主在哪一年结婚") == "event_detail"


def test_classify_life_outline() -> None:
    assert classify_question("论格局用神与一生大势") == "life_outline"


def test_classify_mixed() -> None:
    q = "论格局用神, 并问2010年是否离婚"
    assert classify_question(q) == "mixed"


def test_merge_prefers_liuyao_on_detail_conflict() -> None:
    bazi = ChannelVerdict("bazi", "命", "吉", available=True)
    liuyao = ChannelVerdict("liuyao", "卦", "凶", available=True)
    fusion = merge_verdicts("哪年结婚", bazi, liuyao)
    assert fusion.agreed is False
    assert fusion.preferred_channel == "liuyao"
    assert "此事重卦" in fusion.merged_summary or "卦象" in fusion.merged_summary


def test_merge_mcq_letters_detail() -> None:
    letter, scope, ch = merge_mcq_letters("A", "B", "哪年结婚")
    assert letter == "B"
    assert scope == "event_detail"
    assert ch == "liuyao"


def test_merge_prefers_bazi_on_outline_conflict() -> None:
    bazi = ChannelVerdict("bazi", "命", "吉", available=True)
    liuyao = ChannelVerdict("liuyao", "卦", "凶", available=True)
    fusion = merge_verdicts("论一生格局", bazi, liuyao)
    assert fusion.preferred_channel == "bazi"
