"""Local smoke: build interpret segments from judgement + sample summary."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.benchmark.contest8_chart import build_chart_for_question
from app.benchmark.contest8_dataset import load_split
from app.core.interpret.segments import build_interpret_segments
from app.core.judgement.chain import BaziJudgementChain
from app.core.judgement.evidence import extract_rule_id_refs
from app.core.paipan.engine import PaipanEngine
from app.core.paipan.rules import PaipanRules
from app.config import settings
from app.core.analysis.registry import build_default_registry


async def run_smoke(*, use_rag: bool, question_id: str) -> dict:
    item = next(q for q in load_split("val") if q.question_id == question_id)
    engine = PaipanEngine(
        rules=PaipanRules(
            sect=settings.paipan_sect,
            early_zishi_mode=settings.early_zishi_mode,
        )
    )
    registry = build_default_registry()
    chart = build_chart_for_question(
        item,
        engine=engine,
        registry=registry,
        include_luck_timeline=False,
    )
    report = await BaziJudgementChain(use_rag=use_rag).run(chart, question=item.question)
    judgement = report.to_dict()
    refs = extract_rule_id_refs(judgement)
    sample_rule = refs[0]["ruleId"] if refs else "geju:month:正官"
    summary = (
        f"样例解读段一, 引用判盘链规则. [ruleId:{sample_rule}]\n\n"
        "(推断) 样例解读段二, 无规则锚点."
    )
    bundle = build_interpret_segments(
        summary,
        judgement,
        rule_id_refs=refs,
        confidence_band=(judgement.get("arbitration") or {}).get("confidenceBand"),
    )
    return {
        "questionId": question_id,
        "useRag": use_rag,
        "ruleIdRefCount": len(refs),
        "segmentStats": bundle["stats"],
        "segments": bundle["segments"],
        "confidenceBand": bundle.get("confidenceBand"),
        "confidenceNote": bundle.get("confidenceNote"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rag", action="store_true")
    parser.add_argument("--question-id", default="guangdong_female_19800824_P001-Q1")
    parser.add_argument(
        "--output",
        type=Path,
        default=BACKEND_ROOT.parents[1]
        / "report"
        / "八字判盘最强方案"
        / "继续补全"
        / "interpret_segments_smoke.json",
    )
    args = parser.parse_args()
    payload = asyncio.run(run_smoke(use_rag=args.rag, question_id=args.question_id))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    ok = payload.get("segmentStats", {}).get("total", 0) >= 2
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
