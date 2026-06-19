"""Validate caseReference count and excerpt readability on P0 val sample."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.benchmark.contest8_benchmark_meta import enrich_question  # noqa: E402
from app.benchmark.contest8_chart import build_chart_for_question  # noqa: E402
from app.benchmark.contest8_dataset import load_split  # noqa: E402
from app.core.judgement.chain import BaziJudgementChain  # noqa: E402
from app.core.paipan.engine import PaipanEngine  # noqa: E402
from app.core.paipan.rules import PaipanRules  # noqa: E402
from app.config import settings  # noqa: E402
from app.core.analysis.registry import build_default_registry  # noqa: E402

P0_IDS = [
    "guangdong_female_19800824_P001-Q1",
    "guangdong_female_19800824_P001-Q2",
    "guangdong_female_19800824_P001-Q3",
    "guangdong_female_19800824_P001-Q4",
    "guangdong_female_19800824_P001-Q5",
    "male_19611230_P003-Q13",
    "female_19831028_P004-Q17",
    "female_19831028_P004-Q19",
]


def _excerpt_ok(text: str) -> bool:
    body = str(text or "").strip()
    if len(body) < 20:
        return False
    if "PK\x03\x04" in body:
        return False
    return ("乾造" in body or "坤造" in body or "命例" in body)


async def run_baseline(*, use_rag: bool, question_ids: list[str]) -> dict:
    engine = PaipanEngine(
        rules=PaipanRules(
            sect=settings.paipan_sect,
            early_zishi_mode=settings.early_zishi_mode,
        )
    )
    registry = build_default_registry()
    chain = BaziJudgementChain(use_rag=use_rag)
    rows = []
    for qid in question_ids:
        item = next(q for q in load_split("val") if q.question_id == qid)
        meta = enrich_question(item)
        chart = build_chart_for_question(
            item,
            engine=engine,
            registry=registry,
            include_luck_timeline=False,
        )
        report = await chain.run(chart, question=item.question, benchmark_meta=meta)
        cases = report.tieredEvidence.caseReference or []
        readable = sum(1 for row in cases if _excerpt_ok(str(row.get("excerpt") or "")))
        rows.append(
            {
                "questionId": qid,
                "questionTheme": meta.get("questionTheme"),
                "caseReferenceCount": len(cases),
                "readableExcerptCount": readable,
                "observedEvents": [row.get("observedEvent") for row in cases],
                "excerptPreview": [str(row.get("excerpt") or "")[:100] for row in cases],
            }
        )
    counts = [row["caseReferenceCount"] for row in rows]
    return {
        "useRag": use_rag,
        "total": len(rows),
        "caseReferenceMin": min(counts) if counts else 0,
        "caseReferenceMax": max(counts) if counts else 0,
        "readableExcerptMin": min(row["readableExcerptCount"] for row in rows) if rows else 0,
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rag", action="store_true")
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    payload = asyncio.run(run_baseline(use_rag=args.rag, question_ids=P0_IDS))
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    ok = (
        payload.get("caseReferenceMin", 0) >= 3
        and payload.get("readableExcerptMin", 0) >= 1
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
