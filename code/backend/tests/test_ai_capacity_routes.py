from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.agent.session_store import AgentSessionStore
from app.core.concurrency.interpret_limit import InterpretConcurrencyLimiter
from app.core.quota.service import QuotaService
from app.core.quota.store import QuotaStore
from app.main import app


class CapacityAwareChat:
    enabled = True

    def __init__(self, limiter: InterpretConcurrencyLimiter) -> None:
        self._limiter = limiter
        self.active_seen = 0

    async def send_stream(
        self,
        session_id: str,
        message: str,
        model_id: str | None = None,
    ) -> AsyncIterator[tuple[str, str | None]]:
        self.active_seen = self._limiter.snapshot()["active"]
        yield "测试", None
        yield "", "run-capacity"


def test_chat_stream_holds_shared_ai_capacity_until_stream_finishes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    limiter = InterpretConcurrencyLimiter(5, 1.0, 10)
    chat = CapacityAwareChat(limiter)
    monkeypatch.setattr(app.state, "interpret_limiter", limiter, raising=False)
    monkeypatch.setattr(app.state, "chat_orchestrator", chat, raising=False)
    monkeypatch.setattr(app.state, "session_store", AgentSessionStore(), raising=False)
    monkeypatch.setattr(
        app.state,
        "quota_service",
        QuotaService(QuotaStore(tmp_path / "quota.db")),
        raising=False,
    )

    response = TestClient(app).post(
        "/api/v1/chat/stream",
        json={
            "agentId": "capacity-session-001",
            "message": "请解读这个八字",
            "model": "deepseek-chat",
        },
        headers={
            "X-Device-Id": "capacity-route-device-001",
            "X-Model-Id": "deepseek-chat",
        },
    )

    assert response.status_code == 200
    assert chat.active_seen == 1
    assert limiter.snapshot()["active"] == 0
