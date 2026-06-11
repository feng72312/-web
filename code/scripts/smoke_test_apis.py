import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime

BASE = os.environ.get("API_BASE", "http://127.0.0.1:8001/api/v1").rstrip("/")
HEADERS = {
    "Content-Type": "application/json",
    "X-Device-Id": "smoke-test-device",
}


def post(path: str, body: dict) -> tuple[bool, str]:
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=data,
        headers=HEADERS,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return True, f"HTTP {resp.status}"
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        return False, f"HTTP {exc.code} {detail}"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def main() -> int:
    now = datetime.now()
    tests = [
        ("paipan", "/paipan", {
            "name": "test",
            "calendarType": "solar",
            "year": 1990,
            "month": 5,
            "day": 15,
            "isLeapMonth": False,
            "hour": 10,
            "minute": 30,
            "gender": 1,
        }),
        ("meihua", "/meihua/divine", {
            "question": "cooperation",
            "method": "number",
            "calendarType": "solar",
            "numbers": [8],
        }),
        ("liuyao", "/liuyao/divine", {
            "question": "exam",
            "method": "number",
            "calendarType": "solar",
            "numbers": [3, 5, 7],
        }),
        ("qimen", "/qimen/chart", {
            "question": "travel",
            "category": "shizhan",
            "method": "chaibu",
            "direction": "",
            "useTrueSolarTime": False,
            "longitude": 120,
            "calendarType": "solar",
            "isLeapMonth": False,
            "year": now.year,
            "month": now.month,
            "day": now.day,
            "hour": now.hour,
            "minute": now.minute,
            "second": 0,
        }),
        ("liuren", "/liuren/chart", {
            "question": "affairs",
            "category": "shizhan",
            "castMethod": "both",
            "jinkouDifen": "",
            "guiRenMode": 0,
            "useTrueSolarTime": False,
            "longitude": 120,
            "calendarType": "solar",
            "isLeapMonth": False,
            "year": now.year,
            "month": now.month,
            "day": now.day,
            "hour": now.hour,
            "minute": now.minute,
            "second": 0,
        }),
        ("fengshui", "/fengshui/chart", {
            "question": "home",
            "method": "bazhai",
            "scene": "residence",
            "birthYear": 1990,
            "gender": 1,
            "sittingMountain": "zi",
        }),
        ("ziwei", "/ziwei/chart", {
            "name": "test",
            "calendarType": "solar",
            "year": 1990,
            "month": 5,
            "day": 15,
            "isLeapMonth": False,
            "hour": 10,
            "minute": 30,
            "gender": 1,
            "useTrueSolarTime": False,
            "longitude": 120,
            "targetYear": now.year,
            "question": "career",
            "rules": {
                "leapMonthRule": "next_month",
                "ziHourRule": "combined",
                "mutagenTable": "nan_pai",
            },
        }),
        ("xingming", "/xingming/chart", {
            "name": "test",
            "calendarType": "solar",
            "year": 1990,
            "month": 5,
            "day": 15,
            "isLeapMonth": False,
            "hour": 10,
            "minute": 30,
            "gender": 1,
            "useTrueSolarTime": True,
            "longitude": 120,
            "latitude": 35,
            "targetYear": now.year,
            "question": "wealth",
            "rules": {
                "school": "guolao_v1",
                "ziHourRule": "combined",
                "dayNightRule": "auto",
            },
        }),
        ("zhuge", "/utils/zhuge/divine", {
            "chars": "\u6797\u5c71\u51b2",
            "question": "job",
        }),
        ("jiemeng", "/utils/jiemeng/search", {
            "dream": "\u68a6\u89c1\u5929\u95e8\u5f00\u4e58\u9f99\u4e0a\u5929",
            "limit": 5,
        }),
        ("naming", "/utils/naming/analyze", {
            "surname": "\u674e",
            "givenName": "\u660e\u8f69",
            "birth": None,
        }),
        ("hepan", "/hepan/chart", {
            "personA": {
                "name": "A",
                "calendarType": "solar",
                "year": 1990,
                "month": 5,
                "day": 15,
                "isLeapMonth": False,
                "hour": 10,
                "minute": 30,
                "gender": 1,
            },
            "personB": {
                "name": "B",
                "calendarType": "solar",
                "year": 1992,
                "month": 8,
                "day": 20,
                "isLeapMonth": False,
                "hour": 14,
                "minute": 0,
                "gender": 0,
            },
            "scene": "marriage",
            "discipline": "auto",
            "question": "match",
            "useTrueSolarTime": False,
            "longitude": 120,
            "ziweiRules": {
                "leapMonthRule": "next_month",
                "ziHourRule": "combined",
                "mutagenTable": "nan_pai",
            },
        }),
    ]

    passed = 0
    failed = 0
    print(f"API base: {BASE}")
    for name, path, body in tests:
        ok, msg = post(path, body)
        tag = "PASS" if ok else "FAIL"
        print(f"[{tag}] {name} {msg}")
        if ok:
            passed += 1
        else:
            failed += 1

    print(f"\nSummary: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
