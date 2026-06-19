"""Local smoke test for ZiweiJudgementChain."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.ziwei.engine import ZiweiEngine
from app.core.ziwei.judgement.chain import ZiweiJudgementChain
from app.core.ziwei.models import ZiweiInput
from app.core.ziwei.rules import ZiweiRules

pytest_importorskip = __import__("pytest").importorskip
pytest_importorskip("iztro_py")


def build_sample_chart() -> dict:
    engine = ZiweiEngine()
    result = engine.chart(
        ZiweiInput(
            calendar_type="solar",
            year=1990,
            month=5,
            day=15,
            hour=11,
            minute=30,
            gender=1,
            detail_level="pro",
            question="今年事业和财运如何",
            rules=ZiweiRules(),
        )
    )
    return result.to_dict()


async def run_smoke(*, use_rag: bool) -> dict:
    chart = build_sample_chart()
    report = await ZiweiJudgementChain(use_rag=use_rag).run(
        chart,
        question="今年事业和财运如何",
    )
    payload = report.to_dict()
    judges = payload.get("judges") or []
    roles = [row.get("role") for row in judges]
    return {
        "useRag": use_rag,
        "stepCount": len(payload.get("steps") or []),
        "judgeCount": len(judges),
        "judgeRoles": roles,
        "topicId": (payload.get("topic") or {}).get("topicId"),
        "confidence": (payload.get("arbitration") or {}).get("confidenceScore"),
        "confidenceBand": (payload.get("arbitration") or {}).get("confidenceBand"),
        "conflicts": (payload.get("arbitration") or {}).get("conflicts") or [],
        "primaryEvidenceCount": len((payload.get("tieredEvidence") or {}).get("primaryEvidence") or []),
        "ruleIds": [rid for row in judges for rid in (row.get("ruleIds") or [])],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rag", action="store_true", help="enable RAG retrieval")
    parser.add_argument(
        "--output",
        default=str(
            BACKEND_ROOT.parents[1]
            / "report"
            / "紫薇斗数最强方案"
            / "smoke_judgement_ziwei_local.json"
        ),
    )
    args = parser.parse_args()
    summary = asyncio.run(run_smoke(use_rag=args.rag))
    text = json.dumps(summary, ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    ok = summary["judgeCount"] >= 6 and summary["stepCount"] >= 6
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
