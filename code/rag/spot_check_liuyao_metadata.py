"""Spot-check liuyao RAG chunk metadata and S-tier priority over B-tier."""

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


LIUYAO_CATEGORY = "02六爻卜筮"
LIUYAO_COLLECTION = "kb_02_liuyao"


def _run_query(query: str, top_k: int, authority_tiers: list[str] | None) -> list[dict]:
    get_client()
    return search(
        _Req(
            query=query,
            topK=top_k,
            category=LIUYAO_CATEGORY,
            collection=LIUYAO_COLLECTION,
            authorityTiers=authority_tiers,
        )
    )


def _summarize_rows(rows: list[dict]) -> list[dict]:
    required = (
        "authorityTier",
        "evidenceRole",
        "libraryRole",
        "canJudge",
        "textRole",
        "topicScope",
        "caseOnly",
    )
    samples = []
    missing_fields = 0
    for row in rows:
        sample = {key: row.get(key) for key in required}
        sample["classic"] = row.get("classic")
        sample["evidenceBucket"] = row.get("evidenceBucket")
        sample["excerpt"] = str(row.get("excerpt") or "")[:120]
        if any(sample.get(key) in (None, "") for key in required if key != "caseOnly"):
            missing_fields += 1
        samples.append(sample)
    return samples, missing_fields


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default="用神 妻财 旺衰 月建 日辰")
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
    s_before_b = True
    if s_in_top and b_in_top:
        s_before_b = all_rows.index(s_in_top[0]) < all_rows.index(b_in_top[0])

    result = {
        "category": LIUYAO_CATEGORY,
        "collection": LIUYAO_COLLECTION,
        "query": args.query,
        "hitCount": len(all_rows),
        "sHitCount": len(s_rows),
        "missingRequiredMetadata": all_missing,
        "sTierFirstInOpenSearch": first_is_s,
        "sTierBeforeBTier": s_before_b,
        "openSamples": all_samples,
        "sOnlySamples": s_samples,
        "checks": {
            "hasHits": len(all_rows) > 0,
            "metadataComplete": all_missing == 0,
            "sTierPreferred": first_is_s or (not b_in_top),
        },
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)

    output = args.output
    if output:
        out_path = Path(output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")

    checks = result["checks"]
    ok = checks["hasHits"] and checks["metadataComplete"] and checks["sTierPreferred"]
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
