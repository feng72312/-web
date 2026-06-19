"""Run Contest8 MCQ on wrong_tiaohou / wrong_liunian samples from regression report."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGRESSION = (
    BACKEND_ROOT.parents[1]
    / "report"
    / "八字判盘最强方案"
    / "contest8_val_geju_special_regression.json"
)
DEFAULT_OUTPUT = (
    BACKEND_ROOT.parents[1]
    / "report"
    / "八字判盘最强方案"
    / "继续补全"
    / "contest8_wrong_tiaohou_liunian_sample.json"
)

TARGET_LABELS_DEFAULT = ("wrong_tiaohou", "wrong_liunian")


def _parse_labels(raw: str) -> tuple[str, ...]:
    if not raw.strip():
        return TARGET_LABELS_DEFAULT
    return tuple(item.strip() for item in raw.split(",") if item.strip())


def _load_rows(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("rows") or [])


def _pick_ids(rows: list[dict], *, limit: int, target_labels: tuple[str, ...]) -> list[str]:
    picked: list[str] = []
    seen: set[str] = set()
    for row in rows:
        labels = set(row.get("errorLabels") or [])
        if not labels.intersection(target_labels):
            continue
        qid = str(row.get("questionId") or "").strip()
        if not qid or qid in seen:
            continue
        seen.add(qid)
        picked.append(qid)
        if len(picked) >= limit:
            break
    return picked


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--regression", type=Path, default=DEFAULT_REGRESSION)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--labels", default="", help="comma-separated error labels")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    target_labels = _parse_labels(args.labels)
    rows = _load_rows(args.regression)
    ids = _pick_ids(rows, limit=args.limit, target_labels=target_labels)
    if not ids:
        print(f"no samples found for labels={target_labels}", file=sys.stderr)
        return 1

    print(f"selected {len(ids)} ids:", ", ".join(ids), flush=True)
    if args.dry_run:
        payload = {
            "source": str(args.regression),
            "labels": list(target_labels),
            "ids": ids,
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"dry-run wrote {args.out}")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(BACKEND_ROOT / "scripts" / "run_contest_benchmark.py"),
        "--split",
        "val",
        "--ids",
        ",".join(ids),
        "--out",
        str(args.out),
    ]
    print(">", " ".join(cmd), flush=True)
    proc = subprocess.run(cmd, cwd=str(BACKEND_ROOT))
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
