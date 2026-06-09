from app.core.consensus.confidence import compute_confidence
from app.core.consensus.engine import build_consensus_from_channels
from app.core.fusion.merge_bazi_ziwei import merge_bazi_ziwei_stances
from app.core.fusion.models import ChannelVerdict


def test_merge_bazi_ziwei_stances_agree() -> None:
    ch = merge_bazi_ziwei_stances("吉", "吉", "综合运势")
    assert ch == "agree"


def test_merge_bazi_ziwei_stances_marriage() -> None:
    ch = merge_bazi_ziwei_stances("凶", "吉", "命主婚姻状况如何")
    assert ch == "ziwei"


def test_consensus_strong_when_agree() -> None:
    bazi = ChannelVerdict(channel="bazi", summary="命局偏旺", stance="吉", available=True)
    ziwei = ChannelVerdict(channel="ziwei", summary="夫妻宫稳", stance="吉", available=True)
    result = build_consensus_from_channels(
        "问事业",
        [bazi, ziwei],
        fusion_mode="chart",
        lead_discipline="agree",
        merged_summary="综合吉",
    )
    assert result.confidence_band in ("strong", "medium")
    assert len(result.consensus_points) >= 1


def test_consensus_conflict_points() -> None:
    bazi = ChannelVerdict(channel="bazi", summary="a", stance="吉", available=True)
    ziwei = ChannelVerdict(channel="ziwei", summary="b", stance="凶", available=True)
    result = build_consensus_from_channels(
        "问事",
        [bazi, ziwei],
        fusion_mode="chart",
        lead_discipline="bazi",
        merged_summary="分述",
    )
    assert len(result.conflict_points) >= 1


def test_compute_confidence_empty() -> None:
    score, band = compute_confidence([], lead_available=False)
    assert score == 0.0
    assert band == "weak"
