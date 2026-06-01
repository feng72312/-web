#!/usr/bin/env python
"""Compare DeepSeek models on val split (small benchmark)."""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.benchmark.contest8_eval import run_eval
from app.core.agent.deepseek import DeepSeekError

MODELS = ("deepseek-chat", "deepseek-v4-pro", "deepseek-reasoner")


async def main_async(limit: int | None, votes: int) -> None:
    rows = []
    for model in MODELS:
        try:
            report = await run_eval(
                "val",
                model_id=model,
                limit=limit,
                use_knowledge=True,
                use_case_rag=True,
                use_fewshot=True,
                votes=votes,
                temperature=0.2,
                theme_fewshot=True,
            )
            rows.append(
                {
                    "model": model,
                    "correct": report.correct,
                    "total": report.total,
                    "accuracy": report.accuracy,
                    "error": "",
                }
            )
            print(f"{model}: {report.correct}/{report.total} = {report.accuracy:.1%}")
        except DeepSeekError as err:
            rows.append(
                {
                    "model": model,
                    "correct": 0,
                    "total": 0,
                    "accuracy": 0.0,
                    "error": str(err),
                }
            )
            print(f"{model}: skipped ({err})")
    out = ROOT / "data" / "reports" / "contest8_val_model_ab.json"
    out.write_text(json.dumps({"results": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--votes", type=int, default=1)
    args = parser.parse_args()
    asyncio.run(main_async(args.limit, args.votes))


if __name__ == "__main__":
    main()
