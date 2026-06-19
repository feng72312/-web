from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.interpret_deps import consume_interpret_quota
from app.config import settings
from app.core.agent.chat_orchestrator import ChatOrchestrator
from app.core.agent.prompts_xingming import (
    build_xingming_chat_init_prompt,
    build_xingming_interpret_prompt,
)
from app.core.agent.service import AgentRunError
from app.core.knowledge.factory import get_knowledge_service
from app.core.rag.base import normalize_rag_excerpts
from app.core.rag.factory import build_rag_provider
from app.core.xingming.case_store import search_cases
from app.core.xingming.engine import XingmingEngine
from app.core.xingming.interpret_service import XingmingInterpretService
from app.core.xingming.models import XingmingInput
from app.core.xingming.rules import rules_from_payload
from app.schemas.chat import ChatInitResponse
from app.schemas.xingming import (
    XingmingCasesSearchRequest,
    XingmingCasesSearchResponse,
    XingmingChartRequest,
    XingmingChartResponse,
    XingmingChatInitRequest,
    XingmingInterpretRequest,
    XingmingInterpretResponse,
    XingmingRagSearchRequest,
    XingmingRagSearchResponse,
    XingmingRulesOption,
    XingmingRulesPayload,
    XingmingRulesResponse,
)

router = APIRouter(prefix="/api/v1/xingming", tags=["xingming"])
logger = logging.getLogger(__name__)

_engine = XingmingEngine()
_interpret = XingmingInterpretService()


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


def _request_to_input(body: XingmingChartRequest) -> XingmingInput:
    rules = rules_from_payload(body.rules.model_dump())
    return XingmingInput(
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
        latitude=body.latitude,
        target_year=body.targetYear,
        question=body.question,
        rules=rules,
    )


@router.get("/rules", response_model=XingmingRulesResponse)
async def rules() -> XingmingRulesResponse:
    return XingmingRulesResponse(
        defaults=XingmingRulesPayload(),
        schools=[XingmingRulesOption(id="guolao_v1", label="\u679c\u8001\u661f\u5b97 V1")],
        ziHourRules=[
            XingmingRulesOption(id="combined", label="\u4e0d\u5206\u65e9\u665a\u5b50\u65f6"),
            XingmingRulesOption(id="split", label="\u5206\u65e9\u665a\u5b50\u65f6"),
        ],
        dayNightRules=[
            XingmingRulesOption(id="auto", label="\u81ea\u52a8\u663c\u591c"),
            XingmingRulesOption(id="day", label="\u65e5\u751f"),
            XingmingRulesOption(id="night", label="\u591c\u751f"),
        ],
    )


@router.post("/chart", response_model=XingmingChartResponse)
async def chart(body: XingmingChartRequest) -> XingmingChartResponse:
    try:
        result = _engine.chart(_request_to_input(body)).to_dict()
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    return XingmingChartResponse(chart=result)


@router.post("/rag/search", response_model=XingmingRagSearchResponse)
async def rag_search(body: XingmingRagSearchRequest) -> XingmingRagSearchResponse:
    question = body.question or (body.chart.get("input") or {}).get("question", "")
    query = _interpret.build_query(body.chart, question)
    rag = build_rag_provider()
    try:
        excerpts = await rag.search(query, category=settings.xingming_rag_category)
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    return XingmingRagSearchResponse(
        query=query,
        excerpts=normalize_rag_excerpts(excerpts),
    )


@router.post("/cases/search", response_model=XingmingCasesSearchResponse)
async def cases_search(body: XingmingCasesSearchRequest) -> XingmingCasesSearchResponse:
    question = body.question or (body.chart.get("input") or {}).get("question", "")
    tier = body.tier if body.tier else None
    if settings.xingming_case_gold_only:
        tier = "gold"
    hits = search_cases(body.chart, question, tier=tier, top_k=body.topK)
    return XingmingCasesSearchResponse(cases=hits)


@router.post("/interpret", response_model=XingmingInterpretResponse)
async def interpret(
    body: XingmingInterpretRequest,
    request: Request,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
    _quota: str = Depends(consume_interpret_quota),
) -> XingmingInterpretResponse:
    chart = body.chart
    question = body.question or (chart.get("input") or {}).get("question", "")
    knowledge_hits: list[dict[str, Any]] = []
    knowledge = get_knowledge_service()
    if knowledge.enabled:
        try:
            resolved = knowledge.resolve_for_xingming(chart)
            knowledge_hits = [h.model_dump() for h in resolved.hits]
        except Exception as err:
            logger.warning("xingming knowledge lookup failed: %s", err)

    if body.excerpts is not None:
        excerpts = normalize_rag_excerpts(body.excerpts)
    else:
        query = _interpret.build_query(chart, question)
        rag = build_rag_provider()
        try:
            excerpts = normalize_rag_excerpts(
                await rag.search(query, category=settings.xingming_rag_category)
            )
        except RuntimeError as err:
            raise HTTPException(status_code=503, detail=str(err)) from err

    if body.cases is not None:
        cases = body.cases
    else:
        cases = search_cases(chart, question, tier="gold" if settings.xingming_case_gold_only else None)

    cross = body.crossCharts.model_dump() if body.crossCharts else None
    summary: str | None = None
    agent_id: str | None = None
    if chat is not None and chat.enabled:
        prompt = build_xingming_interpret_prompt(
            chart,
            knowledge_hits,
            excerpts,
            cases,
            cross_charts=cross,
            style=body.style,
        )
        try:
            summary, agent_id = await chat.interpret(prompt, body.model)
            if agent_id:
                get_session_store(request).bind(_interpret.chart_key(chart), agent_id)
        except (AgentRunError, RuntimeError) as err:
            logger.warning("xingming ai interpret failed: %s", err)

    payload = _interpret.build_response(
        chart,
        knowledge_hits,
        excerpts,
        cases,
        summary=summary,
        agent_id=agent_id,
    )
    return XingmingInterpretResponse(chart=chart, interpretation=payload)


@router.post("/chat/init", response_model=ChatInitResponse)
async def chat_init(
    body: XingmingChatInitRequest,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
) -> ChatInitResponse:
    if chat is None:
        raise HTTPException(status_code=404, detail="chat not configured")
    cross = body.crossCharts.model_dump() if body.crossCharts else None
    bootstrap = build_xingming_chat_init_prompt(
        body.chart,
        body.knowledgeHits or [],
        body.excerpts or [],
        body.cases or [],
        cross_charts=cross,
    )
    try:
        session_id = await chat.create_session()
        chat.set_bootstrap(session_id, bootstrap)
        chat.bind_chart(_interpret.chart_key(body.chart), session_id)
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    return ChatInitResponse(agentId=session_id)
