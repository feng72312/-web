from __future__ import annotations

import logging
import sqlite3
import threading
import time
from pathlib import Path

from app.core.quota.keys import (
    FREE_DAILY_LIMIT,
    TIER_FREE_DAILY_LIMITS,
    TIER_FREE_ORDER,
    hash_license_key,
    normalize_license_key,
    tier_free_daily_limit,
)

logger = logging.getLogger(__name__)

SQLITE_BUSY_TIMEOUT_MS = 30_000


class QuotaExceededError(Exception):
    def __init__(
        self,
        free_remaining: int,
        credit_balance: int,
        message: str = "quota exceeded",
    ) -> None:
        super().__init__(message)
        self.free_remaining = free_remaining
        self.credit_balance = credit_balance


class InvalidLicenseKeyError(Exception):
    pass


class PhoneAlreadyBoundError(Exception):
    pass


class QuotaStore:
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
                CREATE TABLE IF NOT EXISTS quota_accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL UNIQUE,
                    phone TEXT UNIQUE,
                    credit_balance INTEGER NOT NULL DEFAULT 0,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS quota_daily_usage (
                    device_id TEXT NOT NULL,
                    usage_date TEXT NOT NULL,
                    used_count INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (device_id, usage_date)
                );
                CREATE TABLE IF NOT EXISTS quota_tier_daily_usage (
                    device_id TEXT NOT NULL,
                    usage_date TEXT NOT NULL,
                    tier_name TEXT NOT NULL,
                    used_count INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (device_id, usage_date, tier_name)
                );
                CREATE TABLE IF NOT EXISTS quota_device_merges (
                    device_id TEXT NOT NULL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    merged_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS license_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key_hash TEXT NOT NULL UNIQUE,
                    credits INTEGER NOT NULL,
                    tier_label TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'unused',
                    redeemed_device_id TEXT,
                    redeemed_at REAL,
                    note TEXT,
                    created_at REAL NOT NULL
                );
                """
            )
            conn.commit()

    def _ensure_account(self, conn: sqlite3.Connection, device_id: str, now: float) -> None:
        row = conn.execute(
            "SELECT device_id FROM quota_accounts WHERE device_id = ?",
            (device_id,),
        ).fetchone()
        if row:
            return
        conn.execute(
            "INSERT INTO quota_accounts (device_id, credit_balance, created_at, updated_at) "
            "VALUES (?, 0, ?, ?)",
            (device_id, now, now),
        )

    def _tier_used(self, conn: sqlite3.Connection, device_id: str, usage_date: str, tier_name: str) -> int:
        row = conn.execute(
            "SELECT used_count FROM quota_tier_daily_usage "
            "WHERE device_id = ? AND usage_date = ? AND tier_name = ?",
            (device_id, usage_date, tier_name),
        ).fetchone()
        return int(row["used_count"]) if row else 0

    def _shared_used(self, conn: sqlite3.Connection, device_id: str, usage_date: str) -> int:
        row = conn.execute(
            "SELECT used_count FROM quota_daily_usage "
            "WHERE device_id = ? AND usage_date = ?",
            (device_id, usage_date),
        ).fetchone()
        return int(row["used_count"]) if row else 0

    def get_status(self, device_id: str, usage_date: str) -> dict[str, int | str | None | list[dict[str, int | str]]]:
        now = time.time()
        with self._lock:
            with self._connect() as conn:
                self._ensure_account(conn, device_id, now)
                conn.commit()
                account = conn.execute(
                    "SELECT phone, credit_balance FROM quota_accounts WHERE device_id = ?",
                    (device_id,),
                ).fetchone()
                shared_used = self._shared_used(conn, device_id, usage_date)
                tier_quotas: list[dict[str, int | str]] = []
                for tier_name in TIER_FREE_ORDER:
                    limit = TIER_FREE_DAILY_LIMITS[tier_name]
                    used = self._tier_used(conn, device_id, usage_date, tier_name)
                    tier_quotas.append(
                        {
                            "tier": tier_name,
                            "remaining": max(0, limit - used),
                            "limit": limit,
                        }
                    )
        free_remaining = max(0, FREE_DAILY_LIMIT - shared_used)
        return {
            "deviceId": device_id,
            "phone": account["phone"] if account else None,
            "freeRemaining": free_remaining,
            "freeDailyLimit": FREE_DAILY_LIMIT,
            "creditBalance": int(account["credit_balance"]) if account else 0,
            "tierQuotas": tier_quotas,
        }

    def consume_one(self, device_id: str, usage_date: str, tier_name: str = "大师") -> dict[str, int | str]:
        tier_name = tier_name if tier_name in TIER_FREE_DAILY_LIMITS else "大师"
        tier_limit = tier_free_daily_limit(tier_name)
        now = time.time()
        with self._lock:
            with self._connect() as conn:
                conn.execute("BEGIN IMMEDIATE")
                try:
                    self._ensure_account(conn, device_id, now)
                    tier_used = self._tier_used(conn, device_id, usage_date, tier_name)
                    shared_used = self._shared_used(conn, device_id, usage_date)
                    account = conn.execute(
                        "SELECT credit_balance FROM quota_accounts WHERE device_id = ?",
                        (device_id,),
                    ).fetchone()
                    credits = int(account["credit_balance"])

                    if tier_used < tier_limit:
                        if tier_used == 0:
                            conn.execute(
                                "INSERT INTO quota_tier_daily_usage "
                                "(device_id, usage_date, tier_name, used_count) VALUES (?, ?, ?, 1)",
                                (device_id, usage_date, tier_name),
                            )
                        else:
                            conn.execute(
                                "UPDATE quota_tier_daily_usage SET used_count = used_count + 1 "
                                "WHERE device_id = ? AND usage_date = ? AND tier_name = ?",
                                (device_id, usage_date, tier_name),
                            )
                        source = "tier_free"
                    elif shared_used < FREE_DAILY_LIMIT:
                        if shared_used == 0:
                            conn.execute(
                                "INSERT INTO quota_daily_usage "
                                "(device_id, usage_date, used_count) VALUES (?, ?, 1)",
                                (device_id, usage_date),
                            )
                        else:
                            conn.execute(
                                "UPDATE quota_daily_usage SET used_count = used_count + 1 "
                                "WHERE device_id = ? AND usage_date = ?",
                                (device_id, usage_date),
                            )
                        source = "shared_free"
                    elif credits > 0:
                        conn.execute(
                            "UPDATE quota_accounts SET credit_balance = credit_balance - 1, "
                            "updated_at = ? WHERE device_id = ?",
                            (now, device_id),
                        )
                        source = "paid"
                    else:
                        conn.execute("ROLLBACK")
                        free_remaining = max(0, FREE_DAILY_LIMIT - shared_used)
                        raise QuotaExceededError(free_remaining, credits)

                    conn.execute(
                        "UPDATE quota_accounts SET updated_at = ? WHERE device_id = ?",
                        (now, device_id),
                    )
                    conn.commit()
                except QuotaExceededError:
                    raise
                except Exception:
                    conn.execute("ROLLBACK")
                    raise

        status = self.get_status(device_id, usage_date)
        return {
            "source": source,
            "tier": tier_name,
            "freeRemaining": int(status["freeRemaining"]),
            "creditBalance": int(status["creditBalance"]),
        }

    def redeem_key(self, device_id: str, plain_key: str) -> int:
        normalized = normalize_license_key(plain_key)
        if len(normalized) < 8:
            raise InvalidLicenseKeyError("invalid key")
        key_hash = hash_license_key(normalized)
        now = time.time()
        with self._lock:
            with self._connect() as conn:
                conn.execute("BEGIN IMMEDIATE")
                try:
                    self._ensure_account(conn, device_id, now)
                    row = conn.execute(
                        "SELECT id, credits, status FROM license_keys WHERE key_hash = ?",
                        (key_hash,),
                    ).fetchone()
                    if row is None:
                        conn.execute("ROLLBACK")
                        raise InvalidLicenseKeyError("key not found")
                    if row["status"] != "unused":
                        conn.execute("ROLLBACK")
                        raise InvalidLicenseKeyError("key already used")

                    conn.execute(
                        "UPDATE license_keys SET status = 'redeemed', "
                        "redeemed_device_id = ?, redeemed_at = ? WHERE id = ?",
                        (device_id, now, row["id"]),
                    )
                    conn.execute(
                        "UPDATE quota_accounts SET credit_balance = credit_balance + ?, "
                        "updated_at = ? WHERE device_id = ?",
                        (int(row["credits"]), now, device_id),
                    )
                    conn.commit()
                    added = int(row["credits"])
                except InvalidLicenseKeyError:
                    raise
                except Exception:
                    conn.execute("ROLLBACK")
                    raise

        return added

    def _is_device_merged(self, conn: sqlite3.Connection, device_id: str) -> bool:
        row = conn.execute(
            "SELECT device_id FROM quota_device_merges WHERE device_id = ?",
            (device_id,),
        ).fetchone()
        return row is not None

    def merge_device_into_user(self, device_id: str, user_id: str, usage_date: str) -> bool:
        device_id = device_id.strip()
        user_id = user_id.strip()
        if not device_id or not user_id or device_id == user_id:
            return False
        now = time.time()
        with self._lock:
            with self._connect() as conn:
                if self._is_device_merged(conn, device_id):
                    return False
                conn.execute("BEGIN IMMEDIATE")
                try:
                    self._ensure_account(conn, device_id, now)
                    self._ensure_account(conn, user_id, now)
                    device_acct = conn.execute(
                        "SELECT credit_balance FROM quota_accounts WHERE device_id = ?",
                        (device_id,),
                    ).fetchone()
                    user_acct = conn.execute(
                        "SELECT credit_balance FROM quota_accounts WHERE device_id = ?",
                        (user_id,),
                    ).fetchone()
                    device_credits = int(device_acct["credit_balance"]) if device_acct else 0
                    user_credits = int(user_acct["credit_balance"]) if user_acct else 0
                    merged_credits = device_credits + user_credits
                    conn.execute(
                        "UPDATE quota_accounts SET credit_balance = ?, updated_at = ? WHERE device_id = ?",
                        (merged_credits, now, user_id),
                    )

                    tier_rows = conn.execute(
                        "SELECT tier_name, used_count FROM quota_tier_daily_usage "
                        "WHERE device_id = ? AND usage_date = ?",
                        (device_id, usage_date),
                    ).fetchall()
                    for row in tier_rows:
                        tier_name = str(row["tier_name"])
                        device_used = int(row["used_count"])
                        user_row = conn.execute(
                            "SELECT used_count FROM quota_tier_daily_usage "
                            "WHERE device_id = ? AND usage_date = ? AND tier_name = ?",
                            (user_id, usage_date, tier_name),
                        ).fetchone()
                        user_used = int(user_row["used_count"]) if user_row else 0
                        merged_used = max(device_used, user_used)
                        if user_row:
                            conn.execute(
                                "UPDATE quota_tier_daily_usage SET used_count = ? "
                                "WHERE device_id = ? AND usage_date = ? AND tier_name = ?",
                                (merged_used, user_id, usage_date, tier_name),
                            )
                        elif merged_used > 0:
                            conn.execute(
                                "INSERT INTO quota_tier_daily_usage "
                                "(device_id, usage_date, tier_name, used_count) VALUES (?, ?, ?, ?)",
                                (user_id, usage_date, tier_name, merged_used),
                            )

                    device_shared = self._shared_used(conn, device_id, usage_date)
                    user_shared = self._shared_used(conn, user_id, usage_date)
                    merged_shared = max(device_shared, user_shared)
                    user_shared_row = conn.execute(
                        "SELECT used_count FROM quota_daily_usage "
                        "WHERE device_id = ? AND usage_date = ?",
                        (user_id, usage_date),
                    ).fetchone()
                    if user_shared_row:
                        conn.execute(
                            "UPDATE quota_daily_usage SET used_count = ? "
                            "WHERE device_id = ? AND usage_date = ?",
                            (merged_shared, user_id, usage_date),
                        )
                    elif merged_shared > 0:
                        conn.execute(
                            "INSERT INTO quota_daily_usage (device_id, usage_date, used_count) "
                            "VALUES (?, ?, ?)",
                            (user_id, usage_date, merged_shared),
                        )

                    conn.execute(
                        "UPDATE license_keys SET redeemed_device_id = ? "
                        "WHERE redeemed_device_id = ?",
                        (user_id, device_id),
                    )
                    conn.execute(
                        "DELETE FROM quota_tier_daily_usage WHERE device_id = ?",
                        (device_id,),
                    )
                    conn.execute(
                        "DELETE FROM quota_daily_usage WHERE device_id = ?",
                        (device_id,),
                    )
                    conn.execute(
                        "DELETE FROM quota_accounts WHERE device_id = ?",
                        (device_id,),
                    )
                    conn.execute(
                        "INSERT INTO quota_device_merges (device_id, user_id, merged_at) "
                        "VALUES (?, ?, ?)",
                        (device_id, user_id, now),
                    )
                    conn.commit()
                    return True
                except Exception:
                    conn.execute("ROLLBACK")
                    raise

    def bind_phone(self, device_id: str, phone: str) -> None:
        now = time.time()
        with self._lock:
            with self._connect() as conn:
                conn.execute("BEGIN IMMEDIATE")
                try:
                    self._ensure_account(conn, device_id, now)
                    existing = conn.execute(
                        "SELECT device_id FROM quota_accounts WHERE phone = ? AND device_id != ?",
                        (phone, device_id),
                    ).fetchone()
                    if existing:
                        conn.execute("ROLLBACK")
                        raise PhoneAlreadyBoundError("phone already bound")
                    conn.execute(
                        "UPDATE quota_accounts SET phone = ?, updated_at = ? WHERE device_id = ?",
                        (phone, now, device_id),
                    )
                    conn.commit()
                except PhoneAlreadyBoundError:
                    raise
                except Exception:
                    conn.execute("ROLLBACK")
                    raise

    def insert_license_keys(
        self,
        entries: list[tuple[str, int, str, str | None]],
    ) -> int:
        now = time.time()
        with self._lock:
            with self._connect() as conn:
                for key_hash, credits, tier_label, note in entries:
                    conn.execute(
                        "INSERT INTO license_keys "
                        "(key_hash, credits, tier_label, status, note, created_at) "
                        "VALUES (?, ?, ?, 'unused', ?, ?)",
                        (key_hash, credits, tier_label, note, now),
                    )
                conn.commit()
        return len(entries)

    def list_license_keys(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
    ) -> tuple[list[dict], int]:
        limit = max(1, min(limit, 200))
        offset = max(0, offset)
        with self._lock:
            with self._connect() as conn:
                where = ""
                params: list[object] = []
                if status:
                    where = "WHERE status = ?"
                    params.append(status)
                total_row = conn.execute(
                    f"SELECT COUNT(*) AS cnt FROM license_keys {where}",
                    params,
                ).fetchone()
                rows = conn.execute(
                    f"SELECT id, credits, tier_label, status, note, created_at, "
                    f"redeemed_device_id, redeemed_at "
                    f"FROM license_keys {where} "
                    f"ORDER BY id DESC LIMIT ? OFFSET ?",
                    [*params, limit, offset],
                ).fetchall()
        items = [
            {
                "id": int(row["id"]),
                "credits": int(row["credits"]),
                "tierLabel": str(row["tier_label"]),
                "status": str(row["status"]),
                "note": row["note"],
                "createdAt": float(row["created_at"]),
                "redeemedDeviceId": row["redeemed_device_id"],
                "redeemedAt": float(row["redeemed_at"]) if row["redeemed_at"] else None,
            }
            for row in rows
        ]
        return items, int(total_row["cnt"])


def default_quota_db_path() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "quota.db"


def resolve_quota_db_path() -> Path:
    from app.config import settings

    raw = (settings.quota_db_path or "").strip()
    if raw:
        path = Path(raw).expanduser()
        logger.info("quota db path=%s", path)
        return path
    path = default_quota_db_path()
    logger.info("quota db path=%s (default)", path)
    return path
