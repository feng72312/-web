#!/usr/bin/env python
"""Build few-shot examples from train split (2021-2023) for contest MCQ prompts."""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.benchmark.contest8_dataset import load_split, normalize_answer_letter


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=8, help="number of few-shot examples")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "data" / "contest8_fewshot.json",
    )
    args = parser.parse_args()
    items = load_split("train")
    rng = random.Random(args.seed)
    picked = rng.sample(items, min(args.count, len(items)))
    examples = []
    for q in picked:
        letter = normalize_answer_letter(q.answer)
        idx = ord(letter.upper()) - ord("A") if letter else -1
        answer_text = q.options[idx] if 0 <= idx < len(q.options) else ""
        examples.append(
            {
                "question_id": q.question_id,
                "year": q.year,
                "question": q.question,
                "answer": letter,
                "answer_text": answer_text,
            }
        )
    payload = {
        "source": "contest8 train 2021-2023",
        "count": len(examples),
        "examples": examples,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(examples)} examples to {args.out}")


if __name__ == "__main__":
    main()
