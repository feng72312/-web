from __future__ import annotations

from app.core.liuyao.judgement.evidence import build_tiered_evidence_summary, partition_rag_hits


def test_partition_liuyao_tiered_buckets():
    tiered = partition_rag_hits(
        [
            {
                "source": "增删卜易",
                "excerpt": "用神旺相",
                "authorityTier": "S",
                "evidenceRole": "core_divination_judge",
            },
            {
                "source": "卜筮全书",
                "excerpt": "六神辅助",
                "authorityTier": "A",
                "evidenceRole": "encyclopedic_judge",
            },
            {
                "source": "卦例",
                "excerpt": "某占求财例",
                "caseOnly": True,
                "authorityTier": "S",
            },
            {
                "source": "B_现代技法/曲炜讲义",
                "excerpt": "现代解释",
                "authorityTier": "B",
                "judgmentPolicy": "explain_only",
            },
        ]
    )
    assert len(tiered.primaryEvidence) == 1
    assert len(tiered.secondaryEvidence) == 1
    assert len(tiered.caseReference) == 1
    assert len(tiered.modernSupport) == 1


def test_build_liuyao_tiered_summary_groups():
    tiered = partition_rag_hits(
        [
            {"source": "增删卜易", "excerpt": "用神", "authorityTier": "S", "evidenceRole": "core_divination_judge"},
            {"source": "曲炜", "excerpt": "讲义", "authorityTier": "B", "judgmentPolicy": "explain_only"},
        ]
    )
    summary = build_tiered_evidence_summary(tiered)
    labels = [group["label"] for group in summary.get("groups") or []]
    assert "主裁典籍" in labels
    assert "现代补充" in labels
    assert summary.get("total", 0) >= 2
