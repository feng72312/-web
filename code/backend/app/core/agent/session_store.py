from __future__ import annotations

from threading import Lock


class AgentSessionStore:
    """In-memory chart_key -> agent_id mapping for MVP sessions."""

    def __init__(self) -> None:
        self._agents: dict[str, str] = {}
        self._bootstrap: dict[str, str] = {}
        self._lock = Lock()

    def bind(self, chart_key: str, agent_id: str) -> None:
        with self._lock:
            self._agents[chart_key] = agent_id

    def get(self, chart_key: str) -> str | None:
        with self._lock:
            return self._agents.get(chart_key)

    def unbind(self, chart_key: str) -> None:
        with self._lock:
            self._agents.pop(chart_key, None)

    def set_bootstrap(self, agent_id: str, context: str) -> None:
        with self._lock:
            self._bootstrap[agent_id] = context

    def pop_bootstrap(self, agent_id: str) -> str | None:
        with self._lock:
            return self._bootstrap.pop(agent_id, None)
