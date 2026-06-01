#!/usr/bin/env python
"""
Run Contest8 (2021-2025) benchmark for multiple divination methods.

Output: data/reports/contest8_{split}_{method}.json

Then generate markdown: python scripts/generate_contest_comparison_md.py
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.benchmark.contest8_dataset import split_summary
from app.benchmark.contest8_eval import EvalReport, run_eval, save_report

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

METHODS: dict[str, dict[str, Any]] = {
    "bazi_kg": {
        "label": "八字(知识图谱)",
        "fewshot": False,
        "case_rag": False,
        "knowledge": True,
        "fusion": False,
        "liuyao_only": False,
    },
    "bazi_fewshot": {
        "label": "八字(知识图谱+fewshot,无命例RAG)",
        "fewshot": True,
        "case_rag": False,
        "knowledge": True,
        "fusion": False,
        "liuyao_only": False,
    },
    "bazi_full": {
        "label": "八字(知识图谱+命例RAG+fewshot)",
        "fewshot": True,
        "case_rag": True,
        "knowledge": True,
        "fusion": False,
        "liuyao_only": False,
    },
    "fusion": {
        "label": "八字+六爻融合",
        "fewshot": True,
        "case_rag": True,
        "knowledge": True,
        "fusion": True,
        "liuyao_only": False,
    },
    "liuyao_only": {
        "label": "六爻(出生时间卦)",
        "fewshot": False,
        "case_rag": False,
        "knowledge": False,
        "fusion": False,
        "liuyao_only": True,
    },
}

# Older report filenames to reuse without re-running API
LEGACY_REPORTS: dict[tuple[str, str], str] = {
    ("bazi_full", "val"): "contest8_val_full.json",
    ("bazi_full", "test"): "contest8_test_full.json",
    ("fusion", "val"): "contest8_val_fusion.json",
}

REPORTS_DIR = ROOT / "data" / "reports"


def report_path(split: str, method: str) -> Path:
    return REPORTS_DIR / f"contest8_{split}_{method}.json"


def save_method_report(
    report: EvalReport,
    out_path: Path,
    *,
    method: str,
    method_label: str,
) -> None:
    payload = report.to_dict()
    payload["method"] = method
    payload["methodLabel"] = method_label
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def import_legacy(split: str, method: str) -> bool:
    key = (method, split)
    legacy_name = LEGACY_REPORTS.get(key)
    if not legacy_name:
        return False
    src = REPORTS_DIR / legacy_name
    dst = report_path(split, method)
    if not src.is_file():
        return False
    if dst.is_file():
        return True
    shutil.copy2(src, dst)
    data = json.loads(dst.read_text(encoding="utf-8"))
    data["method"] = method
    data["methodLabel"] = METHODS[method]["label"]
    dst.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    logging.info("imported legacy %s -> %s", legacy_name, dst.name)
    return True


async def run_method_split(
    method: str,
    split: str,
    *,
    model_id: str | None,
    limit: int | None,
    skip_existing: bool,
) -> Path:
    cfg = METHODS[method]
    out = report_path(split, method)
    if skip_existing and out.is_file():
        logging.info("skip existing %s", out.name)
        return out
    if skip_existing and import_legacy(split, method):
        return out

    report = await run_eval(
        split,  # type: ignore[arg-type]
        model_id=model_id,
        limit=limit,
        use_knowledge=cfg["knowledge"],
        use_case_rag=cfg["case_rag"],
        use_fewshot=cfg["fewshot"],
        use_fusion=cfg["fusion"],
        use_liuyao_only=cfg["liuyao_only"],
    )
    save_method_report(
        report,
        out,
        method=method,
        method_label=str(cfg["label"]),
    )
    logging.info(
        "[%s %s] %s accuracy=%.1f%% (%s/%s)",
        split,
        method,
        cfg["label"],
        report.accuracy * 100,
        report.correct,
        report.total,
    )
    return out


def regenerate_markdown() -> None:
    gen = ROOT / "scripts" / "generate_contest_comparison_md.py"
    if gen.is_file():
        import subprocess

        subprocess.run([sys.executable, str(gen)], check=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Contest8 multi-method benchmark")
    parser.add_argument(
        "--split",
        choices=("train", "val", "test", "all"),
        default="all",
    )
    parser.add_argument(
        "--methods",
        nargs="+",
        choices=list(METHODS.keys()) + ["all"],
        default=["all"],
    )
    parser.add_argument("--model", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()

    print("dataset:", split_summary())
    methods = list(METHODS.keys()) if "all" in args.methods else args.methods
    splits = ("train", "val", "test") if args.split == "all" else (args.split,)

    for method in methods:
        for split in splits:
            asyncio.run(
                run_method_split(
                    method,
                    split,
                    model_id=args.model,
                    limit=args.limit,
                    skip_existing=args.skip_existing,
                )
            )

    regenerate_markdown()


if __name__ == "__main__":
    main()
