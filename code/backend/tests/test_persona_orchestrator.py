from __future__ import annotations

import asyncio

from app.core.agent.chat_orchestrator import ChatOrchestrator
from app.core.agent.session_store import AgentSessionStore


class FakeDeepSeek:
    enabled = True

    def __init__(self) -> None:
        self.system: str | None = None
        self.history: list[dict[str, str]] = []

    async def chat_once(self, model, message, *, system, history):
        self.system = system
        self.history = history
        return "先从今日可做的一件事开始。"


class FakeCursor:
    enabled = True

    def __init__(self) -> None:
        self.bootstrap: str | None = None
        self.streamed: list[str] = []

    async def create_session(self) -> str:
        return "cursor-agent"

    def wrap_message(self, message: str, bootstrap: str | None) -> str:
        return message

    async def send_once(self, agent_id, message, *, bootstrap):
        self.bootstrap = bootstrap
        return "知若真切，便会见诸行动。", "cursor-run"

    async def send_stream(self, agent_id, message, *, bootstrap):
        events = [
            _FakeEvent("tool", ""),
            _FakeEvent("assistant", "知若真切"),
            _FakeEvent("assistant", "，便会见诸行动。"),
        ]
        from app.core.agent.service import assistant_text_chunks

        for event in events:
            for chunk in assistant_text_chunks(event):
                self.streamed.append(chunk)
                yield chunk, None
        yield "", "cursor-run"


class _FakeEvent:
    def __init__(self, type_: str, text: str) -> None:
        self.type = type_
        self.message = type("Msg", (), {"content": [type("Block", (), {"text": text})()]})()


def test_deepseek_receives_bootstrap_and_writes_history() -> None:
    store = AgentSessionStore()
    deepseek = FakeDeepSeek()
    chat = ChatOrchestrator(cursor=None, deepseek=deepseek, sessions=store)
    session_id = asyncio.run(chat.create_session())
    chat.set_bootstrap(session_id, "人物安全合同与王阳明方法论")

    text, _ = asyncio.run(
        chat.send_once(session_id, "怎样理解知行合一？", "deepseek-chat")
    )

    assert text
    assert deepseek.system == "人物安全合同与王阳明方法论"
    assert [item["role"] for item in store.get_messages(session_id)] == [
        "user",
        "assistant",
    ]


def test_cursor_receives_bootstrap_and_writes_history() -> None:
    store = AgentSessionStore()
    cursor = FakeCursor()
    chat = ChatOrchestrator(cursor=cursor, deepseek=None, sessions=store)
    session_id = asyncio.run(chat.create_session())
    chat.set_bootstrap(session_id, "人物安全合同与王阳明方法论")
    text, run_id = asyncio.run(
        chat.send_once(session_id, "何谓致良知？", "composer-2.5")
    )

    assert text
    assert run_id == "cursor-run"
    assert cursor.bootstrap == "人物安全合同与王阳明方法论"
    assert [item["role"] for item in store.get_messages(session_id)] == [
        "user",
        "assistant",
    ]
