from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import AsyncIterator
from contextlib import AbstractAsyncContextManager
from pathlib import Path
from typing import Any

from cursor_sdk import AgentOptions, AsyncClient, CloudAgentOptions, CloudEnvironment, LocalAgentOptions

logger = logging.getLogger(__name__)


class AgentRunError(Exception):
    def __init__(self, run_id: str, message: str = "agent run failed") -> None:
        super().__init__(message)
        self.run_id = run_id


class CursorAgentService:
    def __init__(self, api_key: str, model: str, workspace: str, runtime: str) -> None:
        self._api_key = api_key.strip()
        self._model = model
        self._workspace = workspace
        self._runtime = resolve_runtime(runtime)
        self._bridge_cm: AbstractAsyncContextManager[AsyncClient] | None = None
        self._client: AsyncClient | None = None
        self._agents: dict[str, Any] = {}
        self._bridge_lock: asyncio.Lock | None = None

    @property
    def enabled(self) -> bool:
        return bool(self._api_key)

    @property
    def model(self) -> str:
        return self._model

    @property
    def runtime(self) -> str:
        return self._runtime

    async def startup(self) -> None:
        if not self.enabled:
            logger.info("cursor agent service disabled (no api key)")
            return
        logger.info(
            "cursor agent service ready runtime=%s (bridge starts on first use)",
            self._runtime,
        )

    async def _ensure_bridge(self) -> None:
        if self._client is not None:
            return
        if self._bridge_lock is None:
            self._bridge_lock = asyncio.Lock()
        async with self._bridge_lock:
            if self._client is not None:
                return
            bridge = await AsyncClient.launch_bridge(workspace=self._workspace)
            self._bridge_cm = bridge
            self._client = await bridge.__aenter__()
            logger.info(
                "cursor agent bridge started runtime=%s workspace=%s",
                self._runtime,
                self._workspace,
            )

    async def shutdown(self) -> None:
        if self._bridge_cm is not None:
            await self._bridge_cm.__aexit__(None, None, None)
            self._bridge_cm = None
            self._client = None
            logger.info("cursor agent bridge stopped")

    def _agent_options(self) -> AgentOptions:
        if self._runtime == "cloud":
            return AgentOptions(
                api_key=self._api_key,
                model=self._model,
                cloud=CloudAgentOptions(env=CloudEnvironment()),
            )
        return AgentOptions(
            api_key=self._api_key,
            model=self._model,
            local=LocalAgentOptions(cwd=self._workspace),
        )

    async def _require_client(self) -> AsyncClient:
        await self._ensure_bridge()
        if self._client is None:
            raise RuntimeError("cursor bridge not started")
        return self._client

    def _remember_agent(self, agent: Any) -> str:
        agent_id = agent.agent_id
        self._agents[agent_id] = agent
        return agent_id

    async def _resolve_agent(self, agent_id: str) -> Any:
        cached = self._agents.get(agent_id)
        if cached is not None:
            return cached
        if self._runtime == "cloud":
            raise RuntimeError(
                f"cloud agent session expired or lost after restart: {agent_id}"
            )
        client = await self._require_client()
        agent = await client.agents.resume(agent_id, self._agent_options())
        self._agents[agent_id] = agent
        return agent

    async def create_session(self) -> str:
        """Create agent only; chart context is sent on the first user message."""
        client = await self._require_client()
        opts = self._agent_options()
        agent = await client.agents.create(
            model=opts.model or self._model,
            api_key=opts.api_key or self._api_key,
            local=opts.local,
            cloud=opts.cloud,
        )
        agent_id = self._remember_agent(agent)
        logger.info("chat session created agent_id=%s runtime=%s", agent_id, self._runtime)
        return agent_id

    def wrap_message(self, message: str, bootstrap: str | None) -> str:
        if not bootstrap:
            return message
        return (
            f"{bootstrap}\n\n"
            f"用户追问: {message}\n"
            f"请结合上文命盘资料回答, 不要重复已就绪类开场白."
        )

    async def interpret(self, prompt: str) -> tuple[str, str]:
        client = await self._require_client()
        opts = self._agent_options()
        agent = await client.agents.create(
            model=opts.model or self._model,
            api_key=opts.api_key or self._api_key,
            local=opts.local,
            cloud=opts.cloud,
        )
        run = await agent.send(prompt)
        text = (await run.text()).strip()
        result = await run.wait()
        logger.info(
            "interpret run finished agent_id=%s run_id=%s status=%s",
            agent.agent_id,
            result.id,
            result.status,
        )
        if result.status == "error" and not text:
            raise AgentRunError(result.id)
        if not text:
            raise AgentRunError(result.id, "empty interpret response")
        self._remember_agent(agent)
        return text, agent.agent_id

    async def send_once(
        self, agent_id: str, message: str, bootstrap: str | None = None
    ) -> tuple[str, str]:
        agent = await self._resolve_agent(agent_id)
        run = await agent.send(self.wrap_message(message, bootstrap))
        text = await run.text()
        result = await run.wait()
        logger.info("chat run finished agent_id=%s run_id=%s", agent_id, result.id)
        if result.status == "error":
            raise AgentRunError(result.id)
        return text, result.id

    async def send_stream(
        self, agent_id: str, message: str, bootstrap: str | None = None
    ) -> AsyncIterator[tuple[str, str | None]]:
        agent = await self._resolve_agent(agent_id)
        run = await agent.send(self.wrap_message(message, bootstrap))
        run_id = run.id
        logger.info("chat stream started agent_id=%s run_id=%s", agent_id, run_id)
        async for chunk in run.iter_text():
            yield chunk, None
        result = await run.wait()
        if result.status == "error":
            raise AgentRunError(result.id)
        yield "", run_id


def resolve_runtime(configured: str) -> str:
    normalized = configured.strip().lower()
    if normalized in ("local", "cloud"):
        return normalized
    if os.environ.get("BAZI_CURSOR_RUNTIME", "").strip().lower() == "cloud":
        return "cloud"
    if os.environ.get("PORT"):
        return "cloud"
    return "local"


def default_workspace(configured: str) -> str:
    if configured.strip():
        return configured.strip()
    app_root = Path(__file__).resolve().parents[3]
    if app_root.is_dir():
        return str(app_root)
    return str(Path.cwd())


_service: CursorAgentService | None = None


def init_agent_service(
    api_key: str, model: str, workspace: str, runtime: str = "auto"
) -> CursorAgentService:
    global _service
    _service = CursorAgentService(
        api_key=api_key,
        model=model,
        workspace=default_workspace(workspace),
        runtime=runtime,
    )
    return _service


def get_agent_service() -> CursorAgentService | None:
    return _service
