# -*- coding: utf-8 -*-
"""Verify utils API is registered (run after starting backend)."""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"


def main() -> int:
    try:
        openapi = json.loads(urllib.request.urlopen(f"{BASE}/openapi.json", timeout=5).read())
    except Exception as err:
        print(f"cannot reach backend at {BASE}: {err}")
        return 1
    paths = openapi.get("paths", {})
    divine = "/api/v1/utils/zhuge/divine"
    if divine not in paths:
        print(f"MISSING {divine} - restart backend (close old Bazi Backend window, run start-backend.bat)")
        return 1
    body = json.dumps({"chars": "佑咱统", "strokes": [7, 9, 12]}).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE}{divine}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
    print(f"OK utils zhuge divine qianNo={resp.get('qianNo')} at {BASE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
