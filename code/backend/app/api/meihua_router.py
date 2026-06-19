from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.interpret_deps import consume_interpret_quota
from app.config import settings
from app.core.agent.chat_orchestrator import ChatOrchestrator
from app.core.agent.prompts_meihua import (
    build_meihua_chat_init_prompt,
    build_meihua_interpret_prompt,
)
from app.core.agent.service import AgentRunError
from app.core.knowledge.factory import get_knowledge_service
from app.core.meihua.engine import MeihuaEngine
from app.core.meihua.interpret_service import MeihuaInterpretService
from app.core.meihua.models import MeihuaInput
from app.core.rag.base import normalize_rag_excerpts
from app.core.rag.factory import build_rag_provider
from app.schemas.chat import ChatInitResponse
from app.schemas.meihua import (
    MeihuaChatInitRequest,
    MeihuaDivineRequest,
    MeihuaDivineResponse,
    MeihuaInterpretRequest,
    MeihuaInterpretResponse,
    MeihuaRagSearchRequest,
    MeihuaRagSearchResponse,
    MeihuaTiYongRequest,
    MeihuaTiYongResponse,
)

router = APIRouter(prefix="/api/v1/meihua", tags=["meihua"])
logger = logging.getLogger(__name__)

_engine = MeihuaEngine()
_interpret = MeihuaInterpretService()


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


def _request_to_input(body: MeihuaDivineRequest) -> MeihuaInput:
    return MeihuaInput(
        question=body.question,
        method=body.method,
        numbers=body.numbers,
        year=body.year,
        month=body.month,
        day=body.day,
        hour=body.hour,
        minute=body.minute,
        second=body.second,
        calendar_type=body.calendarType,
        is_leap_month=body.isLeapMonth,
        moving_position_override=body.movingPositionOverride,
    )


def _knowledge_hits_dict(chart: dict[str, Any]) -> list[dict[str, Any]]:
    knowledge = get_knowledge_service()
    if not knowledge.enabled:
        return []
    result = knowledge.lookup_meihua_chart(chart)
    return [hit.model_dump() for hit in result.hits]


@router.post("/divine", response_model=MeihuaDivineResponse)
async def divine(body: MeihuaDivineRequest) -> MeihuaDivineResponse:
    try:
        chart = _engine.divine(_request_to_input(body)).to_dict()
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    return MeihuaDivineResponse(chart=chart)


@router.post("/ti-yong", response_model=MeihuaTiYongResponse)
async def ti_yong(body: MeihuaTiYongRequest) -> MeihuaTiYongResponse:
    chart = dict(body.chart)
    meta = chart.get("meta") or {}
    line_values = meta.get("lineValues")
    if not line_values or len(line_values) != 6:
        raise HTTPException(status_code=400, detail="chart missing meta.lineValues")
    from app.core.meihua.ti_yong import build_chart_parts

    parts = build_chart_parts(line_values, moving_override=body.movingPosition)
    chart["movingLines"] = parts["moving"]
    chart["tiGua"] = parts["ti"].to_dict()
    chart["yongGua"] = parts["yong"].to_dict()
    chart["tiYongRelation"] = parts["relation"]
    chart["isStatic"] = parts["is_static"]
    chart["bianGua"] = parts["bian"].to_dict() if parts["bian"] else None
    chart["huGua"] = parts["hu"].to_dict() if parts["hu"] else None
    meta = dict(meta)
    meta["tiYongMeta"] = parts["ti_meta"]
    chart["meta"] = meta
    chart.setdefault("input", {})["movingPositionOverride"] = body.movingPosition
    return MeihuaTiYongResponse(chart=chart)


@router.post("/rag/search", response_model=MeihuaRagSearchResponse)
async def rag_search(body: MeihuaRagSearchRequest) -> MeihuaRagSearchResponse:
    question = body.question or body.chart.get("input", {}).get("question", "")
    query = _interpret.build_query(body.chart, question)
    rag = build_rag_provider()
    try:
        excerpts = await rag.search(query, category=settings.meihua_rag_category)
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    return MeihuaRagSearchResponse(
        query=query,
        excerpts=normalize_rag_excerpts(excerpts),
    )


@router.post("/interpret", response_model=MeihuaInterpretResponse)
async def interpret(
    body: MeihuaInterpretRequest,
    request: Request,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
    _quota: str = Depends(consume_interpret_quota),
) -> MeihuaInterpretResponse:
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
                await rag.search(query, category=settings.meihua_rag_category)
            )
        except RuntimeError as err:
            raise HTTPException(status_code=503, detail=str(err)) from err

    summary: str | None = None
    agent_id: str | None = None
    if chat is not None and chat.enabled:
        prompt = build_meihua_interpret_prompt(
            chart, knowledge_hits, excerpts, style=body.style
        )
        try:
            summary, agent_id = await chat.interpret(prompt, body.model)
            if agent_id:
                session_store = get_session_store(request)
                session_store.bind(_interpret.chart_key(chart), agent_id)
        except (AgentRunError, RuntimeError) as err:
            logger.warning("meihua ai interpret failed: %s", err)

    payload = _interpret.build_response(
        chart,
        knowledge_hits,
        excerpts,
        summary=summary,
        agent_id=agent_id,
    )
    return MeihuaInterpretResponse(chart=chart, interpretation=payload)


@router.post("/chat/init", response_model=ChatInitResponse)
async def chat_init(
    body: MeihuaChatInitRequest,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
) -> ChatInitResponse:
    if chat is None:
        raise HTTPException(status_code=404, detail="chat not configured")
    hits = body.knowledgeHits if body.knowledgeHits is not None else _knowledge_hits_dict(body.chart)
    bootstrap = build_meihua_chat_init_prompt(
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
