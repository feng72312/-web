from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.core.personas.catalog_import import (
    AWESOME_COMMIT,
    audit_all,
    build_catalog,
    diff_catalog,
    parse_awesome_readme,
    write_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Import a pinned awesome-nuwa catalog without executing upstream code.")
    parser.add_argument("readme", type=Path)
    parser.add_argument("--cache", type=Path, default=Path(".cache/persona-upstreams"))
    parser.add_argument("--output", type=Path, default=Path("app/core/personas/catalog.json"))
    parser.add_argument("--audit-output", type=Path, default=Path("app/core/personas/catalog-audit.json"))
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--skip-repository-audit", action="store_true")
    args = parser.parse_args()

    parsed = parse_awesome_readme(args.readme.read_text(encoding="utf-8"))
    previous = None
    if args.output.exists():
        previous = json.loads(args.output.read_text(encoding="utf-8"))
    candidates = parsed["candidates"]
    audits = {} if args.skip_repository_audit else audit_all(candidates, args.cache, args.workers)
    catalog = build_catalog(parsed, audits)
    audit_report = {
        "awesomeCommit": AWESOME_COMMIT,
        "declaredTotal": parsed["declared_total"],
        "actualUniqueTotal": catalog["actualUniqueTotal"],
        "declaredCounts": parsed["declared_counts"],
        "actualCounts": parsed["actual_counts"],
        "countDrift": parsed["count_drift"],
        "duplicateRepositories": parsed["duplicate_repositories"],
        "changes": diff_catalog(previous, catalog),
        "repositoryAudits": audits,
    }
    write_json(args.output, catalog)
    write_json(args.audit_output, audit_report)
    print(json.dumps({
        "output": str(args.output), "commit": AWESOME_COMMIT,
        "total": catalog["actualUniqueTotal"],
        "ready": sum(item["availability"] == "ready" for item in catalog["personas"]),
        "reviewRequired": sum(item["availability"] != "ready" for item in catalog["personas"]),
        "countDrift": parsed["count_drift"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
