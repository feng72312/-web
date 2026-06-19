"""Spot-check ziwei RAG chunk metadata and S-tier priority over B-tier."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from bazi_rag_engine import get_client, search


class _Req:
    def __init__(self, **kwargs):
        self.categories = None
        self.category = None
        self.collection = None
        self.authorityTiers = None
        self.evidenceRoles = None
        self.libraryRoles = None
        self.classicWhitelist = None
        self.topicScope = None
        self.excludeBenchmark = True
        self.judgeOnly = False
        self.partitioned = False
        self.__dict__.update(kwargs)


ZIWEI_CATEGORY = "11紫微斗数"
ZIWEI_COLLECTION = "kb_11_ziwei"


def _run_query(query: str, top_k: int, authority_tiers: list[str] | None) -> list[dict]:
    get_client()
    return search(
        _Req(
            query=query,
            topK=top_k,
            category=ZIWEI_CATEGORY,
            collection=ZIWEI_COLLECTION,
            authorityTiers=authority_tiers,
        )
    )


def _summarize_rows(rows: list[dict]) -> tuple[list[dict], int]:
    required = (
        "authorityTier",
        "evidenceRole",
        "libraryRole",
        "canJudge",
        "textRole",
        "topicScope",
        "school",
        "palaceScope",
        "starScope",
        "mutagenScope",
        "limitScope",
    )
    samples = []
    missing_fields = 0
    for row in rows:
        sample = {key: row.get(key) for key in required}
        sample["classic"] = row.get("classic")
        sample["excerpt"] = str(row.get("excerpt") or "")[:120]
        if any(sample.get(key) in (None, "") for key in required if key not in {"palaceScope", "starScope", "mutagenScope", "limitScope"}):
            missing_fields += 1
        samples.append(sample)
    return samples, missing_fields


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default="紫微 天府 庙旺 三方四正 四化")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    all_rows = _run_query(args.query, args.top_k, None)
    s_rows = _run_query(args.query, args.top_k, ["S"])

    all_samples, all_missing = _summarize_rows(all_rows)
    s_samples, s_missing = _summarize_rows(s_rows)

    s_in_top = [row for row in all_rows if row.get("authorityTier") == "S"]
    b_in_top = [row for row in all_rows if row.get("authorityTier") == "B"]
    first_is_s = bool(all_rows) and all_rows[0].get("authorityTier") == "S"

    report = {
        "query": args.query,
        "topK": args.top_k,
        "allCount": len(all_rows),
        "sFilterCount": len(s_rows),
        "sInOpenSearch": len(s_in_top),
        "bInOpenSearch": len(b_in_top),
        "sTierFirstInOpenSearch": first_is_s,
        "missingMetadataFields": all_missing,
        "samplesAll": all_samples,
        "samplesSOnly": s_samples,
    }

    out_path = args.output
    if not out_path:
        out_path = str(
            Path(__file__).resolve().parents[2]
            / "report"
            / "紫薇斗数最强方案"
            / "rag_spot_check_ziwei.json"
        )
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if all_rows and first_is_s else 1


if __name__ == "__main__":
    sys.exit(main())
