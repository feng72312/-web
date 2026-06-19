from __future__ import annotations

from app.benchmark.ziwei_error_labels import (
    aggregate_ziwei_error_label_counts,
    infer_ziwei_error_labels,
)


def test_infer_ziwei_empty_prediction() -> None:
    labels = infer_ziwei_error_labels(gold="A", predicted="", judgement={})
    assert labels == ["empty_prediction"]


def test_infer_ziwei_correct_no_labels() -> None:
    labels = infer_ziwei_error_labels(
        gold="A",
        predicted="A",
        judgement={"arbitration": {"confidenceBand": "strong"}},
    )
    assert labels == []


def test_infer_ziwei_overconfident() -> None:
    labels = infer_ziwei_error_labels(
        gold="A",
        predicted="B",
        judgement={
            "topic": {"confidence": 0.8},
            "arbitration": {"confidenceBand": "strong"},
            "judges": [],
            "tieredEvidence": {"primaryEvidence": [{"source": "x", "excerpt": "y"}]},
        },
    )
    assert "overconfident_claim" in labels


def test_aggregate_ziwei_error_label_counts() -> None:
    counts = aggregate_ziwei_error_label_counts(
        [
            {"errorLabels": ["wrong_topic_class", "overconfident_claim"]},
            {"errorLabels": ["wrong_topic_class"]},
            {"errorLabels": []},
        ]
    )
    assert counts["wrong_topic_class"] == 2
    assert counts["overconfident_claim"] == 1
