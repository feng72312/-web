"""Analyze contest regression rows by error label and suggest graph gaps."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime
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
    / "contest_gap_analysis.json"
)

FOCUS_LABELS = (
    "overconfident_claim",
    "wrong_tiaohou",
    "wrong_liunian",
    "wrong_yongshen",
    "case_overfit",
)

LABEL_TO_TOPIC = {
    "wrong_tiaohou": "tiaohou",
    "wrong_liunian": "liunian",
    "wrong_yongshen": "qishi",
    "wrong_geju": "geju",
    "wrong_dayun": "suiyun",
    "wrong_strength": "qishi",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _row_detail(row: dict, contest_row: dict | None) -> dict:
    meta = row.get("meta") or {}
    coverage = row.get("coverage") or {}
    judgement = (contest_row or {}).get("judgement") or row.get("judgement") or {}
    arb = judgement.get("arbitration") or {}
    tiered = judgement.get("tieredEvidence") or {}
    cov = judgement.get("coverage") or coverage
    active_dayun = ""
    target_year = meta.get("targetYear")
    chart = (contest_row or {}).get("chart") or row.get("chart") or {}
    if chart:
        active_dayun = str(chart.get("activeDayunGanzhi") or chart.get("activeDayun") or "")
        if target_year is None:
            target_year = chart.get("targetYear")
    return {
        "questionId": row.get("questionId"),
        "correct": row.get("correct"),
        "errorLabels": row.get("errorLabels") or [],
        "mustCheckRules": meta.get("mustCheckRules") or [],
        "missingRules": coverage.get("missingRules") or cov.get("missingTags") or [],
        "targetYear": target_year,
        "activeDayun": active_dayun,
        "primaryEvidenceCount": len(tiered.get("primaryEvidence") or []),
        "caseReferenceCount": len(tiered.get("caseReference") or []),
        "confidenceBand": arb.get("confidenceBand"),
        "conflicts": arb.get("conflicts") or [],
    }


def _suggest_tasks(rows_by_label: dict[str, list[dict]]) -> list[dict]:
    tasks: list[dict] = []
    for label, details in rows_by_label.items():
        topic = LABEL_TO_TOPIC.get(label)
        if not topic:
            continue
        qids = [str(d.get("questionId") or "") for d in details if d.get("questionId")]
        if not qids:
            continue
        source_map = {
            "tiaohou": "穷通宝鉴-清-余春台.txt",
            "liunian": "三命通会-明-万民英.txt",
            "qishi": "滴天髓阐微-清-任铁樵.txt",
            "geju": "子平真诠-清-沈孝瞻.txt",
            "suiyun": "三命通会-明-万民英.txt",
        }
        tasks.append(
            {
                "topic": topic,
                "sourceFile": source_map.get(topic, ""),
                "reason": f"contest regression label={label}",
                "questionIds": qids[:12],
                "count": len(qids),
            }
        )
    return tasks


def analyze(regression: dict, contest: dict | None) -> dict:
    rows = list(regression.get("rows") or [])
    contest_map: dict[str, dict] = {}
    if contest:
        for row in contest.get("rows") or []:
            qid = str(row.get("questionId") or "")
            if qid:
                contest_map[qid] = row

    label_counter: Counter[str] = Counter()
    rows_by_label: dict[str, list[dict]] = defaultdict(list)
    details: list[dict] = []

    for row in rows:
        labels = list(row.get("errorLabels") or [])
        if not row.get("correct", True):
            for label in labels:
                label_counter[label] += 1
        detail = _row_detail(row, contest_map.get(str(row.get("questionId") or "")))
        details.append(detail)
        for label in labels:
            if label in FOCUS_LABELS:
                rows_by_label[label].append(detail)

    focus_total = sum(
        label_counter.get(label, 0) for label in FOCUS_LABELS[:3]
    )

    return {
        "builtAt": datetime.now().isoformat(timespec="seconds"),
        "sourceRegression": regression.get("split"),
        "total": regression.get("total"),
        "accuracy": regression.get("accuracy"),
        "errorLabelDistribution": dict(regression.get("errorLabelDistribution") or label_counter),
        "focusLabelTotals": {label: label_counter.get(label, 0) for label in FOCUS_LABELS},
        "focusThreeLabelsTotal": focus_total,
        "byLabel": {
            label: {
                "count": len(items),
                "questionIds": [d["questionId"] for d in items],
                "rows": items,
            }
            for label, items in sorted(rows_by_label.items())
        },
        "allRows": details,
        "suggestedExtractTasks": _suggest_tasks(rows_by_label),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--regression", type=Path, default=DEFAULT_REGRESSION)
    parser.add_argument("--contest", type=Path, default=None, help="optional fresh contest output")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    regression = _load_json(args.regression)
    contest = _load_json(args.contest) if args.contest and args.contest.is_file() else None
    payload = analyze(regression, contest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {args.output}")
    print(f"focusThreeLabelsTotal={payload['focusThreeLabelsTotal']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
