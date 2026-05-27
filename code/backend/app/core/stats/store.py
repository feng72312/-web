from __future__ import annotations

import sqlite3
import threading
import time
from pathlib import Path

HEARTBEAT_TTL_SEC = 90


class UsageStatsStore:
    """SQLite cumulative visitors + in-memory online heartbeats."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._lock = threading.Lock()
        self._online: dict[str, float] = {}
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS visitors (
                    visitor_id TEXT PRIMARY KEY,
                    first_seen REAL NOT NULL,
                    last_seen REAL NOT NULL,
                    ip TEXT,
                    user_agent TEXT
                )
                """
            )
            conn.commit()

    def _purge_stale_online(self, now: float) -> None:
        cutoff = now - HEARTBEAT_TTL_SEC
        stale = [vid for vid, ts in self._online.items() if ts < cutoff]
        for vid in stale:
            self._online.pop(vid, None)

    def _register_visitor(
        self,
        visitor_id: str,
        now: float,
        ip: str | None,
        user_agent: str | None,
    ) -> bool:
        """Return True if this is a new unique visitor."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT visitor_id FROM visitors WHERE visitor_id = ?",
                (visitor_id,),
            ).fetchone()
            if row:
                conn.execute(
                    "UPDATE visitors SET last_seen = ?, ip = COALESCE(?, ip), "
                    "user_agent = COALESCE(?, user_agent) WHERE visitor_id = ?",
                    (now, ip, user_agent, visitor_id),
                )
                conn.commit()
                return False
            conn.execute(
                "INSERT INTO visitors (visitor_id, first_seen, last_seen, ip, user_agent) "
                "VALUES (?, ?, ?, ?, ?)",
                (visitor_id, now, now, ip, user_agent),
            )
            conn.commit()
            return True

    def heartbeat(
        self,
        visitor_id: str,
        ip: str | None = None,
        user_agent: str | None = None,
    ) -> dict[str, int]:
        now = time.time()
        with self._lock:
            self._purge_stale_online(now)
            self._online[visitor_id] = now
            self._register_visitor(visitor_id, now, ip, user_agent)
            online = len(self._online)
            total = self._count_visitors()
        return {"online": online, "total": total}

    def overview(self) -> dict[str, int]:
        now = time.time()
        with self._lock:
            self._purge_stale_online(now)
            return {"online": len(self._online), "total": self._count_visitors()}

    def _count_visitors(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS c FROM visitors").fetchone()
            return int(row["c"]) if row else 0


def default_stats_db_path() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "usage_stats.db"
