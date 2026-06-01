from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.agent.service import CursorAgentService
    from app.core.agent.session_store import AgentSessionStore

__all__ = [
    "AgentSessionStore",
    "CursorAgentService",
    "get_agent_service",
    "init_agent_service",
]


def __getattr__(name: str):
    if name == "AgentSessionStore":
        from app.core.agent.session_store import AgentSessionStore

        return AgentSessionStore
    if name in ("CursorAgentService", "get_agent_service", "init_agent_service"):
        from app.core.agent.service import (
            CursorAgentService,
            get_agent_service,
            init_agent_service,
        )

        return {
            "CursorAgentService": CursorAgentService,
            "get_agent_service": get_agent_service,
            "init_agent_service": init_agent_service,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
