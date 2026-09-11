from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

from cursor_sdk import (
    AsyncAgent,
    AsyncClient,
    CursorAgentError,
    CursorSDKError,
    LocalAgentOptions,
    ModelSelection,
    SendOptions,
)

logger = logging.getLogger(__name__)


class AgentRunError(Exception):
    def __init__(self, run_id: str, message: str = "agent run failed") -> None:
        super().__init__(message)
        self.run_id = run_id


def assistant_text_chunks(message: Any) -> list[str]:
    """Keep assistant text only; drop tool / system events."""
    if getattr(message, "type", "") != "assistant":
        return []
    content = getattr(getattr(message, "message", None), "content", ())
    chunks: list[str] = []
    for block in content:
        text = getattr(block, "text", "")
        if text:
            chunks.append(text)
    return chunks


def assistant_text_from_event(event: Any) -> list[str]:
    """Pull assistant text from SDK messages or text-delta updates."""
    sdk = getattr(event, "sdk_message", None)
    if sdk is not None:
        return assistant_text_chunks(sdk)
    chunks = assistant_text_chunks(event)
    if chunks:
        return chunks
    update = getattr(event, "interaction_update", None)
    if getattr(update, "type", "") == "text-delta":
        text = getattr(update, "text", "") or ""
        return [text] if text else []
    return []


def leftover_assistant_text(already: str, final: str) -> str:
    already = (already or "").strip()
    final = (final or "").strip()
    if not final or final == already:
        return ""
    if already and final.startswith(already):
        return final[len(already) :]
    if not already:
        return final
    return ""


class CursorAgentService:
    def __init__(self, api_key: str, model: str, workspace: str, runtime: str) -> None:
        self._api_key = api_key.strip()
        self._model = (model or "composer-2.5").strip() or "composer-2.5"
        self._workspace = Path(workspace)
        self._runtime = "local"
        self._client: AsyncClient | None = None
        self._agents: dict[str, AsyncAgent] = {}

    @property
    def enabled(self) -> bool:
        return bool(self._api_key)

    @property
    def model(self) -> str:
        return self._model

    @property
    def runtime(self) -> str:
        return self._runtime

    def _require_client(self) -> AsyncClient:
        if self._client is None:
            raise RuntimeError("cursor bridge is not running")
        return self._client

    def _local_options(self) -> LocalAgentOptions:
        return LocalAgentOptions(cwd=str(self._workspace), setting_sources=())

    def _model_selection(self) -> ModelSelection:
        return ModelSelection(id=self._model)

    async def startup(self) -> None:
        if not self.enabled:
            logger.info("cursor agent service disabled: empty api key")
            return
        self._workspace.mkdir(parents=True, exist_ok=True)
        self._client = await AsyncClient.launch_bridge(workspace=str(self._workspace))
        logger.info(
            "cursor agent bridge ready workspace=%s model=%s",
            self._workspace,
            self._model,
        )

    async def shutdown(self) -> None:
        self._agents.clear()
        client = self._client
        self._client = None
        if client is not None:
            await client.aclose()
            logger.info("cursor agent bridge closed")

    async def create_session(self) -> str:
        if not self.enabled:
            raise RuntimeError("cursor not configured")
        try:
            agent = await AsyncAgent.create(
                client=self._require_client(),
                model=self._model,
                api_key=self._api_key,
                local=self._local_options(),
            )
        except CursorAgentError as err:
            raise AgentRunError("", str(err)) from err
        self._agents[agent.agent_id] = agent
        return agent.agent_id

    async def _agent(self, agent_id: str) -> AsyncAgent:
        cached = self._agents.get(agent_id)
        if cached is not None:
            return cached
        agent = await AsyncAgent.resume(agent_id, client=self._require_client())
        self._agents[agent_id] = agent
        return agent

    def wrap_message(self, message: str, bootstrap: str | None) -> str:
        if not bootstrap:
            return message
        return (
            f"{bootstrap}\n\n"
            f"用户追问: {message}\n"
            f"直接回答用户。禁止输出模式标记、研究过程或系统说明。"
            f"如有上文资料则结合，否则按当前设定回答。不要重复已就绪类开场白。"
        )

    async def interpret(self, prompt: str) -> tuple[str, str]:
        agent_id = await self.create_session()
        text, _run_id = await self.send_once(agent_id, prompt, bootstrap=None)
        return text, agent_id

    async def send_once(
        self, agent_id: str, message: str, bootstrap: str | None = None
    ) -> tuple[str, str]:
        try:
            agent = await self._agent(agent_id)
            run = await agent.send(message, SendOptions(model=self._model))
            result = await run.wait()
        except CursorAgentError as err:
            raise AgentRunError("", str(err)) from err
        status = getattr(result.status, "value", result.status)
        if str(status) == "error":
            raise AgentRunError(result.id, "agent run failed")
        text = (result.result or "").strip()
        if not text:
            text = (await run.text()).strip()
        return text, result.id

    async def send_stream(
        self, agent_id: str, message: str, bootstrap: str | None = None
    ) -> AsyncIterator[tuple[str, str | None]]:
        try:
            agent = await self._agent(agent_id)
            run = await agent.send(message, SendOptions(model=self._model))
            collected: list[str] = []
            async for event in run.events():
                for chunk in assistant_text_from_event(event):
                    collected.append(chunk)
                    yield chunk, None
            result = await run.wait()
        except CursorAgentError as err:
            raise AgentRunError("", str(err)) from err
        status = getattr(result.status, "value", result.status)
        if str(status) == "error":
            raise AgentRunError(result.id, "agent run failed")
        extra = leftover_assistant_text("".join(collected), result.result or "")
        if not extra and not "".join(collected).strip():
            extra = leftover_assistant_text("", (await run.text()).strip())
        if extra:
            yield extra, None
        yield "", result.id


def resolve_runtime(configured: str) -> str:
    return "local" if (configured or "").strip() else "local"


def default_workspace(configured: str) -> str:
    return str(resolve_composer_workspace(configured))


def resolve_composer_workspace(configured: str | None = None) -> Path:
    from app.config import settings

    raw = (configured if configured is not None else settings.cursor_workspace) or ""
    raw = raw.strip() or "data/composer-workspace"
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[3] / path
    return path


_service: CursorAgentService | None = None


def init_agent_service(
    api_key: str, model: str, workspace: str, runtime: str = "auto"
) -> CursorAgentService:
    global _service
    _service = CursorAgentService(
        api_key=api_key,
        model=model,
        workspace=str(resolve_composer_workspace(workspace)),
        runtime=runtime,
    )
    return _service


def get_agent_service() -> CursorAgentService | None:
    return _service
