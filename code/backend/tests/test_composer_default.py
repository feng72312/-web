from __future__ import annotations

import asyncio
from types import SimpleNamespace

from app.core.agent.chat_orchestrator import ChatOrchestrator
from app.core.agent.models import default_model, list_models, tier_for_model
from app.core.agent.service import (
    CursorAgentService,
    assistant_text_chunks,
    assistant_text_from_event,
    leftover_assistant_text,
)
from app.core.agent.session_store import AgentSessionStore
from app.core.quota.service import QuotaService
from app.core.quota.store import QuotaStore
from tests.test_persona_orchestrator import FakeCursor, FakeDeepSeek


def test_default_model_prefers_composer() -> None:
    assert default_model(cursor_enabled=True, deepseek_enabled=True) == "composer-2.5"
    assert default_model(cursor_enabled=False, deepseek_enabled=True) == "deepseek-chat"


def test_list_models_includes_composer_only_when_enabled() -> None:
    both = list_models(cursor_enabled=True, deepseek_enabled=True)
    ids = [item["id"] for item in both]
    assert "composer-2.5" in ids
    composer = next(item for item in both if item["id"] == "composer-2.5")
    assert composer["tier"] == "大师B"
    assert {item["id"] for item in both} >= {
        "composer-2.5",
        "deepseek-chat",
        "deepseek-reasoner",
        "deepseek-v4-pro",
    }

    deepseek_only = list_models(cursor_enabled=False, deepseek_enabled=True)
    assert all(item["id"] != "composer-2.5" for item in deepseek_only)


def test_tier_for_composer_is_master_b() -> None:
    assert tier_for_model("composer-2.5") == "大师B"


def test_empty_key_does_not_enable_or_start_bridge() -> None:
    service = CursorAgentService(api_key="", model="composer-2.5", workspace="/tmp", runtime="local")
    assert service.enabled is False
    asyncio.run(service.startup())
    assert service._client is None


def test_quota_consumes_master_b(tmp_path) -> None:
    service = QuotaService(QuotaStore(tmp_path / "quota.db"))
    device = "composer-quota-device"
    before = service.get_status(device)
    remaining = next(item["remaining"] for item in before["tierQuotas"] if item["tier"] == "大师B")
    result = service.consume_one(device, tier_name=tier_for_model("composer-2.5"))
    assert result["tier"] == "大师B"
    after = service.get_status(device)
    after_remaining = next(item["remaining"] for item in after["tierQuotas"] if item["tier"] == "大师B")
    assert after_remaining == remaining - 1
    master = next(item["remaining"] for item in after["tierQuotas"] if item["tier"] == "大师")
    assert master == next(item["remaining"] for item in before["tierQuotas"] if item["tier"] == "大师")


def test_resolve_model_hits_composer_and_does_not_fallback() -> None:
    chat = ChatOrchestrator(cursor=FakeCursor(), deepseek=FakeDeepSeek(), sessions=AgentSessionStore())
    assert chat.resolve_model("composer-2.5").id == "composer-2.5"
    assert chat.resolve_model(None).id == "composer-2.5"

    deepseek_only = ChatOrchestrator(cursor=None, deepseek=FakeDeepSeek(), sessions=AgentSessionStore())
    try:
        deepseek_only.resolve_model("composer-2.5")
        raised = False
    except RuntimeError as err:
        raised = True
        assert "cursor" in str(err)
    assert raised


def test_assistant_text_from_event_reads_text_delta() -> None:
    delta = SimpleNamespace(
        sdk_message=None,
        interaction_update=SimpleNamespace(type="text-delta", text="庚金"),
    )
    thinking = SimpleNamespace(
        sdk_message=None,
        interaction_update=SimpleNamespace(type="thinking-delta", text="内部"),
    )
    wrapped = SimpleNamespace(
        sdk_message=SimpleNamespace(
            type="assistant",
            message=SimpleNamespace(content=[SimpleNamespace(text="日主")]),
        ),
        interaction_update=None,
    )
    assert assistant_text_from_event(delta) == ["庚金"]
    assert assistant_text_from_event(thinking) == []
    assert assistant_text_from_event(wrapped) == ["日主"]


def test_leftover_assistant_text_fills_empty_stream() -> None:
    assert leftover_assistant_text("", "判词全文") == "判词全文"
    assert leftover_assistant_text("判", "判词全文") == "词全文"
    assert leftover_assistant_text("判词全文", "判词全文") == ""


def test_assistant_text_chunks_drop_tool_events() -> None:
    tool = SimpleNamespace(type="tool", message=SimpleNamespace(content=[SimpleNamespace(text="ls")]))
    assistant = SimpleNamespace(
        type="assistant",
        message=SimpleNamespace(content=[SimpleNamespace(text="判词")]),
    )
    assert assistant_text_chunks(tool) == []
    assert assistant_text_chunks(assistant) == ["判词"]


def test_fake_cursor_stream_filters_tool_events() -> None:
    cursor = FakeCursor()

    async def collect() -> list[tuple[str, str | None]]:
        rows: list[tuple[str, str | None]] = []
        async for item in cursor.send_stream("agent", "问", bootstrap=None):
            rows.append(item)
        return rows

    rows = asyncio.run(collect())
    texts = [chunk for chunk, run_id in rows if run_id is None]
    assert texts == ["知若真切", "，便会见诸行动。"]
    assert rows[-1] == ("", "cursor-run")
    assert "ls" not in "".join(texts)
