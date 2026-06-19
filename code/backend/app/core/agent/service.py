from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from pathlib import Path

logger = logging.getLogger(__name__)


class AgentRunError(Exception):
    def __init__(self, run_id: str, message: str = "agent run failed") -> None:
        super().__init__(message)
        self.run_id = run_id


class CursorAgentService:
    """Retained as a compatibility shim; Cursor SDK support has been removed."""

    def __init__(self, api_key: str, model: str, workspace: str, runtime: str) -> None:
        self._model = model
        self._workspace = workspace
        self._runtime = "disabled"

    @property
    def enabled(self) -> bool:
        return False

    @property
    def model(self) -> str:
        return self._model

    @property
    def runtime(self) -> str:
        return self._runtime

    async def startup(self) -> None:
        logger.info("cursor agent service removed; DeepSeek-only mode")

    async def shutdown(self) -> None:
        return None

    async def create_session(self) -> str:
        raise RuntimeError("cursor agent service has been removed")

    def wrap_message(self, message: str, bootstrap: str | None) -> str:
        if not bootstrap:
            return message
        return (
            f"{bootstrap}\n\n"
            f"用户追问: {message}\n"
            f"请结合上文命盘资料回答, 不要重复已就绪类开场白."
        )

    async def interpret(self, prompt: str) -> tuple[str, str]:
        raise RuntimeError("cursor agent service has been removed")

    async def send_once(
        self, agent_id: str, message: str, bootstrap: str | None = None
    ) -> tuple[str, str]:
        raise RuntimeError("cursor agent service has been removed")

    async def send_stream(
        self, agent_id: str, message: str, bootstrap: str | None = None
    ) -> AsyncIterator[tuple[str, str | None]]:
        raise RuntimeError("cursor agent service has been removed")


def resolve_runtime(configured: str) -> str:
    return "disabled"


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
