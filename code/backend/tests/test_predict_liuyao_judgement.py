from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

from app.benchmark.contest8_dataset import ContestQuestion
from app.benchmark.contest8_eval import predict_one_liuyao_only
from app.core.agent.deepseek import DeepSeekClient


def _question() -> ContestQuestion:
    return ContestQuestion(
        year=2024,
        person_id="p1",
        question_id="test-liuyao-q1",
        question="今年财运如何",
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


def test_predict_liuyao_only_uses_judgement_yong_shen():
    client = AsyncMock(spec=DeepSeekClient)
    client.chat_once = AsyncMock(return_value="A")

    with patch(
        "app.benchmark.contest8_eval.LiuyaoJudgementChain"
    ) as mock_chain_cls:
        mock_chain = mock_chain_cls.return_value
        mock_chain.run = AsyncMock(
            return_value=type(
                "Report",
                (),
                {
                    "to_dict": lambda self: {
                        "yongShen": {
                            "yongShen": "妻财",
                            "position": 4,
                            "source": "rule",
                            "confidence": 0.8,
                            "reason": "test",
                        },
                        "judges": [{"role": "wang_shuai", "summary": "旺"}] * 8,
                        "arbitration": {"confidenceBand": "medium"},
                        "tieredEvidence": {"primaryEvidence": []},
                        "tieredEvidenceSummary": {"note": "test"},
                    }
                },
            )()
        )
        result = asyncio.run(
            predict_one_liuyao_only(
                _question(),
                client,
                use_judgement=True,
                use_rag=False,
            )
        )

    assert result.liuyao_pred == "A"
    assert result.judgement.get("yongShen", {}).get("source") == "rule"
    assert result.error_labels == []
    client.chat_once.assert_awaited_once()
