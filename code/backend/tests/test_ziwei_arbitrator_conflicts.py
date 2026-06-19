import pytest

from app.core.ziwei.judgement.arbitrator import ZiweiArbiter
from app.core.ziwei.judgement.models import ZiweiJudgeVerdict

pytest.importorskip("iztro_py")


def test_arbitrator_marks_soul_favorable_marriage_ji_conflict() -> None:
    verdicts = [
        ZiweiJudgeVerdict(
            role="star",
            summary="命宫主星偏吉",
            stance="favorable",
            confidenceBand="strong",
        ),
        ZiweiJudgeVerdict(
            role="palace",
            summary="夫妻宫化忌",
            stance="unfavorable",
            confidenceBand="weak",
        ),
        ZiweiJudgeVerdict(
            role="mutagen",
            summary="夫妻化忌入命",
            stance="unfavorable",
            confidenceBand="weak",
        ),
    ]
    result = ZiweiArbiter().arbitrate(verdicts, [], primary_evidence_count=2)
    assert result.conflicts
    assert any("分区" in item or "四化" in item for item in result.conflicts)


def test_arbitrator_caps_confidence_without_primary_evidence() -> None:
    verdicts = [
        ZiweiJudgeVerdict(
            role="star",
            summary="命宫紫微庙旺",
            stance="favorable",
            confidenceBand="strong",
        )
    ]
    result = ZiweiArbiter().arbitrate(verdicts, [], primary_evidence_count=0)
    assert result.confidenceScore <= 0.55
    assert any("主裁证据" in item for item in result.finalBoundaries)
