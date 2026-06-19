"""Local smoke test for BaziJudgementChain without loading full FastAPI app."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.judgement.chain import BaziJudgementChain
from app.core.paipan.engine import PaipanEngine
from app.core.paipan.models import PaipanInput


def build_sample_chart() -> dict:
    engine = PaipanEngine()
    result = engine.calculate(
        PaipanInput(
            name="local-smoke",
            calendar_type="solar",
            year=1990,
            month=3,
            day=15,
            hour=10,
            minute=0,
            gender=1,
            is_leap_month=False,
        ),
        include_luck_timeline=False,
    )
    return result.to_dict()


async def run_smoke(*, use_rag: bool) -> dict:
    chart = build_sample_chart()
    report = await BaziJudgementChain(use_rag=use_rag).run(chart)
    payload = report.to_dict()
    return {
        "useRag": use_rag,
        "dayMaster": chart.get("dayMaster"),
        "stepCount": len(payload.get("steps") or []),
        "opinionCount": len((payload.get("arbitration") or {}).get("judgeOpinions") or []),
        "evidenceChainCount": len(payload.get("evidenceChain") or []),
        "caseReferenceCount": len((payload.get("tieredEvidence") or {}).get("caseReference") or []),
        "primaryEvidenceCount": len((payload.get("tieredEvidence") or {}).get("primaryEvidence") or []),
        "lookupKeys": list((payload.get("lookupKeys") or {}).keys()),
        "ruleIds": [
            rid
            for row in (payload.get("arbitration") or {}).get("judgeOpinions") or []
            for rid in (row.get("ruleIds") or [])
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rag", action="store_true", help="enable RAG retrieval")
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    summary = asyncio.run(run_smoke(use_rag=args.rag))
    text = json.dumps(summary, ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    ok = summary["stepCount"] >= 8 and summary["opinionCount"] >= 5
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
