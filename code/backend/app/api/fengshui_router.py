from __future__ import annotations

import logging
from typing import Any

from cursor_sdk import CursorAgentError
from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.quota_deps import consume_ai_quota
from app.config import settings
from app.core.agent.chat_orchestrator import ChatOrchestrator
from app.core.agent.prompts_fengshui import (
    build_fengshui_chat_init_prompt,
    build_fengshui_interpret_prompt,
)
from app.core.agent.service import AgentRunError
from app.core.fengshui.engine import FengshuiEngine
from app.core.knowledge.factory import get_knowledge_service
from app.core.fengshui.models import FengshuiInput
from app.core.fengshui.interpret_service import FengshuiInterpretService
from app.core.rag.base import normalize_rag_excerpts
from app.core.rag.factory import build_rag_provider
from app.schemas.chat import ChatInitResponse
from app.schemas.fengshui import (
    FengshuiChartRequest,
    FengshuiChartResponse,
    FengshuiChatInitRequest,
    FengshuiInterpretRequest,
    FengshuiInterpretResponse,
    FengshuiMethodInfo,
    FengshuiMethodsResponse,
    FengshuiMountainInfo,
    FengshuiMountainsResponse,
    FengshuiRagSearchRequest,
    FengshuiRagSearchResponse,
)

router = APIRouter(prefix="/api/v1/fengshui", tags=["fengshui"])
logger = logging.getLogger(__name__)

_engine = FengshuiEngine()
_interpret = FengshuiInterpretService()


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


def _request_to_input(body: FengshuiChartRequest) -> FengshuiInput:
    return FengshuiInput(
        question=body.question,
        method=body.method,
        scene=body.scene,
        birth_year=body.birthYear,
        gender=body.gender,
        sitting_mountain=body.sittingMountain,
        build_year=body.buildYear,
        flow_year=body.flowYear,
    )


def _knowledge_hits_dict(chart: dict[str, Any]) -> list[dict[str, Any]]:
    knowledge = get_knowledge_service()
    if not knowledge.enabled:
        return []
    result = knowledge.lookup_fengshui_chart(chart)
    return [hit.model_dump() for hit in result.hits]


@router.get("/methods", response_model=FengshuiMethodsResponse)
async def methods() -> FengshuiMethodsResponse:
    return FengshuiMethodsResponse(
        methods=[
            FengshuiMethodInfo(id="bazhai", label="八宅", implemented=True),
            FengshuiMethodInfo(id="xuankong", label="玄空飞星", implemented=True),
        ]
    )


@router.get("/mountains", response_model=FengshuiMountainsResponse)
async def mountains() -> FengshuiMountainsResponse:
    rows = _engine.list_mountains()
    return FengshuiMountainsResponse(
        mountains=[FengshuiMountainInfo(**row) for row in rows]
    )


@router.post("/chart", response_model=FengshuiChartResponse)
async def chart(body: FengshuiChartRequest) -> FengshuiChartResponse:
    try:
        result = _engine.chart(_request_to_input(body)).to_dict()
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    return FengshuiChartResponse(chart=result)


@router.post("/rag/search", response_model=FengshuiRagSearchResponse)
async def rag_search(body: FengshuiRagSearchRequest) -> FengshuiRagSearchResponse:
    question = body.question or body.chart.get("input", {}).get("question", "")
    query = _interpret.build_query(body.chart, question)
    rag = build_rag_provider()
    try:
        excerpts = await rag.search(query, category=settings.fengshui_rag_category)
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    return FengshuiRagSearchResponse(
        query=query,
        excerpts=normalize_rag_excerpts(excerpts),
    )


@router.post("/interpret", response_model=FengshuiInterpretResponse)
async def interpret(
    body: FengshuiInterpretRequest,
    request: Request,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
    _quota: str = Depends(consume_ai_quota),
) -> FengshuiInterpretResponse:
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
                await rag.search(query, category=settings.fengshui_rag_category)
            )
        except RuntimeError as err:
            raise HTTPException(status_code=503, detail=str(err)) from err

    summary: str | None = None
    agent_id: str | None = None
    if chat is not None and chat.enabled:
        prompt = build_fengshui_interpret_prompt(
            chart, knowledge_hits, excerpts, style=body.style
        )
        try:
            summary, agent_id = await chat.interpret(prompt, body.model)
            if agent_id:
                get_session_store(request).bind(_interpret.chart_key(chart), agent_id)
        except (CursorAgentError, AgentRunError, RuntimeError) as err:
            logger.warning("fengshui ai interpret failed: %s", err)

    payload = _interpret.build_response(
        chart, knowledge_hits, excerpts, summary=summary, agent_id=agent_id
    )
    return FengshuiInterpretResponse(chart=chart, interpretation=payload)


@router.post("/chat/init", response_model=ChatInitResponse)
async def chat_init(
    body: FengshuiChatInitRequest,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
) -> ChatInitResponse:
    if chat is None:
        raise HTTPException(status_code=404, detail="chat not configured")
    hits = body.knowledgeHits if body.knowledgeHits is not None else _knowledge_hits_dict(body.chart)
    bootstrap = build_fengshui_chat_init_prompt(
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
