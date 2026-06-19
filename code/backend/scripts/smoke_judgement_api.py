"""HTTP smoke test for POST /api/v1/paipan/judgement."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

SAMPLE_BODY = {
    "name": "smoke",
    "calendarType": "solar",
    "year": 1990,
    "month": 3,
    "day": 15,
    "hour": 10,
    "minute": 0,
    "second": 0,
    "gender": 1,
    "question": "2024年事业财运如何",
}


def run_smoke(base_url: str) -> dict:
    url = f"{base_url.rstrip('/')}/api/v1/paipan/judgement"
    payload = json.dumps(SAMPLE_BODY).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    top_summary = body.get("tieredEvidenceSummary") or {}
    judgement = body.get("judgement") or {}
    nested_summary = judgement.get("tieredEvidenceSummary") or {}
    tiered = judgement.get("tieredEvidence") or {}
    opinions = (judgement.get("arbitration") or {}).get("judgeOpinions") or []
    return {
        "url": url,
        "status": "ok",
        "dayMaster": (body.get("chart") or {}).get("dayMaster"),
        "topTieredSummaryTotal": top_summary.get("total", 0),
        "nestedTieredSummaryTotal": nested_summary.get("total", 0),
        "topGroups": [g.get("label") for g in top_summary.get("groups") or []],
        "caseOverreachRisk": top_summary.get("caseOverreachRisk"),
        "primaryEvidenceCount": len(tiered.get("primaryEvidence") or []),
        "caseReferenceCount": len(tiered.get("caseReference") or []),
        "opinionCount": len(opinions),
        "note": top_summary.get("note") or nested_summary.get("note") or "",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://127.0.0.1:8000")
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    try:
        summary = run_smoke(args.base)
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
    ok = (
        summary.get("status") == "ok"
        and summary.get("opinionCount", 0) >= 5
        and summary.get("primaryEvidenceCount", 0) > 0
        and (
            summary.get("topTieredSummaryTotal", 0) > 0
            or summary.get("nestedTieredSummaryTotal", 0) > 0
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
