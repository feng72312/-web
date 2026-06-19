#!/usr/bin/env python
"""Run Contest8 MCQ eval filtered by question theme(s)."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.benchmark.contest8_dataset import flatten_questions
from app.benchmark.contest8_eval import (
    EvalReport,
    build_deepseek_client,
    predict_one,
)
from app.benchmark.contest8_fewshot import select_fewshot_by_theme
from app.benchmark.contest8_rag import infer_question_theme
from app.core.knowledge.contest_channel_route import (
    has_explicit_timing_signal,
    is_yingqi_question,
    uses_full_judgement_chain,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def _parse_themes(raw: str) -> list[str]:
    return [part.strip() for part in raw.split(",") if part.strip()]


def _filter_questions(
    years: list[int] | None,
    themes: list[str],
    question_ids: list[str] | None = None,
) -> list:
    rows = flatten_questions(years or [2021, 2022, 2023, 2024, 2025])
    if question_ids:
        id_set = set(question_ids)
        rows = [q for q in rows if q.question_id in id_set]
    if not themes:
        return rows
    theme_set = set(themes)
    return [q for q in rows if infer_question_theme(q.question) in theme_set]


async def run_theme_eval(
    questions: list,
    *,
    model_id: str | None,
    use_knowledge: bool,
    use_case_rag: bool,
    use_fewshot: bool,
    votes: int = 1,
) -> EvalReport:
    client = build_deepseek_client()
    results = []
    total = len(questions)
    for idx, q in enumerate(questions, start=1):
        logging.info("theme eval progress %s/%s %s", idx, total, q.question_id)
        fs = None
        if use_fewshot:
            fs = select_fewshot_by_theme(
                infer_question_theme(q.question),
                exclude_question_id=q.question_id,
                max_items=3,
            )
        results.append(
            await predict_one(
                q,
                client,
                model_id=model_id,
                use_knowledge=use_knowledge,
                use_case_rag=use_case_rag,
                fewshot_examples=fs,
                votes=votes,
            )
        )
    correct = sum(1 for r in results if r.correct)
    total_n = len(results)
    acc = correct / total_n if total_n else 0.0
    return EvalReport(
        split="theme-subset",
        total=total_n,
        correct=correct,
        accuracy=acc,
        results=results,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Contest8 theme subset benchmark")
    parser.add_argument(
        "--themes",
        default="学历",
        help="comma-separated themes, e.g. 学历,家庭出身",
    )
    parser.add_argument(
        "--years",
        default="",
        help="comma-separated years to include, default all 2021-2025",
    )
    parser.add_argument(
        "--ids",
        default="",
        help="comma-separated question_id filter, e.g. P018-Q6,P027-Q11",
    )
    parser.add_argument("--model", default=None)
    parser.add_argument("--fewshot", action="store_true")
    parser.add_argument(
        "--votes",
        type=int,
        default=1,
        help="base votes per question (1-5); full channel auto-bumps 1->3",
    )
    parser.add_argument("--no-knowledge", action="store_true")
    parser.add_argument("--no-case-rag", action="store_true")
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "data" / "reports" / "contest8_sub_theme.json",
    )
    parser.add_argument("--tag", default="", help="suffix for default output filename")
    args = parser.parse_args()

    themes = _parse_themes(args.themes)
    years = [int(y.strip()) for y in args.years.split(",") if y.strip()] or None
    question_ids = [part.strip() for part in args.ids.split(",") if part.strip()] or None
    questions = _filter_questions(years, themes, question_ids)
    if not questions:
        print("no questions matched themes:", themes)
        sys.exit(1)

    print(f"themes={themes} count={len(questions)}")
    for q in questions:
        ch = (
            "full"
            if uses_full_judgement_chain(q.question, q.options)
            else "yingqi"
            if is_yingqi_question(q.question, q.options)
            else "static-light"
            if infer_question_theme(q.question) in ("学历", "家庭出身", "子女")
            and not has_explicit_timing_signal(q.question, q.options)
            else "other"
        )
        print(f"  {q.question_id} ({q.year}) channel={ch}")

    report = asyncio.run(
        run_theme_eval(
            questions,
            model_id=args.model,
            use_knowledge=not args.no_knowledge,
            use_case_rag=not args.no_case_rag,
            use_fewshot=args.fewshot,
            votes=args.votes,
        )
    )
    out = args.out
    if args.tag and out.name == "contest8_sub_theme.json":
        out = out.parent / f"contest8_sub_{args.tag}.json"
    payload = report.to_dict()
    payload["themes"] = themes
    payload["votes"] = args.votes
    payload["questionIds"] = [q.question_id for q in questions]
    if question_ids:
        payload["filterIds"] = question_ids
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"accuracy={report.accuracy:.1%} ({report.correct}/{report.total}) -> {out}")


if __name__ == "__main__":
    main()
