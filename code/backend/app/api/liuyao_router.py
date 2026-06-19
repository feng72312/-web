from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.interpret_deps import consume_interpret_quota
from app.config import settings
from app.core.agent.chat_orchestrator import ChatOrchestrator
from app.core.agent.prompts_liuyao import (
    build_liuyao_chat_init_prompt,
    build_liuyao_interpret_prompt,
)
from app.core.agent.service import AgentRunError
from app.core.liuyao.engine import LiuyaoEngine
from app.core.liuyao.interpret_service import LiuyaoInterpretService
from app.core.liuyao.judgement.chain import LiuyaoJudgementChain
from app.core.liuyao.models import LiuyaoInput
from app.core.liuyao.yong_shen_service import YongShenService
from app.core.rag.factory import build_rag_provider
from app.core.rag.base import normalize_rag_excerpts
from app.schemas.chat import ChatInitResponse
from app.schemas.liuyao import (
    LiuyaoChatInitRequest,
    LiuyaoDivineRequest,
    LiuyaoDivineResponse,
    LiuyaoInferYongShenRequest,
    LiuyaoInterpretRequest,
    LiuyaoInterpretResponse,
    LiuyaoRagSearchRequest,
    LiuyaoRagSearchResponse,
    LiuyaoYongShenOverrideRequest,
    YongShenResponse,
)
from app.schemas.liuyao_judgement import LiuyaoJudgementRequest, LiuyaoJudgementResponse

router = APIRouter(prefix="/api/v1/liuyao", tags=["liuyao"])
logger = logging.getLogger(__name__)

_engine = LiuyaoEngine()
_yong_shen = YongShenService()
_interpret = LiuyaoInterpretService()
_judgement = LiuyaoJudgementChain()


def get_chat_orchestrator(request: Request) -> ChatOrchestrator | None:
    orchestrator = getattr(request.app.state, "chat_orchestrator", None)
    if orchestrator is None or not orchestrator.enabled:
        return None
    return orchestrator


def get_session_store(request: Request):
    store = getattr(request.app.state, "session_store", None)
    if store is None:
        raise HTTPException(status_code=503, detail="session store not initialized")
    return store


def _request_to_input(body: LiuyaoDivineRequest) -> LiuyaoInput:
    return LiuyaoInput(
        question=body.question,
        method=body.method,
        coin_lines=body.coinLines,
        numbers=body.numbers,
        year=body.year,
        month=body.month,
        day=body.day,
        hour=body.hour,
        minute=body.minute,
        second=body.second,
        calendar_type=body.calendarType,
        is_leap_month=body.isLeapMonth,
    )


def _normalize_excerpts(excerpts: list[dict[str, str]]) -> list[dict[str, str]]:
    return normalize_rag_excerpts(excerpts)


@router.post("/divine", response_model=LiuyaoDivineResponse)
async def divine(body: LiuyaoDivineRequest) -> LiuyaoDivineResponse:
    try:
        chart = _engine.divine(_request_to_input(body)).to_dict()
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    return LiuyaoDivineResponse(chart=chart)


@router.post("/infer-yong-shen", response_model=YongShenResponse)
async def infer_yong_shen(
    body: LiuyaoInferYongShenRequest,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
) -> YongShenResponse:
    result = await _yong_shen.infer(
        body.chart,
        body.question.strip(),
        chat,
        body.model,
    )
    return YongShenResponse(**result.to_dict())


@router.post("/yong-shen", response_model=YongShenResponse)
async def override_yong_shen(body: LiuyaoYongShenOverrideRequest) -> YongShenResponse:
    try:
        result = _yong_shen.apply_override(body.chart, body.yongShen, body.position)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    return YongShenResponse(**result.to_dict())


@router.post("/rag/search", response_model=LiuyaoRagSearchResponse)
async def rag_search(body: LiuyaoRagSearchRequest) -> LiuyaoRagSearchResponse:
    query = _interpret.build_query(body.chart, body.yongShen, body.question)
    rag = build_rag_provider()
    try:
        excerpts = await rag.search(query, category=settings.liuyao_rag_category)
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    excerpts = _normalize_excerpts(excerpts)
    return LiuyaoRagSearchResponse(query=query, excerpts=excerpts)


@router.post("/judgement", response_model=LiuyaoJudgementResponse)
async def judgement(body: LiuyaoJudgementRequest) -> LiuyaoJudgementResponse:
    chart = body.chart
    question = body.question or chart.get("input", {}).get("question", "")
    try:
        report = await LiuyaoJudgementChain(use_rag=body.useRag).run(
            chart,
            question=question,
            yong_shen=body.yongShen,
            yong_shen_override=body.yongShenOverride,
        )
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    payload = report.to_dict()
    arbitration = payload.get("arbitration") or {}
    return LiuyaoJudgementResponse(
        judgement=payload,
        confidence=float(arbitration.get("confidenceScore") or 0.5),
        confidenceBand=str(arbitration.get("confidenceBand") or "medium"),
        conflicts=list(arbitration.get("conflicts") or []),
    )


@router.post("/interpret", response_model=LiuyaoInterpretResponse)
async def interpret(
    body: LiuyaoInterpretRequest,
    request: Request,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
    _quota: str = Depends(consume_interpret_quota),
) -> LiuyaoInterpretResponse:
    chart = body.chart
    question = body.question or chart.get("input", {}).get("question", "")

    judgement_report = await _judgement.run(chart, question=question, yong_shen=body.yongShen)
    judgement_payload = judgement_report.to_dict()
    yong_shen = judgement_payload.get("yongShen") or {}

    if body.excerpts is not None:
        excerpts = _normalize_excerpts(body.excerpts)
    else:
        tiered = judgement_payload.get("tieredEvidence") or {}
        excerpts = _normalize_excerpts(
            (tiered.get("primaryEvidence") or [])
            + (tiered.get("secondaryEvidence") or [])
        )
        if not excerpts:
            query = _interpret.build_query(chart, yong_shen, question, judgement_payload)
            rag = build_rag_provider()
            try:
                excerpts = await rag.search(query, category=settings.liuyao_rag_category)
            except RuntimeError as err:
                raise HTTPException(status_code=503, detail=str(err)) from err
            excerpts = _normalize_excerpts(excerpts)

    summary: str | None = None
    agent_id: str | None = None
    if chat is not None and chat.enabled:
        prompt = build_liuyao_interpret_prompt(
            chart,
            yong_shen,
            excerpts,
            style=body.style,
            judgement=judgement_payload,
        )
        try:
            summary, agent_id = await chat.interpret(prompt, body.model)
            if agent_id:
                session_store = get_session_store(request)
                session_store.bind(_interpret.chart_key(chart), agent_id)
        except (AgentRunError, RuntimeError) as err:
            logger.warning("liuyao ai interpret failed: %s", err)

    payload = _interpret.build_response(
        chart,
        yong_shen,
        excerpts,
        summary=summary,
        agent_id=agent_id,
        judgement=judgement_payload,
    )
    return LiuyaoInterpretResponse(chart=chart, interpretation=payload)


@router.post("/chat/init", response_model=ChatInitResponse)
async def chat_init(
    body: LiuyaoChatInitRequest,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
) -> ChatInitResponse:
    if chat is None:
        raise HTTPException(status_code=404, detail="chat not configured")
    bootstrap = build_liuyao_chat_init_prompt(
        body.chart,
        body.yongShen,
        body.excerpts or [],
    )
    try:
        session_id = await chat.create_session()
        chat.set_bootstrap(session_id, bootstrap)
        chat.bind_chart(_interpret.chart_key(body.chart), session_id)
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    return ChatInitResponse(agentId=session_id)
