#!/usr/bin/env python
"""
Run Global Fortune-teller Competition (Contest8) MCQ benchmark.

Splits (default):
  train: 2021-2023 (120 questions)
  val:   2024 (40 questions)
  test:  2025 (40 questions)

Requires BAZI_DEEPSEEK_API_KEY or BAZI_CURSOR_API_KEY in code/backend/.env
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.benchmark.contest8_dataset import split_summary
from app.benchmark.contest8_eval import run_eval, save_report

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Contest8 Bazi MCQ benchmark")
    parser.add_argument(
        "--split",
        choices=("train", "val", "test", "all"),
        default="val",
        help="dataset split to evaluate",
    )
    parser.add_argument("--model", default=None, help="model id, e.g. deepseek-chat")
    parser.add_argument("--limit", type=int, default=None, help="max questions")
    parser.add_argument("--no-knowledge", action="store_true", help="disable knowledge graph")
    parser.add_argument(
        "--no-case-rag",
        action="store_true",
        help="disable 命例 RAG retrieval from knowledge base",
    )
    parser.add_argument("--fewshot", action="store_true", help="include train few-shot examples")
    parser.add_argument(
        "--votes",
        type=int,
        default=1,
        help="majority votes per question (1-5, structured reasoning only)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="LLM temperature (default 0.2 for structured reasoning)",
    )
    parser.add_argument(
        "--static-fewshot",
        action="store_true",
        help="use contest8_fewshot.json instead of theme-matched train examples",
    )
    parser.add_argument(
        "--fusion",
        action="store_true",
        help="bazi+liuyao dual channel (birth time gua, dynamic merge)",
    )
    parser.add_argument(
        "--liuyao-only",
        action="store_true",
        help="liuyao time-gua MCQ only (no bazi channel)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="report json path (default: data/reports/contest8_<split>.json)",
    )
    args = parser.parse_args()

    summary = split_summary()
    print("dataset:", summary)

    splits = ("train", "val", "test") if args.split == "all" else (args.split,)
    for name in splits:
        report = asyncio.run(
            run_eval(
                name,  # type: ignore[arg-type]
                model_id=args.model,
                limit=args.limit,
                use_knowledge=not args.no_knowledge,
                use_case_rag=not args.no_case_rag,
                use_fewshot=args.fewshot,
                use_fusion=args.fusion,
                use_liuyao_only=args.liuyao_only,
                votes=args.votes,
                temperature=args.temperature,
                theme_fewshot=not args.static_fewshot,
            )
        )
        suffix = "_fusion" if args.fusion else "_liuyao" if args.liuyao_only else ""
        out = args.out or (ROOT / "data" / "reports" / f"contest8_{name}{suffix}.json")
        if args.split == "all":
            out = ROOT / "data" / "reports" / f"contest8_{name}.json"
        save_report(report, out)
        print(
            f"[{name}] accuracy={report.accuracy:.1%} "
            f"({report.correct}/{report.total}) -> {out}"
        )


if __name__ == "__main__":
    main()
