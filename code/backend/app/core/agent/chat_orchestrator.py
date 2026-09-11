from __future__ import annotations

import logging
import uuid
from collections.abc import AsyncIterator
from typing import Any


from app.core.agent.ai_text import sanitize_ai_text, visible_stream_text
from app.core.agent.deepseek import DeepSeekClient, DeepSeekError
from app.core.agent.models import ChatModel, model_by_id
from app.core.agent.service import AgentRunError, CursorAgentService
from app.core.agent.session_store import AgentSessionStore

logger = logging.getLogger(__name__)


class ChatOrchestrator:
    def __init__(
        self,
        cursor: CursorAgentService | None,
        deepseek: DeepSeekClient | None,
        sessions: AgentSessionStore,
    ) -> None:
        self._cursor = cursor
        self._deepseek = deepseek
        self._sessions = sessions

    @property
    def cursor_enabled(self) -> bool:
        return self._cursor is not None and self._cursor.enabled

    @property
    def deepseek_enabled(self) -> bool:
        return self._deepseek is not None and self._deepseek.enabled

    @property
    def enabled(self) -> bool:
        return self.cursor_enabled or self.deepseek_enabled

    def resolve_model(self, model_id: str | None) -> ChatModel:
        if model_id:
            found = model_by_id(model_id)
            if found is not None:
                if found.provider == "cursor":
                    if not self.cursor_enabled:
                        raise RuntimeError("cursor not configured")
                    return found
                if found.provider == "deepseek":
                    if not self.deepseek_enabled:
                        raise RuntimeError("deepseek not configured")
                    return found
        if self.cursor_enabled:
            found = model_by_id("composer-2.5")
            if found is not None:
                return found
        if self.deepseek_enabled:
            found = model_by_id("deepseek-chat")
            if found is not None:
                return found
        raise RuntimeError("no chat provider configured")

    async def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self._sessions.create(session_id)
        logger.info("chat session created session_id=%s", session_id)
        return session_id

    def set_bootstrap(self, session_id: str, bootstrap: str) -> None:
        self._sessions.set_bootstrap(session_id, bootstrap)

    def bind_chart(self, chart_key: str, session_id: str) -> None:
        self._sessions.bind(chart_key, session_id)

    async def send_once(
        self,
        session_id: str,
        message: str,
        model_id: str | None = None,
    ) -> tuple[str, str]:
        model = self.resolve_model(model_id)
        bootstrap = self._sessions.peek_bootstrap(session_id)
        if model.provider == "deepseek":
            text = await self._send_deepseek_once(session_id, message, model, bootstrap)
            run_id = f"deepseek-{session_id[:8]}"
            return text, run_id
        text, run_id = await self._send_cursor_once(session_id, message, bootstrap)
        return text, run_id

    async def send_stream(
        self,
        session_id: str,
        message: str,
        model_id: str | None = None,
    ) -> AsyncIterator[tuple[str, str | None]]:
        model = self.resolve_model(model_id)
        bootstrap = self._sessions.peek_bootstrap(session_id)
        if model.provider == "deepseek":
            full = ""
            async for chunk in self._stream_deepseek(session_id, message, model, bootstrap):
                full += chunk
                yield chunk, None
            full = sanitize_ai_text(full)
            self._sessions.append_message(session_id, "user", message, model.id)
            self._sessions.append_message(session_id, "assistant", full, model.id)
            yield "", f"deepseek-{session_id[:8]}"
            return

        async for chunk, run_id in self._stream_cursor(session_id, message, bootstrap):
            yield chunk, run_id

    async def _send_deepseek_once(
        self,
        session_id: str,
        message: str,
        model: ChatModel,
        bootstrap: str | None,
    ) -> str:
        if self._deepseek is None:
            raise RuntimeError("deepseek not configured")
        history = self._sessions.get_messages(session_id)
        try:
            text = await self._deepseek.chat_once(
                model.id,
                message,
                system=bootstrap,
                history=history,
            )
        except DeepSeekError as err:
            raise RuntimeError(str(err)) from err
        text = sanitize_ai_text(text)
        self._sessions.append_message(session_id, "user", message, model.id)
        self._sessions.append_message(session_id, "assistant", text, model.id)
        return text

    async def _stream_deepseek(
        self,
        session_id: str,
        message: str,
        model: ChatModel,
        bootstrap: str | None,
    ) -> AsyncIterator[str]:
        if self._deepseek is None:
            raise RuntimeError("deepseek not configured")
        history = self._sessions.get_messages(session_id)
        try:
            async for chunk in self._deepseek.chat_stream(
                model.id,
                message,
                system=bootstrap,
                history=history,
            ):
                yield chunk
        except DeepSeekError as err:
            raise RuntimeError(str(err)) from err

    async def _send_cursor_once(
        self,
        session_id: str,
        message: str,
        bootstrap: str | None,
    ) -> tuple[str, str]:
        if self._cursor is None:
            raise RuntimeError("cursor not configured")
        agent_id = await self._ensure_cursor_agent(session_id)
        wrapped = self._wrap_cursor_message(session_id, message, bootstrap)
        use_bootstrap = bootstrap if not self._sessions.cursor_bootstrapped(session_id) else None
        if use_bootstrap:
            self._sessions.mark_cursor_bootstrapped(session_id)
        try:
            text, run_id = await self._cursor.send_once(
                agent_id,
                wrapped,
                bootstrap=use_bootstrap,
            )
        except AgentRunError as err:
            raise RuntimeError(str(err)) from err
        text = sanitize_ai_text(text)
        self._sessions.append_message(session_id, "user", message, "composer-2.5")
        self._sessions.append_message(session_id, "assistant", text, "composer-2.5")
        return text, run_id

    async def _stream_cursor(
        self,
        session_id: str,
        message: str,
        bootstrap: str | None,
    ) -> AsyncIterator[tuple[str, str | None]]:
        if self._cursor is None:
            raise RuntimeError("cursor not configured")
        agent_id = await self._ensure_cursor_agent(session_id)
        wrapped = self._wrap_cursor_message(session_id, message, bootstrap)
        use_bootstrap = bootstrap if not self._sessions.cursor_bootstrapped(session_id) else None
        if use_bootstrap:
            self._sessions.mark_cursor_bootstrapped(session_id)
        raw = ""
        emitted = ""
        try:
            async for chunk, run_id in self._cursor.send_stream(
                agent_id,
                wrapped,
                bootstrap=use_bootstrap,
            ):
                if run_id is not None:
                    stored = sanitize_ai_text(raw)
                    self._sessions.append_message(session_id, "user", message, "composer-2.5")
                    self._sessions.append_message(session_id, "assistant", stored, "composer-2.5")
                    yield "", run_id
                    return
                if chunk:
                    raw += chunk
                    cleaned = visible_stream_text(raw)
                    if cleaned.startswith(emitted):
                        delta = cleaned[len(emitted) :]
                        if delta:
                            emitted = cleaned
                            yield delta, None
        except AgentRunError as err:
            raise RuntimeError(str(err)) from err

    async def _ensure_cursor_agent(self, session_id: str) -> str:
        existing = self._sessions.get_cursor_agent(session_id)
        if existing:
            return existing
        if self._cursor is None:
            raise RuntimeError("cursor not configured")
        agent_id = await self._cursor.create_session()
        self._sessions.set_cursor_agent(session_id, agent_id)
        return agent_id

    def _wrap_cursor_message(
        self,
        session_id: str,
        message: str,
        bootstrap: str | None,
    ) -> str:
        if self._cursor is None:
            return message
        prefix = self._sessions.foreign_history_prefix(session_id, "composer-2.5")
        if prefix:
            return (
                f"{prefix}\n\n"
                f"用户追问: {message}\n"
                f"直接回答用户。禁止输出模式标记、研究过程或系统说明。"
                f"如有上文资料则结合，否则按当前设定回答。不要重复已就绪类开场白。"
            )
        return self._cursor.wrap_message(message, bootstrap)

    def seed_interpret_summaries(
        self,
        session_id: str,
        *,
        summary_plain: str | None = None,
        summary_professional: str | None = None,
        model_id: str = "deepseek-chat",
    ) -> int:
        model = self.resolve_model(model_id)
        existing = self._sessions.get_messages(session_id)
        existing_bodies = {
            item.get("content", "").strip()
            for item in existing
            if item.get("role") == "assistant"
        }
        added = 0
        seeds: list[tuple[str, str | None]] = [
            ("AI深度解读", summary_plain),
            ("命理师专用解读", summary_professional),
        ]
        for label, raw in seeds:
            text = sanitize_ai_text((raw or "").strip())
            if not text:
                continue
            if text in existing_bodies:
                continue
            prefixed = any(
                text in body or body.endswith(text)
                for body in existing_bodies
            )
            if prefixed:
                continue
            content = f"【{label}】\n\n{text}"
            self._sessions.append_message(session_id, "assistant", content, model.id)
            existing_bodies.add(content)
            added += 1
        return added

    async def interpret(self, prompt: str, model_id: str | None = None) -> tuple[str, str | None]:
        model = self.resolve_model(model_id)
        if model.provider == "deepseek":
            if self._deepseek is None:
                raise RuntimeError("deepseek not configured")
            text = sanitize_ai_text(await self._deepseek.chat_once(model.id, prompt))
            session_id = await self.create_session()
            self._sessions.set_bootstrap(session_id, prompt)
            self._sessions.append_message(session_id, "assistant", text, model.id)
            return text, session_id
        if self._cursor is None:
            raise RuntimeError("cursor not configured")
        text, cursor_agent_id = await self._cursor.interpret(prompt)
        text = sanitize_ai_text(text)
        session_id = await self.create_session()
        self._sessions.set_cursor_agent(session_id, cursor_agent_id)
        self._sessions.mark_cursor_bootstrapped(session_id)
        self._sessions.append_message(session_id, "assistant", text, "composer-2.5")
        return text, session_id


_orchestrator: ChatOrchestrator | None = None


def init_chat_orchestrator(
    cursor: CursorAgentService | None,
    deepseek: DeepSeekClient | None,
    sessions: AgentSessionStore,
) -> ChatOrchestrator:
    global _orchestrator
    _orchestrator = ChatOrchestrator(cursor=cursor, deepseek=deepseek, sessions=sessions)
    return _orchestrator


def get_chat_orchestrator() -> ChatOrchestrator | None:
    return _orchestrator
