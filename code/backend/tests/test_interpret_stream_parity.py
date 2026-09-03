from __future__ import annotations

import json
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.core.agent.session_store import AgentSessionStore
from app.core.concurrency.interpret_limit import InterpretConcurrencyLimiter
from app.core.judgement.models import BaziJudgementReport
from app.core.quota.service import QuotaService
from app.core.quota.store import QuotaStore
from app.main import app

DEVICE = "stream-parity-device-001"
PAYLOAD = {
    "name": "命主",
    "calendarType": "solar",
    "year": 1990,
    "month": 5,
    "day": 15,
    "hour": 13,
    "minute": 30,
    "gender": 1,
    "fusion": False,
    "question": "请论此命主格局",
    "excerpts": [],
}
HEADERS = {"X-Device-Id": DEVICE, "X-Model-Id": "deepseek-chat"}


class FakeChat:
    enabled = True

    async def interpret(self, prompt: str, model_id: str | None = None) -> tuple[str, str]:
        return "FIXED TEXT", "sess-fixed"

    async def create_session(self) -> str:
        return "sess-stream"

    def set_bootstrap(self, session_id: str, bootstrap: str) -> None:
        return None

    def bind_chart(self, chart_key: str, session_id: str) -> None:
        return None

    async def send_stream(
        self,
        session_id: str,
        message: str,
        model_id: str | None = None,
    ) -> AsyncIterator[tuple[str, str | None]]:
        yield "FIXED ", None
        yield "TEXT", None
        yield "", "run-1"


def _parse_sse(text: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for block in text.split("\n\n"):
        line = next((item for item in block.split("\n") if item.startswith("data: ")), "")
        if not line:
            continue
        events.append(json.loads(line[6:]))
    return events


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    test_client = TestClient(app)
    app.state.quota_service = QuotaService(QuotaStore(tmp_path / "quota.db"))
    app.state.chat_orchestrator = FakeChat()
    app.state.session_store = AgentSessionStore()
    app.state.interpret_limiter = InterpretConcurrencyLimiter(5, 1.0)

    async def fake_run(self, chart, question: str = ""):  # noqa: ANN001
        return BaziJudgementReport()

    monkeypatch.setattr("app.api.router.BaziJudgementChain.run", fake_run)
    return test_client


def test_stream_fusion_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/v1/interpret/stream",
        json={**PAYLOAD, "fusion": True},
        headers=HEADERS,
    )
    assert response.status_code == 400


def test_stream_event_order_and_payload_parity(client: TestClient) -> None:
    before = client.get("/api/v1/quota/status", headers={"X-Device-Id": DEVICE}).json()
    remaining_before = before["tierQuotas"][0]["remaining"]

    non_stream = client.post("/api/v1/interpret", json=PAYLOAD, headers=HEADERS)
    assert non_stream.status_code == 200
    non_interp = non_stream.json()["interpretation"]

    after_one = client.get("/api/v1/quota/status", headers={"X-Device-Id": DEVICE}).json()
    assert after_one["tierQuotas"][0]["remaining"] == remaining_before - 1

    stream = client.post("/api/v1/interpret/stream", json=PAYLOAD, headers=HEADERS)
    assert stream.status_code == 200
    events = _parse_sse(stream.text)
    types = [event["type"] for event in events]
    assert types[0] == "stage"
    assert "delta" in types
    assert types[-1] == "done"
    assert types == (
        ["stage"] * types.count("stage")
        + ["delta"] * types.count("delta")
        + ["done"]
    )

    done = events[-1]
    stream_interp = done["interpretation"]
    for key in (
        "judgement",
        "tieredEvidence",
        "ruleIdRefs",
        "knowledgeEvidence",
        "segmentStats",
    ):
        assert key in stream_interp
    assert stream_interp["judgement"] == non_interp["judgement"]
    assert stream_interp["tieredEvidence"] == non_interp["tieredEvidence"]
    assert stream_interp["ruleIdRefs"] == non_interp["ruleIdRefs"]

    after_two = client.get("/api/v1/quota/status", headers={"X-Device-Id": DEVICE}).json()
    assert after_two["tierQuotas"][0]["remaining"] == remaining_before - 2
