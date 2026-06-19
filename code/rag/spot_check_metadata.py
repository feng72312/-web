"""Spot-check RAG chunk metadata for 01八字命理 collection."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from bazi_rag_engine import get_client, search
from config import DEFAULT_RAG_COLLECTION


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default="甲木寅月 调候 用神")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    get_client()
    rows = search(
        _Req(
            query=args.query,
            topK=args.top_k,
            category="01八字命理",
            collection=DEFAULT_RAG_COLLECTION,
            authorityTiers=["S"],
            judgeOnly=True,
        )
    )
    required = ("authorityTier", "evidenceRole", "libraryRole", "canJudge", "textRole")
    samples = []
    missing_fields = 0
    for row in rows:
        sample = {key: row.get(key) for key in required}
        sample["classic"] = row.get("classic")
        sample["evidenceBucket"] = row.get("evidenceBucket")
        sample["excerpt"] = str(row.get("excerpt") or "")[:120]
        sample["textRole"] = row.get("textRole")
        if any(sample.get(key) in (None, "") for key in required):
            missing_fields += 1
        samples.append(sample)

    result = {
        "query": args.query,
        "hitCount": len(rows),
        "missingRequiredMetadata": missing_fields,
        "samples": samples,
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    return 0 if rows and missing_fields == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
