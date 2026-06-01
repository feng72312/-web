import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for name in ("val", "test"):
    r = json.loads((ROOT / "data" / "reports" / f"contest8_{name}_full.json").read_text(encoding="utf-8"))
    by_person = defaultdict(lambda: [0, 0])
    for row in r["results"]:
        pid = row["question_id"].rsplit("-", 1)[0]
        by_person[pid][1] += 1
        if row["correct"]:
            by_person[pid][0] += 1
    print(f"=== {name} {r['correct']}/{r['total']} {r['accuracy']:.1%}")
    for pid in sorted(by_person):
        c, t = by_person[pid]
        print(f"  {pid}: {c}/{t}")
