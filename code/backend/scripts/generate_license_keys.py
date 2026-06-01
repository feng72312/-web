#!/usr/bin/env python3
"""Generate license keys for manual sale (store hash only in DB)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.quota.keys import (  # noqa: E402
    TIERS,
    credits_for_tier,
    generate_license_key,
    hash_license_key,
    normalize_license_key,
)
from app.core.quota.store import QuotaStore, resolve_quota_db_path  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate AI quota license keys")
    parser.add_argument(
        "--tier",
        type=int,
        required=True,
        choices=sorted(TIERS.keys()),
        help="price tier yuan: 10/20/50/100",
    )
    parser.add_argument("--count", type=int, default=1, help="number of keys")
    parser.add_argument("--note", type=str, default="", help="admin note")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="optional file to write plaintext keys",
    )
    args = parser.parse_args()

    credits = credits_for_tier(args.tier)
    store = QuotaStore(resolve_quota_db_path())
    plaintext_keys: list[str] = []
    batch: list[tuple[str, int, str, str | None]] = []

    for _ in range(args.count):
        plain = generate_license_key()
        normalized = normalize_license_key(plain)
        plaintext_keys.append(plain)
        batch.append(
            (
                hash_license_key(normalized),
                credits,
                str(args.tier),
                args.note or None,
            )
        )

    store.insert_license_keys(batch)

    print(f"Generated {len(plaintext_keys)} keys tier={args.tier}yuan credits={credits}")
    for key in plaintext_keys:
        print(key)

    if args.out:
        args.out.write_text("\n".join(plaintext_keys) + "\n", encoding="utf-8")
        print(f"Saved to {args.out}")


if __name__ == "__main__":
    main()
