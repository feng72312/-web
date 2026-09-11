from __future__ import annotations

from fastapi.testclient import TestClient

from app.api.router import get_chat_orchestrator, get_session_store
from app.core.agent.chat_scope import is_message_in_scope_for_session
from app.core.agent.session_store import AgentSessionStore
from app.core.personas.prompts import build_persona_chat_bootstrap
from app.core.personas.catalog import get_persona_catalog
from app.core.personas.registry import get_persona_registry
from app.main import app


class FakeChat:
    enabled = True

    def __init__(self, store: AgentSessionStore) -> None:
        self.store = store
        self.bootstrap = ""

    async def create_session(self) -> str:
        self.store.create("persona-session")
        return "persona-session"

    def set_bootstrap(self, session_id: str, bootstrap: str) -> None:
        self.bootstrap = bootstrap
        self.store.set_bootstrap(session_id, bootstrap)


def test_persona_catalog_and_detail_are_public() -> None:
    client = TestClient(app)
    catalog = client.get("/api/v1/personas")
    assert catalog.status_code == 200
    assert catalog.json()["total"] == 165
    assert len(catalog.json()["categories"]) == 18

    detail = client.get("/api/v1/personas/wang-yangming")
    assert detail.status_code == 200
    payload = detail.json()
    assert payload["sources"]
    assert payload["starters"]
    assert payload["license"]["name"] == "MIT"


def test_catalog_filters_and_public_framework_detail() -> None:
    client = TestClient(app)
    category = client.get("/api/v1/personas", params={"category": "chinese-philosophers", "limit": 200})
    assert category.status_code == 200
    assert category.json()["total"] == 14
    assert {item["categoryId"] for item in category.json()["personas"]} == {"chinese-philosophers"}

    search = client.get("/api/v1/personas", params={"query": "renzhengfei"})
    assert search.status_code == 200
    assert search.json()["personas"][0]["name"] == "任正非"
    assert search.json()["personas"][0]["interactionMode"] == "public_framework"


def test_persona_init_uses_server_metadata_and_bootstrap() -> None:
    store = AgentSessionStore()
    fake = FakeChat(store)
    app.dependency_overrides[get_chat_orchestrator] = lambda: fake
    app.dependency_overrides[get_session_store] = lambda: store
    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/chat/init/persona",
            json={
                "personaId": "wang-yangming",
                "initialPrompt": "我想讨论知行合一",
                "sessionKind": "divination",
                "interactionMode": "historical_simulation",
            },
        )
        assert response.status_code == 200
        assert response.json()["agentId"] == "persona-session"
        assert store.get_metadata("persona-session") == {
            "session_kind": "persona",
            "persona_id": "wang-yangming",
            "interaction_mode": "historical_simulation",
        }
        assert "AI 思想模拟" in fake.bootstrap
        assert "知行合一" in fake.bootstrap
        assert "《传习录》" in fake.bootstrap
    finally:
        app.dependency_overrides.clear()


def test_persona_init_rejects_unknown_persona() -> None:
    store = AgentSessionStore()
    fake = FakeChat(store)
    app.dependency_overrides[get_chat_orchestrator] = lambda: fake
    app.dependency_overrides[get_session_store] = lambda: store
    try:
        response = TestClient(app).post(
            "/api/v1/chat/init/persona", json={"personaId": "unknown"}
        )
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_public_framework_mode_is_server_selected() -> None:
    store = AgentSessionStore()
    fake = FakeChat(store)
    app.dependency_overrides[get_chat_orchestrator] = lambda: fake
    app.dependency_overrides[get_session_store] = lambda: store
    try:
        response = TestClient(app).post(
            "/api/v1/chat/init/persona",
            json={"personaId": "renzhengfei", "interactionMode": "historical_simulation"},
        )
        assert response.status_code == 200
        assert response.json()["interactionMode"] == "public_framework"
        assert store.get_metadata("persona-session")["interaction_mode"] == "public_framework"
        assert "不得冒充" in fake.bootstrap
        assert "第一人称" in fake.bootstrap
    finally:
        app.dependency_overrides.clear()


def test_unavailable_persona_is_rejected_before_session_creation() -> None:
    catalog = get_persona_catalog()
    record = catalog.get_record("renzhengfei")
    assert record is not None
    original_status = record["availability"]
    original_reason = record["availabilityReason"]
    record["availability"] = "review_required"
    record["availabilityReason"] = "license review pending"
    store = AgentSessionStore()
    fake = FakeChat(store)
    app.dependency_overrides[get_chat_orchestrator] = lambda: fake
    app.dependency_overrides[get_session_store] = lambda: store
    try:
        response = TestClient(app).post("/api/v1/chat/init/persona", json={"personaId": "renzhengfei"})
        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "PERSONA_NOT_AVAILABLE"
        assert store.get_metadata("persona-session") == {}
    finally:
        record["availability"] = original_status
        record["availabilityReason"] = original_reason
        app.dependency_overrides.clear()


def test_scope_is_dispatched_only_by_server_session_kind() -> None:
    allowed, _ = is_message_in_scope_for_session("请和我谈谈知行合一", "persona")
    assert allowed is True
    allowed, refusal = is_message_in_scope_for_session("请陪我角色扮演王阳明", None)
    assert allowed is False
    assert refusal


def test_builtin_prompt_preserves_disclosure_and_source_boundaries() -> None:
    pack = get_persona_registry().require("wang-yangming")
    prompt = build_persona_chat_bootstrap(pack, initial_prompt="如何面对拖延？")
    assert "并非王阳明本人" in prompt
    assert "不得捏造" in prompt
    assert "如何面对拖延" in prompt
