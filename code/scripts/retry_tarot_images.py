# -*- coding: utf-8 -*-
"""Retry missing RWS tarot images from Wikimedia Commons."""

from __future__ import annotations

import json
import time
from pathlib import Path

import requests

DECK = Path(__file__).resolve().parents[1] / "backend" / "app" / "core" / "tarot" / "data" / "deck_rws.json"
IMG = Path(__file__).resolve().parents[1] / "frontend" / "public" / "tarot" / "rws"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TarotImageRetry/1.0"}


def main() -> int:
    deck = json.loads(DECK.read_text(encoding="utf-8"))
    IMG.mkdir(parents=True, exist_ok=True)
    ok = 0
    for card in deck.get("cards", []):
        dest = IMG / f"{card['id']}.jpg"
        if dest.exists() and dest.stat().st_size > 5000:
            continue
        commons_file = card.get("commonsFile") or ""
        if not commons_file:
            continue
        url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{commons_file}"
        for attempt in range(4):
            try:
                resp = requests.get(url, headers=HEADERS, timeout=120, allow_redirects=True)
                if resp.status_code == 429:
                    time.sleep(10 * (attempt + 1))
                    continue
                resp.raise_for_status()
                if "image" not in (resp.headers.get("Content-Type") or ""):
                    break
                dest.write_bytes(resp.content)
                ok += 1
                print(f"ok: {card['id']} <- {commons_file}")
                time.sleep(3)
                break
            except Exception as exc:
                if attempt == 3:
                    print(f"fail: {card['id']} ({exc})")
                time.sleep(5)
    total = len(list(IMG.glob("*.jpg")))
    print(f"downloaded this run: {ok}, total files: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
