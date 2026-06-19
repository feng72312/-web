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
from app.core.knowledge.contest_channel_route import (
    is_yingqi_question,
    resolve_contest_votes,
    uses_full_judgement_chain,
)
from app.core.knowledge.marriage_subtheme import infer_marriage_subtheme
from app.core.knowledge.career_subtheme import infer_career_subtheme
from app.core.knowledge.health_subtheme import infer_health_subtheme
from app.config import settings
from app.core.agent.deepseek import DeepSeekClient, DeepSeekError
from app.core.agent.prompts_contest import (
    build_bazi_ziwei_arbitrate_parts,
    build_contest_liuyao_mcq_parts,
    build_contest_mcq_parts,
    build_contest_ziwei_mcq_parts,
    load_fewshot_examples,
)
from app.core.agent.prompts_liuyao import build_yong_shen_prompt
from app.core.fusion.inputs import paipan_to_liuyao_input
from app.core.fusion.merge import merge_mcq_letters
from app.core.fusion.merge_bazi_ziwei import merge_bazi_ziwei_letters
from app.core.liuyao.engine import LiuyaoEngine
from app.core.liuyao.interpret_service import LiuyaoInterpretService
from app.core.liuyao.yong_shen_rules import fallback_yong_shen, parse_yong_shen_json
from app.benchmark.contest8_chart import question_to_paipan_request
from app.core.knowledge.factory import get_knowledge_service
from app.core.knowledge.rag_fallback import fetch_on_demand_rag
from app.core.knowledge.models import CompressedContext
from app.core.rag.factory import build_rag_provider
from app.benchmark.contest8_ziwei_chart import build_ziwei_chart_for_question
from app.benchmark.contest8_benchmark_meta import check_judgement_coverage, enrich_question
from app.core.knowledge.luck_chart import enrich_chart_for_judgement
from app.benchmark.error_labels import infer_error_labels
from app.benchmark.liuyao_error_labels import infer_liuyao_error_labels
from app.benchmark.ziwei_error_labels import infer_ziwei_error_labels
from app.core.judgement.chain import BaziJudgementChain
from app.core.liuyao.judgement.chain import LiuyaoJudgementChain
from app.core.ziwei.interpret_service import ZiweiInterpretService
from app.core.ziwei.judgement.chain import ZiweiJudgementChain
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
    ziwei_pred: str = ""
    question_scope: str = ""
    preferred_channel: str = ""
    parse_source: str = ""
    vote_letters: list[str] = field(default_factory=list)
    error_labels: list[str] = field(default_factory=list)
    judgement: dict[str, Any] = field(default_factory=dict)
    confidence_band: str = ""
    marriage_subtheme: str = ""
    career_subtheme: str = ""
    health_subtheme: str = ""


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
                    "ziweiPred": r.ziwei_pred,
                    "questionScope": r.question_scope,
                    "preferredChannel": r.preferred_channel,
                    "parseSource": r.parse_source,
                    "voteLetters": r.vote_letters,
                    "errorLabels": r.error_labels,
                    "judgement": r.judgement,
                    "confidenceBand": r.confidence_band,
                    "marriageSubtheme": r.marriage_subtheme,
                    "careerSubtheme": r.career_subtheme,
                    "healthSubtheme": r.health_subtheme,
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
_ziwei_interpret = ZiweiInterpretService()


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
    use_judgement: bool = True,
    use_rag: bool = True,
) -> QuestionResult:
    gold = q.answer
    try:
        body = question_to_paipan_request(q)
        liuyao_chart = _liuyao_engine.divine(
            paipan_to_liuyao_input(body, q.question)
        ).to_dict()
        judgement_dict: dict[str, Any] = {}
        yong_shen: dict[str, Any] = {}
        if use_judgement:
            report = await LiuyaoJudgementChain(use_rag=use_rag).run(
                liuyao_chart,
                question=q.question,
            )
            judgement_dict = report.to_dict()
            yong_shen = dict(judgement_dict.get("yongShen") or {})
            if float(yong_shen.get("confidence") or 0) < 0.35:
                yong_shen = await _infer_yong_shen_deepseek(
                    client, liuyao_chart, q.question, model_id
                )
        else:
            yong_shen = await _infer_yong_shen_deepseek(
                client, liuyao_chart, q.question, model_id
            )

        ly_excerpts: list[dict[str, str]] = []
        if use_judgement and judgement_dict:
            tiered = judgement_dict.get("tieredEvidence") or {}
            ly_excerpts = normalize_rag_excerpts(
                (tiered.get("primaryEvidence") or [])[:3]
                + (tiered.get("secondaryEvidence") or [])[:2]
            )
        if not ly_excerpts and settings.rag_provider == "http" and settings.rag_http_url:
            rag = build_rag_provider()
            ly_query = _liuyao_interpret.build_query(
                liuyao_chart,
                yong_shen,
                q.question,
                judgement_dict or None,
            )
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
            judgement=judgement_dict or None,
        )
        liuyao_letter, liuyao_raw, _ = await _mcq_letter(
            client, ly_system, ly_user, model_id
        )
        result = QuestionResult(
            question_id=q.question_id,
            year=q.year,
            gold=gold,
            predicted=liuyao_letter,
            correct=liuyao_letter == gold and liuyao_letter != "",
            raw_response=liuyao_raw,
            liuyao_pred=liuyao_letter,
            judgement=judgement_dict,
            confidence_band=str(
                (judgement_dict.get("arbitration") or {}).get("confidenceBand") or ""
            ),
        )
        result.error_labels = infer_liuyao_error_labels(
            gold=gold,
            predicted=liuyao_letter,
            judgement=judgement_dict or None,
            raw_response=liuyao_raw,
        )
        return result
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
            error_labels=["empty_prediction"],
        )


async def predict_one_bazi_ziwei_fusion(
    q: ContestQuestion,
    client: DeepSeekClient,
    *,
    model_id: str | None = "deepseek-chat",
    use_knowledge: bool = True,
    use_case_rag: bool = True,
    fewshot_examples: list[dict[str, Any]] | None = None,
    votes: int = 1,
    temperature: float | None = None,
    arbitrate_disagree: bool = False,
) -> QuestionResult:
    gold = q.answer
    try:
        bazi_r, ziwei_r = await asyncio.gather(
            predict_one(
                q,
                client,
                model_id=model_id,
                use_knowledge=use_knowledge,
                use_case_rag=use_case_rag,
                fewshot_examples=fewshot_examples,
                votes=votes,
                temperature=temperature,
            ),
            predict_one_ziwei_only(
                q,
                client,
                model_id=model_id,
                use_case_rag=use_case_rag,
                use_judgement=True,
                use_rag=settings.rag_provider == "http",
            ),
        )
        bazi_letter = bazi_r.predicted
        ziwei_letter = ziwei_r.predicted
        merged, preferred = merge_bazi_ziwei_letters(
            bazi_letter,
            ziwei_letter,
            q.question,
            bazi_confidence=bazi_r.confidence_band,
            ziwei_confidence=ziwei_r.confidence_band,
        )
        arb_raw = ""
        if (
            arbitrate_disagree
            and bazi_letter
            and ziwei_letter
            and bazi_letter.upper() != ziwei_letter.upper()
        ):
            arb_system, arb_user = build_bazi_ziwei_arbitrate_parts(
                q.question,
                q.options,
                bazi_letter,
                ziwei_letter,
                bazi_note=bazi_r.raw_response[:600],
                ziwei_note=ziwei_r.raw_response[:600],
            )
            arb_letter, arb_raw, _ = await _mcq_letter(
                client,
                arb_system,
                arb_user,
                model_id,
                temperature=0.2,
            )
            if arb_letter:
                merged = arb_letter
                preferred = "arbitrate"
        raw = (
            f"bazi={bazi_letter} ziwei={ziwei_letter} merged={merged} "
            f"channel={preferred}\n"
            f"bazi_raw={bazi_r.raw_response[:800]}\n"
            f"ziwei_raw={ziwei_r.raw_response[:800]}"
        )
        if arb_raw:
            raw += f"\narbitrate_raw={arb_raw[:400]}"
        return QuestionResult(
            question_id=q.question_id,
            year=q.year,
            gold=gold,
            predicted=merged,
            correct=merged == gold and merged != "",
            raw_response=raw,
            bazi_pred=bazi_letter,
            ziwei_pred=ziwei_letter,
            preferred_channel=preferred,
        )
    except Exception as err:
        logger.exception("bazi-ziwei fusion failed %s", q.question_id)
        return QuestionResult(
            question_id=q.question_id,
            year=q.year,
            gold=gold,
            predicted="",
            correct=False,
            raw_response="",
            error=str(err),
        )


async def predict_one_ziwei_only(
    q: ContestQuestion,
    client: DeepSeekClient,
    *,
    model_id: str | None = "deepseek-chat",
    use_case_rag: bool = True,
    use_judgement: bool = True,
    use_rag: bool = True,
) -> QuestionResult:
    gold = q.answer
    try:
        ziwei_chart = build_ziwei_chart_for_question(q)
        judgement_dict: dict[str, Any] = {}
        if use_judgement:
            report = await ZiweiJudgementChain(use_rag=use_rag).run(
                ziwei_chart,
                question=q.question,
                target_year=q.year,
            )
            judgement_dict = report.to_dict()
            enriched = judgement_dict.get("enrichedChart")
            if enriched:
                ziwei_chart = enriched

        zw_excerpts: list[dict[str, str]] = []
        if use_judgement and judgement_dict:
            tiered = judgement_dict.get("tieredEvidence") or {}
            zw_excerpts = normalize_rag_excerpts(
                (tiered.get("primaryEvidence") or [])[:3]
                + (tiered.get("secondaryEvidence") or [])[:2]
            )
        if not zw_excerpts and use_case_rag and settings.rag_provider == "http" and settings.rag_http_url:
            rag = build_rag_provider()
            zw_query = _ziwei_interpret.build_query(
                ziwei_chart,
                q.question,
                judgement_dict or None,
            )
            try:
                zw_excerpts = normalize_rag_excerpts(
                    await rag.search(
                        zw_query,
                        top_k=5,
                        category=settings.ziwei_rag_category,
                    )
                )
            except Exception as err:
                logger.warning("ziwei contest rag: %s", err)
        zw_system, zw_user = build_contest_ziwei_mcq_parts(
            ziwei_chart,
            q.question,
            q.options,
            rag_excerpts=zw_excerpts,
            judgement=judgement_dict or None,
        )
        ziwei_letter, ziwei_raw, _ = await _mcq_letter(
            client, zw_system, zw_user, model_id, temperature=0.2
        )
        result = QuestionResult(
            question_id=q.question_id,
            year=q.year,
            gold=gold,
            predicted=ziwei_letter,
            correct=ziwei_letter == gold and ziwei_letter != "",
            raw_response=ziwei_raw,
            ziwei_pred=ziwei_letter,
            judgement=judgement_dict,
            confidence_band=str(
                (judgement_dict.get("arbitration") or {}).get("confidenceBand") or ""
            ),
        )
        result.error_labels = infer_ziwei_error_labels(
            gold=gold,
            predicted=ziwei_letter,
            judgement=judgement_dict or None,
            raw_response=ziwei_raw,
            question=q.question,
        )
        return result
    except Exception as err:
        logger.exception("ziwei-only predict failed %s", q.question_id)
        return QuestionResult(
            question_id=q.question_id,
            year=q.year,
            gold=gold,
            predicted="",
            correct=False,
            raw_response="",
            error=str(err),
            error_labels=["empty_prediction"],
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
        benchmark_meta = enrich_question(q)
        chart = enrich_chart_for_judgement(
            chart,
            question=q.question,
            benchmark_meta=benchmark_meta,
        )
        full_judgement = uses_full_judgement_chain(q.question, q.options)
        yingqi_mode = is_yingqi_question(q.question, q.options)
        judgement_dict: dict[str, Any] = {}
        if full_judgement:
            judgement_chain = BaziJudgementChain(
                use_rag=settings.rag_provider == "http"
            )
            judgement_report = await judgement_chain.run(
                chart,
                question=q.question,
                benchmark_meta=benchmark_meta,
            )
            judgement_dict = judgement_report.to_dict()
            judgement_dict["benchmarkMeta"] = benchmark_meta
            judgement_dict["coverage"] = check_judgement_coverage(
                judgement_dict, benchmark_meta
            )
        case_rag_enabled = use_case_rag and full_judgement
        compressed = None
        excerpts: list[dict[str, str]] = []
        if use_knowledge:
            compressed, excerpts = await _resolve_knowledge_context_async(
                chart,
                q.question,
                use_case_rag=case_rag_enabled,
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
            judgement=judgement_dict or None,
            judgement_profile="full" if full_judgement else ("yingqi" if yingqi_mode else None),
        )
        temp = temperature
        if temp is None and use_option_elimination:
            temp = 0.2
        vote_n = resolve_contest_votes(q.question, q.options, votes)
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
        marriage_subtheme = ""
        if infer_question_theme(q.question) == "婚姻感情":
            st = infer_marriage_subtheme(q.question, q.options)
            marriage_subtheme = st or ""
        career_subtheme = ""
        if infer_question_theme(q.question) == "职业财运":
            st = infer_career_subtheme(q.question, q.options)
            career_subtheme = st or ""
        health_subtheme = ""
        if infer_question_theme(q.question) == "健康疾病":
            st = infer_health_subtheme(q.question, q.options)
            health_subtheme = st or ""
        result = QuestionResult(
            question_id=q.question_id,
            year=q.year,
            gold=gold,
            predicted=predicted,
            correct=predicted == gold and predicted != "",
            raw_response=raw_response,
            parse_source=parse_source,
            vote_letters=letters,
            judgement=judgement_dict,
            confidence_band=str(
                (judgement_dict.get("arbitration") or {}).get("confidenceBand") or ""
            ),
            marriage_subtheme=marriage_subtheme,
            career_subtheme=career_subtheme,
            health_subtheme=health_subtheme,
        )
        if not result.correct:
            result.error_labels = infer_error_labels(
                gold=gold,
                predicted=predicted,
                judgement=judgement_dict,
                raw_response=raw_response,
            )
        return result
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
    use_bazi_ziwei_fusion: bool = False,
    fusion_arbitrate: bool = False,
    use_liuyao_only: bool = False,
    use_ziwei_only: bool = False,
    fewshot_path: Path | None = None,
    data_dir: Path | None = None,
    votes: int = 1,
    temperature: float | None = None,
    theme_fewshot: bool = True,
    question_ids: list[str] | None = None,
) -> EvalReport:
    questions = load_split(split, data_dir)
    if question_ids:
        id_set = set(question_ids)
        questions = [q for q in questions if q.question_id in id_set]
    elif limit is not None:
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
    if use_bazi_ziwei_fusion:
        predict_fn = predict_one_bazi_ziwei_fusion
    elif use_ziwei_only:
        predict_fn = predict_one_ziwei_only
    elif use_liuyao_only:
        predict_fn = predict_one_liuyao_only
    elif use_fusion:
        predict_fn = predict_one_fusion
    else:
        predict_fn = predict_one
    total_q = len(questions)
    for idx, q in enumerate(questions, start=1):
        if idx == 1 or idx % 10 == 0 or idx == total_q:
            logger.info("eval %s progress %s/%s", split, idx, total_q)
        if use_bazi_ziwei_fusion:
            fs = fewshot
            if fs is None and not use_fewshot:
                fs = []
            results.append(
                await predict_one_bazi_ziwei_fusion(
                    q,
                    client,
                    model_id=model_id,
                    use_knowledge=use_knowledge,
                    use_case_rag=use_case_rag,
                    fewshot_examples=fewshot if use_fewshot else [],
                    votes=votes,
                    temperature=temperature,
                    arbitrate_disagree=fusion_arbitrate,
                )
            )
        elif use_ziwei_only:
            results.append(
                await predict_one_ziwei_only(
                    q,
                    client,
                    model_id=model_id,
                    use_case_rag=use_case_rag,
                    use_judgement=True,
                    use_rag=settings.rag_provider == "http",
                )
            )
        elif use_liuyao_only:
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
