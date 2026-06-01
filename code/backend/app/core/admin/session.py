from __future__ import annotations

import secrets
import threading
import time


class AdminSessionStore:
    def __init__(self, ttl_seconds: int = 86_400) -> None:
        self._ttl_seconds = ttl_seconds
        self._lock = threading.Lock()
        self._sessions: dict[str, float] = {}

    def create(self) -> str:
        token = secrets.token_urlsafe(32)
        expires_at = time.time() + self._ttl_seconds
        with self._lock:
            self._purge_expired_locked(time.time())
            self._sessions[token] = expires_at
        return token

    def validate(self, token: str) -> bool:
        if not token:
            return False
        now = time.time()
        with self._lock:
            self._purge_expired_locked(now)
            expires_at = self._sessions.get(token)
            if expires_at is None:
                return False
            if expires_at <= now:
                self._sessions.pop(token, None)
                return False
            return True

    def revoke(self, token: str) -> None:
        with self._lock:
            self._sessions.pop(token, None)

    def _purge_expired_locked(self, now: float) -> None:
        expired = [token for token, expires_at in self._sessions.items() if expires_at <= now]
        for token in expired:
            self._sessions.pop(token, None)
