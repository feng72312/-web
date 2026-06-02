from __future__ import annotations

import re
from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.quota.keys import (
    credits_for_tier,
    generate_license_key,
    hash_license_key,
    normalize_license_key,
)
from app.core.quota.store import (
    InvalidLicenseKeyError,
    PhoneAlreadyBoundError,
    QuotaExceededError,
    QuotaStore,
)

_BEIJING = ZoneInfo("Asia/Shanghai")
_PHONE_RE = re.compile(r"^1[3-9]\d{9}$")


class QuotaService:
    def __init__(self, store: QuotaStore) -> None:
        self._store = store

    @staticmethod
    def beijing_date() -> str:
        return datetime.now(_BEIJING).strftime("%Y-%m-%d")

    def get_status(self, device_id: str) -> dict:
        return self._store.get_status(device_id, self.beijing_date())

    def consume_one(self, device_id: str, tier_name: str = "大师") -> dict:
        return self._store.consume_one(device_id, self.beijing_date(), tier_name)

    def redeem_key(self, device_id: str, plain_key: str) -> dict[str, int]:
        added = self._store.redeem_key(device_id, plain_key)
        status = self.get_status(device_id)
        return {
            "addedCredits": added,
            "creditBalance": int(status["creditBalance"]),
        }

    def bind_phone(self, device_id: str, phone: str) -> None:
        normalized = phone.strip()
        if not _PHONE_RE.match(normalized):
            raise ValueError("invalid phone number")
        self._store.bind_phone(device_id, normalized)

    def merge_device_into_user(self, device_id: str, user_id: str) -> bool:
        return self._store.merge_device_into_user(device_id, user_id, self.beijing_date())

    def generate_license_keys(
        self,
        tier: int,
        count: int,
        note: str | None = None,
    ) -> list[dict[str, int | str]]:
        credits = credits_for_tier(tier)
        batch: list[tuple[str, int, str, str | None]] = []
        generated: list[dict[str, int | str]] = []
        trimmed_note = (note or "").strip() or None

        for _ in range(count):
            plain = generate_license_key()
            normalized = normalize_license_key(plain)
            batch.append(
                (
                    hash_license_key(normalized),
                    credits,
                    str(tier),
                    trimmed_note,
                )
            )
            generated.append({"key": plain, "tier": tier, "credits": credits})

        self._store.insert_license_keys(batch)
        return generated

    def list_license_keys(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
    ) -> tuple[list[dict], int]:
        return self._store.list_license_keys(limit=limit, offset=offset, status=status)


__all__ = [
    "QuotaService",
    "QuotaExceededError",
    "InvalidLicenseKeyError",
    "PhoneAlreadyBoundError",
]
