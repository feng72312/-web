"""Offline val-split judgement baseline without LLM calls."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from collections import Counter
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.benchmark.contest8_benchmark_meta import check_judgement_coverage, enrich_question
from app.benchmark.contest8_chart import build_chart_for_question
from app.benchmark.contest8_dataset import load_split
from app.core.judgement.chain import BaziJudgementChain


async def run_baseline(split: str, *, limit: int, use_rag: bool, question_ids: list[str] | None = None) -> dict:
    from app.core.paipan.engine import PaipanEngine
    from app.core.paipan.rules import PaipanRules
    from app.config import settings
    from app.core.analysis.registry import build_default_registry

    questions = load_split(split)  # type: ignore[arg-type]
    if question_ids:
        id_set = set(question_ids)
        questions = [q for q in questions if q.question_id in id_set]
    elif limit > 0:
        questions = questions[:limit]
    chain = BaziJudgementChain(use_rag=use_rag)
    engine = PaipanEngine(
        rules=PaipanRules(
            sect=settings.paipan_sect,
            early_zishi_mode=settings.early_zishi_mode,
        )
    )
    registry = build_default_registry()
    rows = []
    coverage_ok = 0
    event_liunian_ok = 0
    case_overreach = 0
    label_counter: Counter[str] = Counter()
    total = len(questions)
    for idx, item in enumerate(questions, start=1):
        print(f"[{idx}/{total}] {item.question_id}", flush=True)
        meta = enrich_question(item)
        chart = build_chart_for_question(
            item,
            engine=engine,
            registry=registry,
            include_luck_timeline=False,
        )
        report = await chain.run(
            chart,
            question=item.question,
            benchmark_meta=meta,
        )
        payload = report.to_dict()
        coverage = check_judgement_coverage(payload, meta)
        tiered = payload.get("tieredEvidence") or {}
        primary_count = len(tiered.get("primaryEvidence") or [])
        if coverage.get("covered"):
            coverage_ok += 1
        if coverage.get("eventLiunianCovered"):
            event_liunian_ok += 1
        if coverage.get("caseOverreach"):
            case_overreach += 1
        for tag in coverage.get("missingTags") or []:
            label_counter[f"missing:{tag}"] += 1
        for tag in coverage.get("missingEventLiunian") or []:
            label_counter[f"missingEvent:{tag}"] += 1
        rows.append(
            {
                "questionId": item.question_id,
                "year": item.year,
                "meta": meta,
                "coverage": coverage,
                "primaryEvidenceCount": primary_count,
                "tieredSummaryTotal": (payload.get("tieredEvidenceSummary") or {}).get("total", 0),
                "ruleIds": [
                    rid
                    for opinion in (payload.get("arbitration") or {}).get("judgeOpinions") or []
                    for rid in (opinion.get("ruleIds") or [])
                ],
            }
        )
    return {
        "split": split,
        "total": len(questions),
        "coverageOk": coverage_ok,
        "coverageRate": round(coverage_ok / len(questions), 4) if questions else 0.0,
        "eventLiunianOk": event_liunian_ok,
        "eventLiunianRate": round(event_liunian_ok / len(questions), 4) if questions else 0.0,
        "caseOverreach": case_overreach,
        "primaryEvidenceMin": min((row["primaryEvidenceCount"] for row in rows), default=0),
        "primaryEvidenceMax": max((row["primaryEvidenceCount"] for row in rows), default=0),
        "missingTagDistribution": dict(label_counter),
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="val")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--ids", default="", help="comma-separated question ids")
    parser.add_argument("--from-regression", default="", help="regression json to pick sample ids")
    parser.add_argument("--sample-label", default="", help="wrong_tiaohou or wrong_liunian when using --from-regression")
    parser.add_argument("--sample-size", type=int, default=4, help="per label when using --from-regression")
    parser.add_argument("--rag", action="store_true")
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    question_ids: list[str] | None = None
    if args.ids:
        question_ids = [part.strip() for part in args.ids.split(",") if part.strip()]
    elif args.from_regression:
        regression = json.loads(Path(args.from_regression).read_text(encoding="utf-8"))
        labels = [args.sample_label] if args.sample_label else ["wrong_tiaohou", "wrong_liunian"]
        question_ids = []
        for label in labels:
            picked = 0
            for row in regression.get("rows") or []:
                if row.get("correct"):
                    continue
                tags = row.get("errorLabels") or []
                if label not in tags:
                    continue
                qid = str(row.get("questionId") or "")
                if not qid or qid in question_ids:
                    continue
                question_ids.append(qid)
                picked += 1
                if picked >= args.sample_size:
                    break
    limit = 0 if question_ids else args.limit
    report = asyncio.run(
        run_baseline(args.split, limit=limit, use_rag=args.rag, question_ids=question_ids)
    )
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
