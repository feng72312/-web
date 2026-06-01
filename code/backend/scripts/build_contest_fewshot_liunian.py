#!/usr/bin/env python
"""Build few-shot examples from train split, filtered to 流年事件 / year questions."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.benchmark.contest8_dataset import load_split, normalize_answer_letter
from app.benchmark.contest8_rag import infer_question_theme
def main() -> None:
    items = load_split("train")
    picked = []
    for q in items:
        if infer_question_theme(q.question) != "流年事件":
            continue
        letter = normalize_answer_letter(q.answer)
        idx = ord(letter.upper()) - ord("A") if letter else -1
        answer_text = q.options[idx] if 0 <= idx < len(q.options) else ""
        picked.append(
            {
                "question_id": q.question_id,
                "year": q.year,
                "question": q.question,
                "answer": letter,
                "answer_text": answer_text,
            }
        )
    picked = picked[:4]
    out = ROOT / "data" / "contest8_fewshot_liunian.json"
    payload = {
        "source": "contest8 train 流年/应期",
        "count": len(picked),
        "examples": picked,
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(picked)} examples to {out}")


if __name__ == "__main__":
    main()
