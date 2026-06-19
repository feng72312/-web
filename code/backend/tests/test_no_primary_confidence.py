from __future__ import annotations

from app.core.judgement.arbitrator import apply_no_primary_confidence_cap
from app.core.judgement.models import ArbitrationResult, JudgeVerdict


def test_downgrade_when_no_primary_evidence() -> None:
    arbitration = ArbitrationResult(
        judgeOpinions=[
            JudgeVerdict(role="tiaohou", classic="穷通", summary="test", confidenceBand="strong"),
        ],
        confidenceScore=0.82,
        confidenceBand="strong",
    )
    capped = apply_no_primary_confidence_cap(arbitration, 0)
    assert capped.confidenceBand == "medium"
    assert capped.confidenceScore <= 0.45


def test_keep_when_primary_exists() -> None:
    arbitration = ArbitrationResult(
        confidenceScore=0.82,
        confidenceBand="strong",
    )
    capped = apply_no_primary_confidence_cap(arbitration, 3)
    assert capped.confidenceBand == "strong"
    assert capped.confidenceScore == 0.82
