from __future__ import annotations

from typing import Literal

from app.core.fusion.models import ChannelVerdict

ConfidenceBand = Literal["strong", "medium", "weak"]


def _normalize_stance(stance: str) -> str:
    return (stance or "").strip()


def score_channel_agreement(channels: list[ChannelVerdict]) -> float:
    """0.0-1.0 agreement score among available channels with non-empty stance."""
    available = [
        c for c in channels if c.available and _normalize_stance(c.stance) not in ("", "未定")
    ]
    if len(available) <= 1:
        return 1.0 if available else 0.0
    stances = [_normalize_stance(c.stance) for c in available]
    if len(set(stances)) == 1:
        return 1.0
    if len(set(stances)) == len(stances):
        return 0.0
    return 0.5


def evidence_score(channels: list[ChannelVerdict]) -> float:
    total_excerpts = sum(len(c.excerpts) for c in channels if c.available)
    if total_excerpts >= 3:
        return 1.0
    if total_excerpts >= 1:
        return 0.6
    return 0.2


def compute_confidence(
    channels: list[ChannelVerdict],
    *,
    lead_available: bool = True,
) -> tuple[float, ConfidenceBand]:
    if not lead_available:
        return 0.0, "weak"
    agreement = score_channel_agreement(channels)
    evidence = evidence_score(channels)
    available_count = sum(1 for c in channels if c.available)
    coverage = min(1.0, available_count / max(len(channels), 1))
    score = round(0.5 * agreement + 0.3 * evidence + 0.2 * coverage, 3)
    if score >= 0.75:
        band: ConfidenceBand = "strong"
    elif score >= 0.45:
        band = "medium"
    else:
        band = "weak"
    return score, band
