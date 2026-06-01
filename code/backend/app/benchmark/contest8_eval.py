from __future__ import annotations

import asyncio
import json
import logging
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.benchmark.contest8_chart import build_chart_for_question
from app.benchmark.contest8_rag import build_case_rag_query
from app.benchmark.contest8_dataset import (
    ContestQuestion,
    SplitName,
    load_split,
    normalize_answer_letter,
    parse_contest_answer_letter,
)
from app.benchmark.contest8_fewshot import select_fewshot_by_theme
from app.benchmark.contest8_rag import infer_question_theme
from app.core.knowledge.mcq_reasoning_mode import should_structured_mcq_reasoning
from app.config import settings
from app.core.agent.deepseek import DeepSeekClient, DeepSeekError
from app.core.agent.prompts_contest import (
    build_contest_liuyao_mcq_parts,
    build_contest_mcq_parts,
    load_fewshot_examples,
)
from app.core.agent.prompts_liuyao import build_yong_shen_prompt
from app.core.fusion.inputs import paipan_to_liuyao_input
from app.core.fusion.merge import merge_mcq_letters
from app.core.liuyao.engine import LiuyaoEngine
from app.core.liuyao.interpret_service import LiuyaoInterpretService
from app.core.liuyao.yong_shen_rules import fallback_yong_shen, parse_yong_shen_json
from app.benchmark.contest8_chart import question_to_paipan_request
from app.core.knowledge.factory import get_knowledge_service
from app.core.knowledge.rag_fallback import fetch_on_demand_rag
from app.core.knowledge.models import CompressedContext
from app.core.rag.factory import build_rag_provider
from app.core.rag.base import normalize_rag_excerpts

logger = logging.getLogger(__name__)


@dataclass
class QuestionResult:
    question_id: str
    year: int
    gold: str
    predicted: str
    correct: bool
    raw_response: str
    error: str = ""
    bazi_pred: str = ""
    liuyao_pred: str = ""
    question_scope: str = ""
    preferred_channel: str = ""
    parse_source: str = ""
    vote_letters: list[str] = field(default_factory=list)


@dataclass
class EvalReport:
    split: str
    total: int
    correct: int
    accuracy: float
    results: list[QuestionResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "split": self.split,
            "total": self.total,
            "correct": self.correct,
            "accuracy": self.accuracy,
            "results": [
                {
                    "question_id": r.question_id,
                    "year": r.year,
                    "gold": r.gold,
                    "predicted": r.predicted,
                    "correct": r.correct,
                    "raw_response": r.raw_response[:500],
                    "error": r.error,
                    "baziPred": r.bazi_pred,
                    "liuyaoPred": r.liuyao_pred,
                    "questionScope": r.question_scope,
                    "preferredChannel": r.preferred_channel,
                    "parseSource": r.parse_source,
                    "voteLetters": r.vote_letters,
                }
                for r in self.results
            ],
        }


def _case_rag_top_k(question: str) -> int:
    theme = infer_question_theme(question)
    return 3 if theme != "综合" else 5


async def _fetch_case_rag_excerpts(
    chart: dict[str, Any],
    question: str,
    *,
    top_k: int | None = None,
) -> list[dict[str, str]]:
    if settings.rag_provider != "http" or not settings.rag_http_url:
        return []
    rag = build_rag_provider()
    query = build_case_rag_query(chart, question)
    k = top_k if top_k is not None else _case_rag_top_k(question)
    try:
        rows = await rag.search(
            query,
            top_k=k,
            category=settings.rag_default_category,
        )
        return normalize_rag_excerpts(rows)
    except Exception as err:
        logger.warning("case rag search failed: %s", err)
        return []


async def _resolve_knowledge_context_async(
    chart: dict[str, Any],
    question: str = "",
    *,
    use_case_rag: bool = True,
) -> tuple[CompressedContext | None, list[dict[str, str]]]:
    knowledge = get_knowledge_service()
    compressed = None
    excerpts: list[dict[str, str]] = []

    if knowledge.enabled:
        compressed = knowledge.resolve_for_chart(chart, question=question)
        if (
            settings.knowledge_rag_fallback
            and settings.rag_provider == "http"
            and compressed.missingTopics
        ):
            rag = build_rag_provider()
            try:
                excerpts = normalize_rag_excerpts(
                    await fetch_on_demand_rag(
                        rag,
                        chart,
                        compressed.missingTopics,
                        category=settings.rag_default_category,
                    )
                )
            except Exception as err:
                logger.warning("rag fallback in eval: %s", err)

    if use_case_rag and question:
        case_rows = await _fetch_case_rag_excerpts(chart, question)
        seen = {e.get("excerpt", "")[:80] for e in excerpts}
        for row in case_rows:
            key = row.get("excerpt", "")[:80]
            if key and key not in seen:
                excerpts.append(row)
                seen.add(key)

    if not knowledge.enabled:
        compressed = None
    return compressed, excerpts


def build_deepseek_client() -> DeepSeekClient:
    client = DeepSeekClient(
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
    )
    if not client.enabled:
        raise RuntimeError("set BAZI_DEEPSEEK_API_KEY in code/backend/.env")
    return client


_liuyao_engine = LiuyaoEngine()
_liuyao_interpret = LiuyaoInterpretService()


async def _mcq_letter(
    client: DeepSeekClient,
    system: str,
    user: str,
    model_id: str | None,
    *,
    temperature: float | None = None,
    structured: bool = False,
) -> tuple[str, str, str]:
    raw = await client.chat_once(
        model_id or "deepseek-chat",
        user,
        system=system,
        temperature=temperature,
    )
    if structured:
        letter, source = parse_contest_answer_letter(
            raw,
            prefer_final_line=True,
            reconcile_reasoning=True,
        )
        return letter, raw, source
    letter = normalize_answer_letter(raw)
    return letter, raw, ("fallback" if letter else "empty")


async def _infer_yong_shen_deepseek(
    client: DeepSeekClient,
    chart: dict[str, Any],
    question: str,
    model_id: str | None,
) -> dict[str, Any]:
    prompt = build_yong_shen_prompt(chart, question)
    try:
        raw = await client.chat_once(model_id or "deepseek-chat", prompt)
        payload = parse_yong_shen_json(raw)
        if payload and str(payload.get("yongShen", "")).strip():
            ys = str(payload["yongShen"]).strip()
            pos = int(payload.get("position") or 0)
            if pos < 1 or pos > 6:
                pos = fallback_yong_shen(chart, question).position
            return {
                "yongShen": ys,
                "position": pos,
                "reason": str(payload.get("reason") or "AI"),
                "source": "ai",
            }
    except DeepSeekError:
        pass
    return fallback_yong_shen(chart, question).to_dict()


async def predict_one_fusion(
    q: ContestQuestion,
    client: DeepSeekClient,
    *,
    model_id: str | None = "deepseek-chat",
    use_knowledge: bool = True,
    use_case_rag: bool = True,
    fewshot_examples: list[dict[str, Any]] | None = None,
) -> QuestionResult:
    gold = q.answer
    try:
        chart = build_chart_for_question(q)
        compressed = None
        excerpts: list[dict[str, str]] = []
        if use_knowledge:
            compressed, excerpts = await _resolve_knowledge_context_async(
                chart,
                q.question,
                use_case_rag=use_case_rag,
            )
        bazi_system, bazi_user = build_contest_mcq_parts(
            chart,
            q.question,
            q.options,
            compressed=compressed,
            rag_excerpts=excerpts,
            fewshot_examples=fewshot_examples,
        )
        bazi_letter, bazi_raw, _ = await _mcq_letter(
            client, bazi_system, bazi_user, model_id
        )

        body = question_to_paipan_request(q)
        liuyao_chart = _liuyao_engine.divine(
            paipan_to_liuyao_input(body, q.question)
        ).to_dict()
        yong_shen = await _infer_yong_shen_deepseek(
            client, liuyao_chart, q.question, model_id
        )
        ly_excerpts: list[dict[str, str]] = []
        if settings.rag_provider == "http" and settings.rag_http_url:
            rag = build_rag_provider()
            ly_query = _liuyao_interpret.build_query(liuyao_chart, yong_shen, q.question)
            try:
                ly_excerpts = normalize_rag_excerpts(
                    await rag.search(
                        ly_query,
                        top_k=5,
                        category=settings.liuyao_rag_category,
                    )
                )
            except Exception as err:
                logger.warning("liuyao contest rag: %s", err)

        ly_system, ly_user = build_contest_liuyao_mcq_parts(
            liuyao_chart,
            yong_shen,
            q.question,
            q.options,
            rag_excerpts=ly_excerpts,
        )
        liuyao_letter, liuyao_raw, _ = await _mcq_letter(
            client, ly_system, ly_user, model_id
        )

        default_scope = settings.fusion_default_scope
        if default_scope not in ("life_outline", "event_detail", "mixed"):
            default_scope = "life_outline"
        merged, scope, preferred = merge_mcq_letters(
            bazi_letter,
            liuyao_letter,
            q.question,
            default_scope=default_scope,  # type: ignore[arg-type]
        )
        raw = f"bazi={bazi_raw}\nliuyao={liuyao_raw}\nmerged={merged}"
        return QuestionResult(
            question_id=q.question_id,
            year=q.year,
            gold=gold,
            predicted=merged,
            correct=merged == gold and merged != "",
            raw_response=raw,
            bazi_pred=bazi_letter,
            liuyao_pred=liuyao_letter,
            question_scope=scope,
            preferred_channel=preferred,
        )
    except Exception as err:
        logger.exception("fusion predict failed %s", q.question_id)
        return QuestionResult(
            question_id=q.question_id,
            year=q.year,
            gold=gold,
            predicted="",
            correct=False,
            raw_response="",
            error=str(err),
        )


async def predict_one_liuyao_only(
    q: ContestQuestion,
    client: DeepSeekClient,
    *,
    model_id: str | None = "deepseek-chat",
) -> QuestionResult:
    gold = q.answer
    try:
        body = question_to_paipan_request(q)
        liuyao_chart = _liuyao_engine.divine(
            paipan_to_liuyao_input(body, q.question)
        ).to_dict()
        yong_shen = await _infer_yong_shen_deepseek(
            client, liuyao_chart, q.question, model_id
        )
        ly_excerpts: list[dict[str, str]] = []
        if settings.rag_provider == "http" and settings.rag_http_url:
            rag = build_rag_provider()
            ly_query = _liuyao_interpret.build_query(liuyao_chart, yong_shen, q.question)
            try:
                ly_excerpts = normalize_rag_excerpts(
                    await rag.search(
                        ly_query,
                        top_k=5,
                        category=settings.liuyao_rag_category,
                    )
                )
            except Exception as err:
                logger.warning("liuyao contest rag: %s", err)

        ly_system, ly_user = build_contest_liuyao_mcq_parts(
            liuyao_chart,
            yong_shen,
            q.question,
            q.options,
            rag_excerpts=ly_excerpts,
        )
        liuyao_letter, liuyao_raw, _ = await _mcq_letter(
            client, ly_system, ly_user, model_id
        )
        return QuestionResult(
            question_id=q.question_id,
            year=q.year,
            gold=gold,
            predicted=liuyao_letter,
            correct=liuyao_letter == gold and liuyao_letter != "",
            raw_response=liuyao_raw,
            liuyao_pred=liuyao_letter,
        )
    except Exception as err:
        logger.exception("liuyao-only predict failed %s", q.question_id)
        return QuestionResult(
            question_id=q.question_id,
            year=q.year,
            gold=gold,
            predicted="",
            correct=False,
            raw_response="",
            error=str(err),
        )


async def predict_one(
    q: ContestQuestion,
    client: DeepSeekClient,
    *,
    model_id: str | None = "deepseek-chat",
    use_knowledge: bool = True,
    use_case_rag: bool = True,
    fewshot_examples: list[dict[str, Any]] | None = None,
    use_option_elimination: bool | None = None,
    votes: int = 1,
    temperature: float | None = None,
) -> QuestionResult:
    gold = q.answer
    try:
        chart = build_chart_for_question(q)
        compressed = None
        excerpts: list[dict[str, str]] = []
        if use_knowledge:
            compressed, excerpts = await _resolve_knowledge_context_async(
                chart,
                q.question,
                use_case_rag=use_case_rag,
            )
        if use_option_elimination is None:
            use_option_elimination = should_structured_mcq_reasoning(
                q.question, q.options
            )
        if fewshot_examples is None:
            fs = select_fewshot_by_theme(
                infer_question_theme(q.question),
                exclude_question_id=q.question_id,
                max_items=3,
            )
        else:
            fs = fewshot_examples
        system, user = build_contest_mcq_parts(
            chart,
            q.question,
            q.options,
            compressed=compressed,
            rag_excerpts=excerpts,
            fewshot_examples=fs,
            current_question_id=q.question_id,
            use_option_elimination=use_option_elimination,
        )
        temp = temperature
        if temp is None and use_option_elimination:
            temp = 0.2
        vote_n = max(1, min(int(votes), 5))
        letters: list[str] = []
        sources: list[str] = []
        raw_parts: list[str] = []
        for _ in range(vote_n):
            try:
                letter, raw, source = await _mcq_letter(
                    client,
                    system,
                    user,
                    model_id,
                    temperature=temp,
                    structured=bool(use_option_elimination),
                )
            except DeepSeekError as err:
                raise RuntimeError(str(err)) from err
            raw_parts.append(raw)
            if letter:
                letters.append(letter)
                sources.append(source)
        if letters:
            predicted = Counter(letters).most_common(1)[0][0]
            parse_source = sources[0] if sources else "empty"
        else:
            predicted = ""
            parse_source = "empty"
        raw_response = (
            " | ".join(p[:400] for p in raw_parts)[:1200]
            if vote_n > 1
            else (raw_parts[0] if raw_parts else "")
        )
        return QuestionResult(
            question_id=q.question_id,
            year=q.year,
            gold=gold,
            predicted=predicted,
            correct=predicted == gold and predicted != "",
            raw_response=raw_response,
            parse_source=parse_source,
            vote_letters=letters,
        )
    except Exception as err:
        logger.exception("predict failed %s", q.question_id)
        return QuestionResult(
            question_id=q.question_id,
            year=q.year,
            gold=gold,
            predicted="",
            correct=False,
            raw_response="",
            error=str(err),
        )


async def run_eval(
    split: SplitName,
    *,
    model_id: str | None = None,
    limit: int | None = None,
    use_knowledge: bool = True,
    use_case_rag: bool = True,
    use_fewshot: bool = False,
    use_fusion: bool = False,
    use_liuyao_only: bool = False,
    fewshot_path: Path | None = None,
    data_dir: Path | None = None,
    votes: int = 1,
    temperature: float | None = None,
    theme_fewshot: bool = True,
) -> EvalReport:
    questions = load_split(split, data_dir)
    if limit is not None:
        questions = questions[:limit]
    if use_fewshot:
        fewshot = (
            None
            if theme_fewshot
            else load_fewshot_examples(fewshot_path)
        )
    else:
        fewshot = []
    client = build_deepseek_client()
    results: list[QuestionResult] = []
    if use_liuyao_only:
        predict_fn = predict_one_liuyao_only
    elif use_fusion:
        predict_fn = predict_one_fusion
    else:
        predict_fn = predict_one
    total_q = len(questions)
    for idx, q in enumerate(questions, start=1):
        if idx == 1 or idx % 10 == 0 or idx == total_q:
            logger.info("eval %s progress %s/%s", split, idx, total_q)
        if use_liuyao_only:
            results.append(
                await predict_one_liuyao_only(q, client, model_id=model_id)
            )
        else:
            kwargs: dict[str, Any] = {
                "model_id": model_id,
                "use_knowledge": use_knowledge,
                "use_case_rag": use_case_rag,
                "fewshot_examples": fewshot,
            }
            if predict_fn is predict_one:
                kwargs["votes"] = votes
                kwargs["temperature"] = temperature
            results.append(await predict_fn(q, client, **kwargs))
    correct = sum(1 for r in results if r.correct)
    total = len(results)
    acc = correct / total if total else 0.0
    return EvalReport(
        split=split,
        total=total,
        correct=correct,
        accuracy=acc,
        results=results,
    )


def save_report(report: EvalReport, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
