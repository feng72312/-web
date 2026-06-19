"""HTTP smoke test for POST /api/v1/liuyao/judgement."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

DIVINE_BODY = {
    "question": "最近身体不舒服, 能否痊愈",
    "method": "coin",
    "coinLines": [9, 7, 8, 6, 7, 8],
    "year": 2024,
    "month": 11,
    "day": 8,
    "hour": 14,
    "minute": 0,
    "second": 0,
    "calendarType": "solar",
}


def _post(base_url: str, path: str, body: dict) -> dict:
    url = f"{base_url.rstrip('/')}{path}"
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run_smoke(base_url: str, *, use_rag: bool) -> dict:
    divine = _post(base_url, "/api/v1/liuyao/divine", DIVINE_BODY)
    chart = divine.get("chart") or {}
    judgement_resp = _post(
        base_url,
        "/api/v1/liuyao/judgement",
        {
            "chart": chart,
            "question": DIVINE_BODY["question"],
            "useRag": use_rag,
        },
    )
    judgement = judgement_resp.get("judgement") or {}
    tiered = judgement.get("tieredEvidence") or {}
    judges = judgement.get("judges") or []
    enriched = judgement.get("enrichedChart") or {}
    return {
        "url": f"{base_url.rstrip('/')}/api/v1/liuyao/judgement",
        "status": "ok",
        "useRag": use_rag,
        "benGua": (chart.get("benGua") or {}).get("name"),
        "topicId": (judgement.get("topic") or {}).get("topicId"),
        "confidence": judgement_resp.get("confidence"),
        "confidenceBand": judgement_resp.get("confidenceBand"),
        "judgeCount": len(judges),
        "stepCount": len(judgement.get("steps") or []),
        "conflicts": judgement_resp.get("conflicts") or [],
        "tieredSummary": judgement.get("tieredEvidenceSummary") or {},
        "primaryEvidenceCount": len(tiered.get("primaryEvidence") or []),
        "secondaryEvidenceCount": len(tiered.get("secondaryEvidence") or []),
        "caseReferenceCount": len(tiered.get("caseReference") or []),
        "modernSupportCount": len(tiered.get("modernSupport") or []),
        "excludedCount": len(tiered.get("excludedOrLowTrust") or []),
        "enrichedLineCount": len(enriched.get("lines") or []),
        "hasKongPoState": bool(
            ((enriched.get("lines") or [{}])[0] or {}).get("kongPoState")
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://127.0.0.1:8000")
    parser.add_argument("--rag", action="store_true")
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    try:
        summary = run_smoke(args.base, use_rag=args.rag)
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", errors="replace")[:500]
        print(json.dumps({"status": "http_error", "code": err.code, "detail": detail}, ensure_ascii=False))
        return 1
    except urllib.error.URLError as err:
        print(json.dumps({"status": "url_error", "reason": str(err.reason)}, ensure_ascii=False))
        return 1
    text = json.dumps(summary, ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text)
    ok = summary.get("status") == "ok" and summary.get("judgeCount", 0) >= 8
    if args.rag:
        ok = ok and summary.get("primaryEvidenceCount", 0) > 0
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
