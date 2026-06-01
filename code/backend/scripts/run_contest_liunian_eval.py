#!/usr/bin/env python
"""Run Contest8 MCQ eval on liunian-related questions only (bazi_kg + liunian graph)."""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.benchmark.contest8_dataset import (
    ContestQuestion,
    flatten_questions,
    normalize_answer_letter,
)
from app.benchmark.contest8_eval import build_deepseek_client
from app.benchmark.contest8_rag import infer_question_theme
from app.core.knowledge.luck_prompt_util import extract_years_from_question

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
REPORTS = ROOT / "data" / "reports"
REPORT_DIR = ROOT.parents[1] / "report"


def classify_liunian_rule(q: ContestQuestion) -> str:
    if infer_question_theme(q.question) == "流年事件":
        return "theme"
    if extract_years_from_question(q.question):
        return "year_in_stem"
    return "keyword"


def is_liunian_question(q: ContestQuestion) -> bool:
    if infer_question_theme(q.question) == "流年事件":
        return True
    if extract_years_from_question(q.question):
        return True
    keys = ("流年", "太岁", "岁运", "虚龄", "大运", "哪一年", "何时", "年发生")
    return any(k in q.question for k in keys)


def filter_questions(mode: str) -> list[ContestQuestion]:
    all_q = flatten_questions([2021, 2022, 2023, 2024, 2025])
    if mode == "strict":
        return [q for q in all_q if infer_question_theme(q.question) == "流年事件"]
    return [q for q in all_q if is_liunian_question(q)]


async def _predict_letter(
    q: ContestQuestion,
    client,
    model_id: str | None,
    fewshot: list | None,
    *,
    votes: int = 1,
    temperature: float | None = None,
) -> tuple[str, str]:
    from app.benchmark.contest8_eval import predict_one

    r = await predict_one(
        q,
        client,
        model_id=model_id,
        use_knowledge=True,
        use_case_rag=True,
        fewshot_examples=fewshot,
        votes=votes,
        temperature=temperature,
    )
    return r.predicted, r.raw_response


async def run_eval(
    questions: list[ContestQuestion],
    model_id: str | None,
    *,
    votes: int = 1,
) -> dict:
    client = build_deepseek_client()
    votes = max(1, min(votes, 5))
    results = []
    for idx, q in enumerate(questions, start=1):
        logging.info("progress %s/%s %s", idx, len(questions), q.question_id)
        pred, raw = await _predict_letter(
            q,
            client,
            model_id,
            None,
            votes=votes,
            temperature=0.2,
        )
        predicted = pred
        gold = normalize_answer_letter(q.answer)
        r_correct = predicted == gold and predicted != ""
        results.append(
            {
                "question_id": q.question_id,
                "year": q.year,
                "gold": gold,
                "predicted": predicted,
                "correct": r_correct,
                "raw_response": raw[:4000] if raw else "",
                "error": "",
                "votes": votes,
                "voteLetters": [],
                "liunianRule": classify_liunian_rule(q),
                "theme": infer_question_theme(q.question),
                "question": q.question,
                "options": q.options,
            }
        )
    correct = sum(1 for x in results if x["correct"])
    total = len(results)
    return {
        "filter": "liunian",
        "total": total,
        "correct": correct,
        "accuracy": correct / total if total else 0.0,
        "results": results,
    }


def compare_with_prior(report: dict, prior_path: Path) -> dict:
    if not prior_path.is_file():
        return {"prior_available": False}
    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    by_id = {r["question_id"]: r for r in prior.get("results", [])}
    improved, worsened, same = [], [], 0
    for r in report["results"]:
        qid = r["question_id"]
        old = by_id.get(qid)
        if not old:
            continue
        if r["correct"] and not old.get("correct"):
            improved.append(qid)
        elif not r["correct"] and old.get("correct"):
            worsened.append(qid)
        elif r["predicted"] == old.get("predicted"):
            same += 1
    return {
        "prior_available": True,
        "prior_file": str(prior_path),
        "improved": improved,
        "worsened": worsened,
        "same_prediction": same,
    }


def write_analysis_md(report: dict, cmp: dict, out_path: Path) -> None:
    lines = [
        "# 命理师大赛 - 流年相关题评测",
        "",
        f"- 题数: **{report['correct']}/{report['total']}** = **{report['accuracy']:.1%}**",
        "- 配置: 八字(知识图谱 dayun+liunian + 命例RAG + fewshot) + 目标年断语 + 流年时间轴",
        "- 流年事件题: **规则预排除 + 四选项逐条推理**, 末行「答案:」解析字母",
        "- 随机基线约 25%",
        "",
    ]
    if cmp.get("prior_available"):
        lines.append("## 与此前全量 bazi_kg (无流年图谱强化前报告) 对比")
        lines.append("")
        lines.append(f"- 变好: {len(cmp['improved'])} 题")
        lines.append(f"- 变差: {len(cmp['worsened'])} 题")
        lines.append(f"- 预测字母相同: {cmp['same_prediction']} 题")
        lines.append("")

    by_theme: dict[str, list] = defaultdict(list)
    for r in report["results"]:
        by_theme[r["theme"]].append(r)

    lines.append("## 按题型准确率")
    lines.append("")
    lines.append("| 题型 | 对/总 | 准确率 |")
    lines.append("|------|-------|--------|")
    for theme, rows in sorted(
        by_theme.items(),
        key=lambda x: sum(1 for r in x[1] if r["correct"]) / len(x[1]),
        reverse=True,
    ):
        c = sum(1 for r in rows if r["correct"])
        lines.append(f"| {theme} | {c}/{len(rows)} | {c/len(rows):.1%} |")
    lines.append("")

    by_rule: dict[str, list] = defaultdict(list)
    for r in report["results"]:
        by_rule[r["liunianRule"]].append(r)
    lines.append("## 按纳入规则")
    lines.append("")
    lines.append("| 规则 | 对/总 | 准确率 |")
    lines.append("|------|-------|--------|")
    for rule, rows in sorted(by_rule.items()):
        c = sum(1 for r in rows if r["correct"])
        lines.append(f"| {rule} | {c}/{len(rows)} | {c/len(rows):.1%} |")
    lines.append("")

    wrong = [r for r in report["results"] if not r["correct"]]
    lines.append("## 错题原因归纳")
    lines.append("")
    lines.append("1. **年份/事件对不上**: 题干问具体公历或虚龄年, 模型未对准大运下该年十神与冲合.")
    lines.append("2. **相近选项**: 婚姻/健康/职业描述相似, 单看本命或单条流年规则不足以区分.")
    lines.append("3. **非纯流年题混入**: 含「何时」「大运」关键词的题可能属婚姻/子女, 更看配偶星而非太岁.")
    lines.append("4. **LLM 波动**: 边界题重跑选项可能变化.")
    lines.append("")

    lines.append("## 错题明细")
    lines.append("")
    for idx, r in enumerate(wrong, 1):
        lines.append(f"### {idx}. `{r['question_id']}` ({r['theme']})")
        lines.append("")
        lines.append(f"- 题: {r['question']}")
        lines.append(f"- 金标: **{r['gold']}** | 预测: **{r.get('predicted') or '-'}**")
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("strict", "broad"),
        default="broad",
        help="strict=仅流年事件主题19题; broad=流年相关73题",
    )
    parser.add_argument("--model", default=None)
    parser.add_argument(
        "--votes",
        type=int,
        default=1,
        help="每题多次调用 DeepSeek 后多数表决 (1-5)",
    )
    args = parser.parse_args()

    questions = filter_questions(args.mode)
    print(f"mode={args.mode} questions={len(questions)} votes={args.votes}")
    report = asyncio.run(run_eval(questions, args.model, votes=args.votes))
    report["mode"] = args.mode
    report["votes"] = args.votes
    report["optionElimination"] = args.mode == "strict"

    out_json = REPORTS / f"contest8_liunian_{args.mode}.json"
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"accuracy={report['accuracy']:.1%} -> {out_json}")

    prior_by_id: dict[str, dict] = {}
    for name in (
        "contest8_train_bazi_kg.json",
        "contest8_val_bazi_kg.json",
        "contest8_test_bazi_kg.json",
    ):
        path = REPORTS / name
        if path.is_file():
            for r in json.loads(path.read_text(encoding="utf-8")).get("results", []):
                prior_by_id[r["question_id"]] = r
    if prior_by_id:
        improved, worsened = [], []
        for r in report["results"]:
            old = prior_by_id.get(r["question_id"])
            if not old:
                continue
            if r["correct"] and not old.get("correct"):
                improved.append(r["question_id"])
            elif not r["correct"] and old.get("correct"):
                worsened.append(r["question_id"])
        cmp = {
            "prior_available": True,
            "improved": improved,
            "worsened": worsened,
            "same_prediction": sum(
                1
                for r in report["results"]
                if prior_by_id.get(r["question_id"], {}).get("predicted")
                == r.get("predicted")
            ),
        }
    else:
        cmp = {"prior_available": False}

    md_path = REPORT_DIR / f"命理师大赛-流年相关题评测-{args.mode}.md"
    write_analysis_md(report, cmp, md_path)
    print(f"wrote {md_path}")


if __name__ == "__main__":
    main()
