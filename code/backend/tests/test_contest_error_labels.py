from __future__ import annotations

from app.benchmark.error_labels import ERROR_LABELS, infer_error_labels


def test_infer_case_overfit_from_coverage_signal() -> None:
    labels = infer_error_labels(
        gold="A",
        predicted="B",
        judgement={
            "coverage": {"caseOverreach": True},
            "tieredEvidence": {
                "caseReference": [{"excerpt": "x"}],
                "primaryEvidence": [],
            },
            "arbitration": {"confidenceBand": "medium"},
        },
    )
    assert labels[0] == "case_overfit"


def test_infer_case_overfit() -> None:
    labels = infer_error_labels(
        gold="A",
        predicted="B",
        judgement={
            "tieredEvidence": {
                "caseReference": [{"excerpt": "x"}],
                "primaryEvidence": [],
            },
            "arbitration": {"confidenceBand": "medium"},
        },
    )
    assert "case_overfit" in labels


def test_no_labels_when_correct() -> None:
    labels = infer_error_labels(gold="B", predicted="B")
    assert labels == []


def test_error_label_catalog() -> None:
    assert "wrong_tiaohou" in ERROR_LABELS
    assert "low_authority_override" in ERROR_LABELS
