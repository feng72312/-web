from __future__ import annotations

import logging
import sqlite3
import threading
import time
from pathlib import Path

logger = logging.getLogger(__name__)

HEARTBEAT_TTL_SEC = 90
SQLITE_BUSY_TIMEOUT_MS = 30_000


class UsageStatsStore:
    """SQLite cumulative visitors and online count from recent heartbeats."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            self._db_path,
            check_same_thread=False,
            timeout=SQLITE_BUSY_TIMEOUT_MS / 1000.0,
        )
        conn.row_factory = sqlite3.Row
        conn.execute(f"PRAGMA busy_timeout={SQLITE_BUSY_TIMEOUT_MS}")
        # DELETE journal is safer than WAL on COS/NFS mounts.
        conn.execute("PRAGMA journal_mode=DELETE")
        conn.execute("PRAGMA synchronous=FULL")
        return conn

    def _init_db(self) -> None:
        from app.core.quota.persistence import ensure_persist_marker

        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        ensure_persist_marker(self._db_path)
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS visitors (
                    visitor_id TEXT PRIMARY KEY,
                    first_seen REAL NOT NULL,
                    last_seen REAL NOT NULL,
                    ip TEXT,
                    user_agent TEXT
                );
                CREATE TABLE IF NOT EXISTS stats_counters (
                    key TEXT PRIMARY KEY,
                    value INTEGER NOT NULL DEFAULT 0
                );
                """
            )
            conn.commit()

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
        *,
        count_visit: bool = False,
    ) -> dict[str, int]:
        now = time.time()
        with self._lock:
            self._register_visitor(visitor_id, now, ip, user_agent)
            if count_visit:
                self._increment_visits()
            return self._overview_locked(now)

    def overview(self) -> dict[str, int]:
        now = time.time()
        with self._lock:
            return self._overview_locked(now)

    def _overview_locked(self, now: float) -> dict[str, int]:
        return {
            "online": self._count_online(now),
            "total": self._count_visitors(),
            "visits": self._count_visits(),
        }

    def _increment_visits(self) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO stats_counters (key, value) VALUES ('visits', 1) "
                "ON CONFLICT(key) DO UPDATE SET value = value + 1"
            )
            conn.commit()

    def _count_visits(self) -> int:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value FROM stats_counters WHERE key = 'visits'"
            ).fetchone()
            return int(row["value"]) if row else 0

    def _count_online(self, now: float) -> int:
        cutoff = now - HEARTBEAT_TTL_SEC
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS c FROM visitors WHERE last_seen >= ?",
                (cutoff,),
            ).fetchone()
            return int(row["c"]) if row else 0

    def _count_visitors(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS c FROM visitors").fetchone()
            return int(row["c"]) if row else 0


def default_stats_db_path() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "usage_stats.db"


def resolve_stats_db_path() -> Path:
    from app.config import settings

    raw = (settings.stats_db_path or "").strip()
    if raw:
        path = Path(raw).expanduser()
        logger.info("usage stats db path=%s", path)
        return path
    path = default_stats_db_path()
    logger.info("usage stats db path=%s (default)", path)
    return path
