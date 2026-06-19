from app.core.ziwei.judgement.evidence import (
    _bucket_hit,
    _rank_hit,
    empty_tiered_evidence,
    partition_rag_hits,
)


def test_partition_rag_hits_five_buckets() -> None:
    hits = [
        {
            "source": "S1",
            "excerpt": "a",
            "authorityTier": "S",
            "evidenceRole": "primary_classic",
        },
        {
            "source": "B1",
            "excerpt": "b",
            "authorityTier": "B",
            "judgmentPolicy": "explain_only",
        },
        {
            "source": "C1",
            "excerpt": "c",
            "school": "feixing",
            "authorityTier": "B",
        },
        {
            "source": "case1",
            "excerpt": "d",
            "textRole": "case",
            "authorityTier": "A",
        },
        {
            "source": "D1",
            "excerpt": "e",
            "authorityTier": "D",
            "judgmentPolicy": "exclude_from_core_judge",
        },
    ]
    tiered = partition_rag_hits(hits)
    payload = tiered.model_dump()
    assert len(payload["primaryEvidence"]) == 1
    assert len(payload["secondaryEvidence"]) == 1
    assert len(payload["schoolCommentary"]) == 1
    assert len(payload["caseReference"]) == 1
    assert len(payload["excludedOrUnreadable"]) == 1


def test_case_text_role_downranked_in_rank_hit() -> None:
    base = {"score": 1.0, "authorityTier": "A", "textRole": "original"}
    case = {"score": 1.0, "authorityTier": "A", "textRole": "case"}
    assert _rank_hit(case) < _rank_hit(base)


def test_empty_tiered_evidence_has_all_keys() -> None:
    payload = empty_tiered_evidence()
    assert set(payload.keys()) == {
        "primaryEvidence",
        "secondaryEvidence",
        "schoolCommentary",
        "caseReference",
        "excludedOrUnreadable",
    }


def test_bucket_hit_respects_evidence_bucket_from_rag() -> None:
    assert _bucket_hit({"evidenceBucket": "primaryEvidence"}) == "primaryEvidence"
    assert _bucket_hit({"evidenceBucket": "caseReference"}) == "caseReference"
