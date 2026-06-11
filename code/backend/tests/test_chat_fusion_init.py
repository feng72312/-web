from __future__ import annotations

import pytest

pytest.importorskip("zoneinfo")

from fastapi.testclient import TestClient

from app.core.agent.prompts_fusion import build_fusion_chat_init_prompt
from app.main import app


def _sample_source(module_id: str, module_label: str, title: str) -> dict:
    return {
        "moduleId": module_id,
        "moduleLabel": module_label,
        "title": title,
        "question": "请论事业",
        "chartSnapshot": {
            "moduleHint": module_label,
            "input": {"name": "测试", "year": 1990, "month": 5, "day": 1},
        },
        "summaryPlain": "示例 AI 摘要",
        "summaryProfessional": "示例命理师摘要",
    }


def test_build_fusion_chat_init_prompt_includes_sources() -> None:
    prompt = build_fusion_chat_init_prompt(
        [
            _sample_source("01", "八字", "甲木命盘"),
            _sample_source("11", "紫微", "水二局"),
        ]
    )
    assert "八字" in prompt
    assert "紫微" in prompt
    assert "同向点" in prompt
    assert "冲突点" in prompt


def test_chat_init_fusion_rejects_single_source() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/chat/init/fusion",
        json={"sources": [_sample_source("01", "八字", "甲木命盘")]},
    )
    assert response.status_code == 422


def test_chat_init_fusion_creates_session() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/chat/init/fusion",
        json={
            "title": "融合分析 · 八字 + 紫微",
            "sources": [
                _sample_source("01", "八字", "甲木命盘"),
                _sample_source("11", "紫微", "水二局"),
            ],
        },
    )
    if response.status_code == 404:
        pytest.skip("chat orchestrator not configured in test environment")
    assert response.status_code == 200
    payload = response.json()
    assert payload["agentId"]
    assert payload["sourceCount"] == 2
    assert payload["scenario"] == "review_result"

    history = client.get(f"/api/v1/chat/history/{payload['agentId']}")
    assert history.status_code == 200
