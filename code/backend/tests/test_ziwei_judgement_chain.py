import asyncio

import pytest

from app.core.ziwei.engine import ZiweiEngine
from app.core.ziwei.judgement.chain import ZiweiJudgementChain
from app.core.ziwei.judgement.pattern_judge import PatternJudge
from app.core.ziwei.models import ZiweiInput
from app.core.ziwei.rules import ZiweiRules

pytest.importorskip("iztro_py")


def test_judgement_chain_runs_all_core_judges() -> None:
    engine = ZiweiEngine()
    chart = engine.chart(
        ZiweiInput(
            calendar_type="solar",
            year=1990,
            month=5,
            day=15,
            hour=11,
            minute=30,
            gender=1,
            detail_level="pro",
            question="今年事业如何",
            rules=ZiweiRules(),
        )
    ).to_dict()

    async def _run():
        return await ZiweiJudgementChain(use_rag=False).run(chart, question="今年事业如何")

    report = asyncio.run(_run())
    payload = report.to_dict()
    roles = {row["role"] for row in payload.get("judges") or []}
    assert roles >= {"topic", "palace", "star", "mutagen", "pattern", "limit", "cross_school"}
    assert len(payload.get("steps") or []) >= 6
    assert payload.get("arbitration")


def test_pattern_judge_rejects_sha_po_lang_without_three_stars() -> None:
    chart = {
        "palaces": [
            {
                "name": "命宫",
                "majorStars": [{"name": "破军", "brightness": "陷"}],
            },
            {"name": "迁移", "majorStars": []},
            {"name": "财帛", "majorStars": [{"name": "天府", "brightness": "旺"}]},
            {"name": "官禄", "majorStars": []},
        ]
    }
    verdict = PatternJudge().judge(chart)
    assert "不成立杀破狼" in verdict.summary
