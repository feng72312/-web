from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.interpret_deps import consume_interpret_quota
from app.config import settings
from app.core.agent.chat_orchestrator import ChatOrchestrator
from app.core.agent.prompts_ziwei import (
    build_ziwei_chat_init_prompt,
    build_ziwei_interpret_prompt,
)
from app.core.agent.service import AgentRunError
from app.core.rag.base import normalize_rag_excerpts
from app.core.rag.factory import build_rag_provider
from app.core.ziwei.engine import ZiweiEngine
from app.core.ziwei.interpret_service import ZiweiInterpretService
from app.core.ziwei.judgement.chain import ZiweiJudgementChain
from app.core.ziwei.models import ZiweiInput
from app.core.ziwei.rules import rules_from_payload
from app.schemas.chat import ChatInitResponse
from app.schemas.ziwei_judgement import ZiweiJudgementRequest, ZiweiJudgementResponse
from app.schemas.ziwei import (
    ZiweiChartRequest,
    ZiweiChartResponse,
    ZiweiChatInitRequest,
    ZiweiInterpretRequest,
    ZiweiInterpretResponse,
    ZiweiRagSearchRequest,
    ZiweiRagSearchResponse,
    ZiweiRulesOption,
    ZiweiRulesPayload,
    ZiweiRulesResponse,
)

router = APIRouter(prefix="/api/v1/ziwei", tags=["ziwei"])
logger = logging.getLogger(__name__)

_engine = ZiweiEngine()
_interpret = ZiweiInterpretService()
_judgement = ZiweiJudgementChain()


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


def _request_to_input(body: ZiweiChartRequest) -> ZiweiInput:
    rules = rules_from_payload(
        body.rules.model_dump(),
        default_leap=settings.ziwei_leap_month_rule,
        default_zi=settings.ziwei_zi_hour_rule,
        default_mutagen=settings.ziwei_mutagen_table,
    )
    return ZiweiInput(
        name=body.name,
        calendar_type=body.calendarType,  # type: ignore[arg-type]
        year=body.year,
        month=body.month,
        day=body.day,
        is_leap_month=body.isLeapMonth,
        hour=body.hour,
        minute=body.minute,
        second=body.second,
        gender=body.gender,
        use_true_solar_time=body.useTrueSolarTime,
        longitude=body.longitude,
        target_year=body.targetYear,
        detail_level=body.detailLevel,
        question=body.question,
        rules=rules,
    )


@router.get("/rules", response_model=ZiweiRulesResponse)
async def rules() -> ZiweiRulesResponse:
    return ZiweiRulesResponse(
        defaults=ZiweiRulesPayload(),
        leapMonthRules=[
            ZiweiRulesOption(id="next_month", label="闰月归下月"),
            ZiweiRulesOption(id="midmonth_split", label="闰月半月分界"),
        ],
        ziHourRules=[
            ZiweiRulesOption(id="combined", label="不分早晚子时"),
            ZiweiRulesOption(id="split", label="分早晚子时"),
        ],
        mutagenTables=[
            ZiweiRulesOption(id="nan_pai", label="南派三合(默认)"),
            ZiweiRulesOption(id="geng_beipai", label="北派庚干四化"),
            ZiweiRulesOption(id="wu_pai", label="王亭之戊干四化"),
            ZiweiRulesOption(id="ren_pai", label="壬干四化(天府科)"),
        ],
        chartSchools=[
            ZiweiRulesOption(id="sanhe", label="三合派(默认)"),
            ZiweiRulesOption(id="feixing", label="飞星派(宫干飞化)"),
        ],
    )


@router.post("/chart", response_model=ZiweiChartResponse)
async def chart(body: ZiweiChartRequest) -> ZiweiChartResponse:
    try:
        result = _engine.chart(_request_to_input(body)).to_dict()
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    return ZiweiChartResponse(chart=result)


@router.post("/rag/search", response_model=ZiweiRagSearchResponse)
async def rag_search(body: ZiweiRagSearchRequest) -> ZiweiRagSearchResponse:
    question = body.question or (body.chart.get("input") or {}).get("question", "")
    query = _interpret.build_query(body.chart, question)
    rag = build_rag_provider()
    try:
        excerpts = await rag.search(query, category=settings.ziwei_rag_category)
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    return ZiweiRagSearchResponse(
        query=query,
        excerpts=normalize_rag_excerpts(excerpts),
    )


@router.post("/judgement", response_model=ZiweiJudgementResponse)
async def judgement(body: ZiweiJudgementRequest) -> ZiweiJudgementResponse:
    try:
        report = await ZiweiJudgementChain(use_rag=body.useRag).run(
            body.chart,
            question=body.question,
            target_year=body.targetYear,
            school=body.school,
        )
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    payload = report.to_dict()
    arb = payload.get("arbitration") or {}
    return ZiweiJudgementResponse(
        judgement=payload,
        confidence=float(arb.get("confidenceScore") or 0.5),
        confidenceBand=str(arb.get("confidenceBand") or "medium"),
        conflicts=list(arb.get("conflicts") or []),
    )


@router.post("/interpret", response_model=ZiweiInterpretResponse)
async def interpret(
    body: ZiweiInterpretRequest,
    request: Request,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
    _quota: str = Depends(consume_interpret_quota),
) -> ZiweiInterpretResponse:
    chart = body.chart
    question = body.question or (chart.get("input") or {}).get("question", "")
    knowledge_hits: list[dict[str, Any]] = []
    judgement_report = await _judgement.run(chart, question=question)
    judgement_payload = judgement_report.to_dict()

    if body.excerpts is not None:
        excerpts = normalize_rag_excerpts(body.excerpts)
    else:
        tiered = judgement_payload.get("tieredEvidence") or {}
        merged = (
            tiered.get("primaryEvidence")
            or tiered.get("secondaryEvidence")
            or tiered.get("schoolCommentary")
            or []
        )
        if merged:
            excerpts = normalize_rag_excerpts(merged)
        else:
            query = _interpret.build_query(chart, question, judgement_payload)
            rag = build_rag_provider()
            try:
                excerpts = normalize_rag_excerpts(
                    await rag.search(query, category=settings.ziwei_rag_category)
                )
            except RuntimeError as err:
                raise HTTPException(status_code=503, detail=str(err)) from err

    summary: str | None = None
    agent_id: str | None = None
    if chat is not None and chat.enabled:
        prompt = build_ziwei_interpret_prompt(
            chart,
            knowledge_hits,
            excerpts,
            style=body.style,
            judgement=judgement_payload,
        )
        try:
            summary, agent_id = await chat.interpret(prompt, body.model)
            if agent_id:
                get_session_store(request).bind(_interpret.chart_key(chart), agent_id)
        except (AgentRunError, RuntimeError) as err:
            logger.warning("ziwei ai interpret failed: %s", err)

    payload = _interpret.build_response(
        chart,
        knowledge_hits,
        excerpts,
        summary=summary,
        agent_id=agent_id,
        judgement=judgement_payload,
    )
    return ZiweiInterpretResponse(chart=chart, interpretation=payload)


@router.post("/chat/init", response_model=ChatInitResponse)
async def chat_init(
    body: ZiweiChatInitRequest,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
) -> ChatInitResponse:
    if chat is None:
        raise HTTPException(status_code=404, detail="chat not configured")
    bootstrap = build_ziwei_chat_init_prompt(
        body.chart,
        body.knowledgeHits or [],
        body.excerpts or [],
    )
    try:
        session_id = await chat.create_session()
        chat.set_bootstrap(session_id, bootstrap)
        chat.bind_chart(_interpret.chart_key(body.chart), session_id)
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    return ChatInitResponse(agentId=session_id)
