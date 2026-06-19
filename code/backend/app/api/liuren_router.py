from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.interpret_deps import consume_interpret_quota
from app.config import settings
from app.core.agent.chat_orchestrator import ChatOrchestrator
from app.core.agent.prompts_liuren import (
    build_liuren_chat_init_prompt,
    build_liuren_interpret_prompt,
)
from app.core.agent.service import AgentRunError
from app.core.knowledge.factory import get_knowledge_service
from app.core.liuren.engine import LiurenEngine
from app.core.liuren.interpret_service import LiurenInterpretService
from app.core.liuren.models import LiurenInput
from app.core.rag.base import normalize_rag_excerpts
from app.core.rag.factory import build_rag_provider
from app.schemas.chat import ChatInitResponse
from app.schemas.liuren import (
    LiurenChartRequest,
    LiurenChartResponse,
    LiurenChatInitRequest,
    LiurenInterpretRequest,
    LiurenInterpretResponse,
    LiurenMethodInfo,
    LiurenMethodsResponse,
    LiurenRagSearchRequest,
    LiurenRagSearchResponse,
)

router = APIRouter(prefix="/api/v1/liuren", tags=["liuren"])
logger = logging.getLogger(__name__)

_engine = LiurenEngine()
_interpret = LiurenInterpretService()


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


def _request_to_input(body: LiurenChartRequest) -> LiurenInput:
    return LiurenInput(
        question=body.question,
        cast_method=body.castMethod,
        category=body.category,
        year=body.year,
        month=body.month,
        day=body.day,
        hour=body.hour,
        minute=body.minute,
        second=body.second,
        calendar_type=body.calendarType,
        is_leap_month=body.isLeapMonth,
        use_true_solar_time=body.useTrueSolarTime,
        longitude=body.longitude,
        jinkou_difen=body.jinkouDifen,
        gui_ren_mode=body.guiRenMode,
    )


def _knowledge_hits_dict(chart: dict[str, Any]) -> list[dict[str, Any]]:
    knowledge = get_knowledge_service()
    if not knowledge.enabled:
        return []
    result = knowledge.lookup_liuren_chart(chart)
    return [hit.model_dump() for hit in result.hits]


@router.get("/methods", response_model=LiurenMethodsResponse)
async def methods() -> LiurenMethodsResponse:
    return LiurenMethodsResponse(
        methods=[
            LiurenMethodInfo(id="liuren", label="正六壬", implemented=True),
            LiurenMethodInfo(id="jinkou", label="金口诀", implemented=True),
            LiurenMethodInfo(id="both", label="六壬+金口诀", implemented=True),
        ]
    )


@router.post("/chart", response_model=LiurenChartResponse)
async def chart(body: LiurenChartRequest) -> LiurenChartResponse:
    try:
        result = _engine.chart(_request_to_input(body)).to_dict()
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    return LiurenChartResponse(chart=result)


@router.post("/rag/search", response_model=LiurenRagSearchResponse)
async def rag_search(body: LiurenRagSearchRequest) -> LiurenRagSearchResponse:
    question = body.question or body.chart.get("input", {}).get("question", "")
    query = _interpret.build_query(body.chart, question)
    rag = build_rag_provider()
    try:
        excerpts = await rag.search(query, category=settings.liuren_rag_category)
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    return LiurenRagSearchResponse(
        query=query,
        excerpts=normalize_rag_excerpts(excerpts),
    )


@router.post("/interpret", response_model=LiurenInterpretResponse)
async def interpret(
    body: LiurenInterpretRequest,
    request: Request,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
    _quota: str = Depends(consume_interpret_quota),
) -> LiurenInterpretResponse:
    chart = body.chart
    question = body.question or chart.get("input", {}).get("question", "")
    knowledge_hits = _knowledge_hits_dict(chart)

    if body.excerpts is not None:
        excerpts = normalize_rag_excerpts(body.excerpts)
    else:
        query = _interpret.build_query(chart, question)
        rag = build_rag_provider()
        try:
            excerpts = normalize_rag_excerpts(
                await rag.search(query, category=settings.liuren_rag_category)
            )
        except RuntimeError as err:
            raise HTTPException(status_code=503, detail=str(err)) from err

    summary: str | None = None
    agent_id: str | None = None
    if chat is not None and chat.enabled:
        prompt = build_liuren_interpret_prompt(
            chart, knowledge_hits, excerpts, style=body.style
        )
        try:
            summary, agent_id = await chat.interpret(prompt, body.model)
            if agent_id:
                get_session_store(request).bind(_interpret.chart_key(chart), agent_id)
        except (AgentRunError, RuntimeError) as err:
            logger.warning("liuren ai interpret failed: %s", err)

    payload = _interpret.build_response(
        chart, knowledge_hits, excerpts, summary=summary, agent_id=agent_id
    )
    return LiurenInterpretResponse(chart=chart, interpretation=payload)


@router.post("/chat/init", response_model=ChatInitResponse)
async def chat_init(
    body: LiurenChatInitRequest,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
) -> ChatInitResponse:
    if chat is None:
        raise HTTPException(status_code=404, detail="chat not configured")
    hits = body.knowledgeHits if body.knowledgeHits is not None else _knowledge_hits_dict(body.chart)
    bootstrap = build_liuren_chat_init_prompt(
        body.chart,
        hits,
        body.excerpts or [],
    )
    try:
        session_id = await chat.create_session()
        chat.set_bootstrap(session_id, bootstrap)
        chat.bind_chart(_interpret.chart_key(body.chart), session_id)
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    return ChatInitResponse(agentId=session_id)
