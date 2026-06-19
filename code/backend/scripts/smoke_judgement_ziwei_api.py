"""HTTP smoke test for POST /api/v1/ziwei/judgement."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

CHART_BODY = {
    "name": "smoke",
    "calendarType": "solar",
    "year": 1990,
    "month": 5,
    "day": 15,
    "hour": 11,
    "minute": 30,
    "gender": 1,
    "useTrueSolarTime": False,
    "targetYear": 2026,
    "detailLevel": "pro",
    "question": "今年事业和财运如何",
    "rules": {
        "leapMonthRule": "next_month",
        "ziHourRule": "combined",
        "mutagenTable": "nan_pai",
        "chartSchool": "sanhe",
    },
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
    chart_resp = _post(base_url, "/api/v1/ziwei/chart", CHART_BODY)
    chart = chart_resp.get("chart") or {}
    judgement_resp = _post(
        base_url,
        "/api/v1/ziwei/judgement",
        {
            "chart": chart,
            "question": CHART_BODY["question"],
            "targetYear": CHART_BODY["targetYear"],
            "school": CHART_BODY["rules"]["chartSchool"],
            "useRag": use_rag,
        },
    )
    judgement = judgement_resp.get("judgement") or {}
    tiered = judgement.get("tieredEvidence") or {}
    judges = judgement.get("judges") or []
    enriched = judgement.get("enrichedChart") or {}
    palaces = enriched.get("palaces") or chart.get("palaces") or []
    return {
        "url": f"{base_url.rstrip('/')}/api/v1/ziwei/judgement",
        "status": "ok",
        "useRag": use_rag,
        "bureau": (chart.get("meta") or {}).get("bureau"),
        "topicId": (judgement.get("topic") or {}).get("topicId"),
        "confidence": judgement_resp.get("confidence"),
        "confidenceBand": judgement_resp.get("confidenceBand"),
        "judgeCount": len(judges),
        "judgeRoles": [row.get("role") for row in judges],
        "stepCount": len(judgement.get("steps") or []),
        "conflicts": judgement_resp.get("conflicts") or [],
        "tieredSummary": judgement.get("tieredEvidenceSummary") or {},
        "primaryEvidenceCount": len(tiered.get("primaryEvidence") or []),
        "secondaryEvidenceCount": len(tiered.get("secondaryEvidence") or []),
        "caseReferenceCount": len(tiered.get("caseReference") or []),
        "schoolCommentaryCount": len(tiered.get("schoolCommentary") or []),
        "excludedCount": len(tiered.get("excludedOrUnreadable") or []),
        "enrichedPalaceCount": len(palaces),
        "hasRulesMeta": bool(judgement.get("rulesMeta") or chart.get("rulesMeta")),
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
    ok = summary.get("status") == "ok" and summary.get("judgeCount", 0) >= 7
    if args.rag:
        ok = ok and summary.get("primaryEvidenceCount", 0) > 0
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
