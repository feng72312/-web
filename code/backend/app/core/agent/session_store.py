from __future__ import annotations

from threading import Lock


class AgentSessionStore:
    """In-memory session store for chart context, history, and cursor agents."""

    def __init__(self) -> None:
        self._agents: dict[str, str] = {}
        self._bootstrap: dict[str, str] = {}
        self._messages: dict[str, list[dict[str, str]]] = {}
        self._metadata: dict[str, dict[str, str]] = {}
        self._cursor_agents: dict[str, str] = {}
        self._cursor_bootstrapped: set[str] = set()
        self._lock = Lock()

    def create(self, session_id: str) -> None:
        with self._lock:
            self._messages.setdefault(session_id, [])

    def set_metadata(
        self,
        session_id: str,
        *,
        session_kind: str,
        persona_id: str | None = None,
        interaction_mode: str | None = None,
    ) -> None:
        metadata = {"session_kind": session_kind}
        if persona_id:
            metadata["persona_id"] = persona_id
        if interaction_mode:
            metadata["interaction_mode"] = interaction_mode
        with self._lock:
            self._metadata[session_id] = metadata

    def get_metadata(self, session_id: str) -> dict[str, str]:
        with self._lock:
            return dict(self._metadata.get(session_id, {}))

    def bind(self, chart_key: str, session_id: str) -> None:
        with self._lock:
            self._agents[chart_key] = session_id

    def get(self, chart_key: str) -> str | None:
        with self._lock:
            return self._agents.get(chart_key)

    def unbind(self, chart_key: str) -> None:
        with self._lock:
            self._agents.pop(chart_key, None)

    def set_bootstrap(self, session_id: str, context: str) -> None:
        with self._lock:
            self._bootstrap[session_id] = context

    def peek_bootstrap(self, session_id: str) -> str | None:
        with self._lock:
            return self._bootstrap.get(session_id)

    def pop_bootstrap(self, session_id: str) -> str | None:
        with self._lock:
            return self._bootstrap.pop(session_id, None)

    def get_messages(self, session_id: str) -> list[dict[str, str]]:
        with self._lock:
            rows = self._messages.get(session_id, [])
            return [{"role": item["role"], "content": item["content"]} for item in rows]

    def append_message(
        self,
        session_id: str,
        role: str,
        content: str,
        model: str,
    ) -> None:
        with self._lock:
            self._messages.setdefault(session_id, []).append(
                {"role": role, "content": content, "model": model}
            )

    def foreign_history_prefix(self, session_id: str, current_model: str) -> str:
        with self._lock:
            rows = self._messages.get(session_id, [])
        foreign: list[str] = []
        for item in rows:
            if item.get("model") == current_model:
                continue
            role_label = "用户" if item.get("role") == "user" else "助手"
            foreign.append(f"{role_label}: {item.get('content', '')}")
        if not foreign:
            return ""
        return "以下是此前由其他模型参与的对话:\n" + "\n".join(foreign)

    def set_cursor_agent(self, session_id: str, agent_id: str) -> None:
        with self._lock:
            self._cursor_agents[session_id] = agent_id

    def get_cursor_agent(self, session_id: str) -> str | None:
        with self._lock:
            return self._cursor_agents.get(session_id)

    def cursor_bootstrapped(self, session_id: str) -> bool:
        with self._lock:
            return session_id in self._cursor_bootstrapped

    def mark_cursor_bootstrapped(self, session_id: str) -> None:
        with self._lock:
            self._cursor_bootstrapped.add(session_id)
