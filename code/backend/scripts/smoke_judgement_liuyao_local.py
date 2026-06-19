"""Local smoke test for LiuyaoJudgementChain without loading full FastAPI app."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.liuyao.engine import LiuyaoEngine
from app.core.liuyao.judgement.chain import LiuyaoJudgementChain
from app.core.liuyao.models import LiuyaoInput


def build_sample_chart() -> dict:
    engine = LiuyaoEngine()
    return engine.divine(
        LiuyaoInput(
            question="最近身体不舒服, 能否痊愈",
            method="coin",
            coin_lines=[9, 7, 8, 6, 7, 8],
            year=2024,
            month=11,
            day=8,
            hour=14,
            minute=0,
        )
    ).to_dict()


async def run_smoke(*, use_rag: bool) -> dict:
    chart = build_sample_chart()
    report = await LiuyaoJudgementChain(use_rag=use_rag).run(
        chart,
        question=chart.get("input", {}).get("question", ""),
    )
    payload = report.to_dict()
    arbitration = payload.get("arbitration") or {}
    return {
        "useRag": use_rag,
        "benGua": (chart.get("benGua") or {}).get("name"),
        "topicId": (payload.get("topic") or {}).get("topicId"),
        "yongShen": payload.get("yongShen"),
        "stepCount": len(payload.get("steps") or []),
        "judgeCount": len(payload.get("judges") or []),
        "confidence": arbitration.get("confidenceScore"),
        "confidenceBand": arbitration.get("confidenceBand"),
        "conflicts": arbitration.get("conflicts") or [],
        "arbitrationSummary": arbitration.get("summary"),
        "ruleIds": [
            rid
            for row in payload.get("judges") or []
            for rid in (row.get("ruleIds") or [])
        ],
        "wangShuaiFlags": next(
            (
                row.get("flags")
                for row in payload.get("judges") or []
                if row.get("role") == "wang_shuai"
            ),
            {},
        ),
        "dongBianSummary": next(
            (
                row.get("summary")
                for row in payload.get("judges") or []
                if row.get("role") == "dong_bian"
            ),
            "",
        ),
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
    ok = summary["stepCount"] >= 8 and summary["judgeCount"] >= 8
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
