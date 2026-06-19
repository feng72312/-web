from __future__ import annotations

from app.benchmark.liuyao_error_labels import (
    aggregate_error_label_counts,
    infer_liuyao_error_labels,
)


def test_empty_prediction_label():
    labels = infer_liuyao_error_labels(gold="A", predicted="", judgement={})
    assert labels == ["empty_prediction"]


def test_correct_answer_no_labels():
    labels = infer_liuyao_error_labels(
        gold="B",
        predicted="B",
        judgement={"arbitration": {"confidenceBand": "strong"}},
    )
    assert labels == []


def test_wrong_yong_shen_ai_source():
    labels = infer_liuyao_error_labels(
        gold="A",
        predicted="C",
        judgement={
            "yongShen": {"source": "ai", "confidence": 0.8},
            "arbitration": {"confidenceBand": "medium"},
        },
    )
    assert "wrong_yong_shen" in labels


def test_case_overfit_from_summary():
    labels = infer_liuyao_error_labels(
        gold="A",
        predicted="D",
        judgement={
            "tieredEvidenceSummary": {"caseOverreachRisk": True},
            "tieredEvidence": {"caseReference": [{"source": "x"}], "primaryEvidence": []},
            "arbitration": {"confidenceBand": "medium"},
        },
    )
    assert "case_overfit" in labels


def test_ignore_kong_po_when_strong_confidence():
    labels = infer_liuyao_error_labels(
        gold="A",
        predicted="B",
        judgement={
            "judges": [
                {
                    "role": "wang_shuai",
                    "flags": {"yuePo": True, "xunKong": False},
                }
            ],
            "arbitration": {"confidenceBand": "strong"},
        },
    )
    assert "ignore_kong_po" in labels


def test_aggregate_error_label_counts():
    counts = aggregate_error_label_counts(
        [
            {"errorLabels": ["wrong_yong_shen", "overconfident_claim"]},
            {"errorLabels": ["wrong_yong_shen"]},
            {"errorLabels": []},
        ]
    )
    assert counts["wrong_yong_shen"] == 2
    assert counts["overconfident_claim"] == 1
