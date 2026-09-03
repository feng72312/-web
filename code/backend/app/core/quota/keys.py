from __future__ import annotations

import hashlib
import secrets
import string

TIERS: dict[int, int] = {
    10: 20,
    20: 50,
    50: 150,
    100: 500,
}

# Shared daily pool after tier-specific free quota is used up.
FREE_DAILY_LIMIT = 9999

# Per model tier free uses per day (Beijing date).
TIER_FREE_DAILY_LIMITS: dict[str, int] = {
    "小师傅": 9999,
    "大师": 9999,
    "资深道长": 9999,
}

TIER_FREE_ORDER: tuple[str, ...] = ("小师傅", "大师", "资深道长")
_KEY_ALPHABET = string.ascii_uppercase + string.digits


def normalize_license_key(raw: str) -> str:
    return raw.strip().upper().replace(" ", "")


def hash_license_key(normalized: str) -> str:
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def generate_license_key() -> str:
    parts = [
        "".join(secrets.choice(_KEY_ALPHABET) for _ in range(4))
        for _ in range(3)
    ]
    return f"ZY-{'-'.join(parts)}"


def credits_for_tier(tier: int) -> int:
    if tier not in TIERS:
        raise ValueError(f"unknown tier {tier}, expected one of {sorted(TIERS)}")
    return TIERS[tier]


def tier_free_daily_limit(tier_name: str) -> int:
    return TIER_FREE_DAILY_LIMITS.get(tier_name, TIER_FREE_DAILY_LIMITS["大师"])
