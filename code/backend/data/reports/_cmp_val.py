import json
from pathlib import Path
from collections import defaultdict
import sys
sys.path.insert(0,".")
from app.benchmark.contest8_dataset import flatten_questions
from app.benchmark.contest8_rag import infer_question_theme
qmap={q.question_id:q for q in flatten_questions([2024])}
old=json.loads(Path("data/reports/contest8_val_bazi_liunian.json").read_text(encoding="utf-8"))
new=json.loads(Path("data/reports/contest8_val_bazi_liunian_static_narrow.json").read_text(encoding="utf-8"))
print("val old", old["correct"], old["total"])
print("val new", new["correct"], new["total"])
imp=[]; reg=[]
for n in new["results"]:
    o=next(x for x in old["results"] if x["question_id"]==n["question_id"])
    if n["correct"] and not o["correct"]: imp.append(n["question_id"])
    elif not n["correct"] and o["correct"]: reg.append(n["question_id"])
print("improved", imp)
print("regressed", reg)
