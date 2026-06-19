from __future__ import annotations

from app.core.judgement.evidence import partition_rag_hits


def test_partition_primary_evidence() -> None:
    tiered = partition_rag_hits(
        [
            {"excerpt": "a", "evidenceRole": "tiaohou_judge", "classic": "穷通宝鉴"},
            {"excerpt": "b", "evidenceRole": "case_reference"},
            {"excerpt": "c", "evidenceRole": "low_trust"},
        ]
    )
    assert len(tiered.primaryEvidence) == 1
    assert len(tiered.caseReference) == 1
    assert len(tiered.excludedOrLowTrust) == 1
