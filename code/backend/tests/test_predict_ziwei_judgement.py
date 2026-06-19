from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

from app.benchmark.contest8_dataset import ContestQuestion
from app.benchmark.contest8_eval import predict_one_ziwei_only
from app.core.agent.deepseek import DeepSeekClient


def _question() -> ContestQuestion:
    return ContestQuestion(
        year=2024,
        person_id="p1",
        question_id="test-ziwei-q1",
        question="命主婚姻状况如何",
        options=["A.好", "B.一般", "C.差", "D.不确定"],
        answer="A",
        birth={
            "year": 1990,
            "month": 3,
            "day": 15,
            "hour": 10,
            "minute": 0,
            "second": 0,
        },
        gender="男",
        person_name="test",
        extra_info={},
    )


def test_predict_ziwei_only_uses_judgement_chain():
    client = AsyncMock(spec=DeepSeekClient)
    client.chat_once = AsyncMock(return_value="A")

    with patch("app.benchmark.contest8_eval.ZiweiJudgementChain") as mock_chain_cls:
        mock_chain = mock_chain_cls.return_value
        mock_chain.run = AsyncMock(
            return_value=type(
                "Report",
                (),
                {
                    "to_dict": lambda self: {
                        "topic": {
                            "topicId": "marriage",
                            "topicLabel": "婚恋感情",
                            "targetPalaces": ["夫妻"],
                            "confidence": 0.8,
                        },
                        "judges": [{"role": role, "summary": "ok"} for role in (
                            "topic",
                            "palace",
                            "star",
                            "mutagen",
                            "pattern",
                            "limit",
                            "cross_school",
                        )],
                        "steps": [{"id": f"s{i}", "label": "x", "status": "ok", "summary": ""} for i in range(7)],
                        "arbitration": {"confidenceBand": "medium"},
                        "tieredEvidence": {"primaryEvidence": []},
                        "tieredEvidenceSummary": {"note": "test"},
                        "enrichedChart": {"palaces": [{"name": "命宫"}]},
                    }
                },
            )()
        )
        result = asyncio.run(
            predict_one_ziwei_only(
                _question(),
                client,
                use_judgement=True,
                use_rag=False,
                use_case_rag=False,
            )
        )

    assert result.ziwei_pred == "A"
    assert result.judgement.get("topic", {}).get("topicId") == "marriage"
    assert result.error_labels == []
    client.chat_once.assert_awaited_once()
