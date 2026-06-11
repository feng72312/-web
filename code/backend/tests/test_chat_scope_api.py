from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("zoneinfo")

from fastapi.testclient import TestClient

from app.core.agent.chat_scope import SCOPE_REFUSAL
from app.core.quota.keys import TIER_FREE_DAILY_LIMITS
from app.core.quota.service import QuotaService
from app.core.quota.store import QuotaStore
from app.main import app


def test_chat_stream_rejects_off_topic_without_quota(tmp_path: Path) -> None:
    store = QuotaStore(tmp_path / "quota.db")
    app.state.quota_service = QuotaService(store)
    device = "chat-scope-device-001"
    client = TestClient(app)

    before = client.get("/api/v1/quota/status", headers={"X-Device-Id": device}).json()
    before_remaining = before["tierQuotas"][0]["remaining"]

    response = client.post(
        "/api/v1/chat/stream",
        json={"agentId": "test-agent", "message": "用 python 写一个爬虫脚本"},
        headers={"X-Device-Id": device, "X-Model-Id": "deepseek-chat"},
    )

    if response.status_code == 404:
        pytest.skip("chat orchestrator not configured in test environment")

    assert response.status_code == 400
    assert SCOPE_REFUSAL in response.text

    after = client.get("/api/v1/quota/status", headers={"X-Device-Id": device}).json()
    after_remaining = after["tierQuotas"][0]["remaining"]
    assert after_remaining == before_remaining == TIER_FREE_DAILY_LIMITS["小师傅"]
