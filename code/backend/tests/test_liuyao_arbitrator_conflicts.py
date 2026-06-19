from __future__ import annotations

from app.core.liuyao.judgement.arbitrator import LiuyaoArbiter
from app.core.liuyao.judgement.judgement_models import LiuyaoJudgeVerdict
from app.core.liuyao.judgement.judges import DongBianJudge, ShengKeJudge, WangShuaiJudge


def _chart_yue_po() -> dict:
    return {
        "monthJian": "子",
        "dayGan": "甲",
        "dayChen": "戌",
        "shiYing": {"shi": 3, "ying": 6},
        "benGua": {"name": "火水未济", "lower": "坎", "upper": "离", "palace": "离"},
        "bianGua": None,
        "movingLines": [],
        "lines": [
            {
                "position": 4,
                "branch": "午",
                "stem": "己",
                "liuqin": "妻财",
                "liushen": "青龙",
                "isMoving": False,
            }
        ],
        "meta": {"lineValues": [7, 8, 7, 8, 7, 8]},
    }


def test_wang_shuai_yue_po_flags():
    from app.core.liuyao.judgement.chart_enrich import enrich_chart_for_judgement

    chart = enrich_chart_for_judgement(_chart_yue_po())
    verdict = WangShuaiJudge().judge(chart, {"yongShen": "妻财", "position": 4})
    assert verdict.flags.get("yuePo") is True
    assert verdict.stance == "unfavorable"
    assert "月破" in verdict.summary


def test_arbitrator_conflict_wang_favorable_sheng_unfavorable():
    arbiter = LiuyaoArbiter()
    verdicts = [
        LiuyaoJudgeVerdict(
            role="wang_shuai",
            summary="用神得月建之气偏旺",
            stance="favorable",
            confidenceBand="strong",
        ),
        LiuyaoJudgeVerdict(
            role="sheng_ke",
            summary="忌神发动克用神",
            stance="unfavorable",
            confidenceBand="weak",
        ),
    ]
    result = arbiter.arbitrate(verdicts, [], primary_evidence_count=1)
    assert result.conflicts
    assert any("有基础但受阻" in item for item in result.conflicts)


def test_dong_bian_illness_liu_chong_boundary():
    chart = {
        "movingLines": [1, 4],
        "riskFlags": {"benLiuChong": True, "bianLiuChong": False},
        "lines": [
            {"position": 1, "isMoving": True, "dongBianTarget": {"huitou": "化回头克"}},
        ],
    }
    verdict = DongBianJudge().judge(
        chart,
        {"position": 1, "yongShen": "官鬼"},
        topic_id="illness",
    )
    assert "六冲" in verdict.summary
    assert "近病" in verdict.boundary or "久病" in verdict.boundary


def test_no_primary_evidence_caps_confidence():
    arbiter = LiuyaoArbiter()
    verdicts = [
        LiuyaoJudgeVerdict(
            role="wang_shuai",
            summary="用神偏旺",
            stance="favorable",
            confidenceBand="strong",
        )
    ]
    result = arbiter.arbitrate(verdicts, [], primary_evidence_count=0)
    assert result.confidenceScore <= 0.55
    assert any("缺少主裁证据" in b for b in result.finalBoundaries)
