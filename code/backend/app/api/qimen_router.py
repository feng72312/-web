from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.interpret_deps import consume_interpret_quota
from app.config import settings
from app.core.agent.chat_orchestrator import ChatOrchestrator
from app.core.agent.prompts_qimen import (
    build_qimen_chat_init_prompt,
    build_qimen_interpret_prompt,
)
from app.core.agent.service import AgentRunError
from app.core.knowledge.factory import get_knowledge_service
from app.core.qimen.engine import QimenEngine
from app.core.qimen.interpret_service import QimenInterpretService
from app.core.qimen.models import QimenInput
from app.core.rag.base import normalize_rag_excerpts
from app.core.rag.factory import build_rag_provider
from app.schemas.chat import ChatInitResponse
from app.schemas.qimen import (
    QimenChartRequest,
    QimenChartResponse,
    QimenChatInitRequest,
    QimenInterpretRequest,
    QimenInterpretResponse,
    QimenMethodInfo,
    QimenMethodsResponse,
    QimenRagSearchRequest,
    QimenRagSearchResponse,
)

router = APIRouter(prefix="/api/v1/qimen", tags=["qimen"])
logger = logging.getLogger(__name__)

_engine = QimenEngine()
_interpret = QimenInterpretService()


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


def _request_to_input(body: QimenChartRequest) -> QimenInput:
    return QimenInput(
        question=body.question,
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
        direction=body.direction,
        method=body.method,
        ju_override=body.juOverride,
    )


def _birth_profile_dict(body) -> dict[str, Any] | None:
    bp = getattr(body, "birthProfile", None)
    if bp is None:
        return None
    return bp.model_dump(exclude_none=True)


def _merge_birth_profile(chart: dict[str, Any], birth: dict[str, Any] | None) -> dict[str, Any]:
    if not birth:
        return chart
    out = dict(chart)
    out["birthProfile"] = birth
    return out


def _knowledge_hits_dict(chart: dict[str, Any]) -> list[dict[str, Any]]:
    knowledge = get_knowledge_service()
    if not knowledge.enabled:
        return []
    result = knowledge.lookup_qimen_chart(chart)
    return [hit.model_dump() for hit in result.hits]


@router.get("/methods", response_model=QimenMethodsResponse)
async def methods() -> QimenMethodsResponse:
    return QimenMethodsResponse(
        methods=[
            QimenMethodInfo(id="chaibu", label="拆补法", implemented=True),
            QimenMethodInfo(id="zhirun", label="置闰法", implemented=True),
            QimenMethodInfo(id="maoshan", label="茅山转盘", implemented=True),
        ]
    )


@router.post("/chart", response_model=QimenChartResponse)
async def chart(body: QimenChartRequest) -> QimenChartResponse:
    try:
        result = _engine.chart(_request_to_input(body)).to_dict()
        result = _merge_birth_profile(result, _birth_profile_dict(body))
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    return QimenChartResponse(chart=result)


@router.post("/rag/search", response_model=QimenRagSearchResponse)
async def rag_search(body: QimenRagSearchRequest) -> QimenRagSearchResponse:
    question = body.question or body.chart.get("input", {}).get("question", "")
    query = _interpret.build_query(body.chart, question)
    rag = build_rag_provider()
    try:
        excerpts = await rag.search(query, category=settings.qimen_rag_category)
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    return QimenRagSearchResponse(
        query=query,
        excerpts=normalize_rag_excerpts(excerpts),
    )


@router.post("/interpret", response_model=QimenInterpretResponse)
async def interpret(
    body: QimenInterpretRequest,
    request: Request,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
    _quota: str = Depends(consume_interpret_quota),
) -> QimenInterpretResponse:
    birth = _birth_profile_dict(body) or body.chart.get("birthProfile")
    chart = _merge_birth_profile(body.chart, birth)
    question = body.question or chart.get("input", {}).get("question", "")
    knowledge_hits = _knowledge_hits_dict(chart)

    if body.excerpts is not None:
        excerpts = normalize_rag_excerpts(body.excerpts)
    else:
        query = _interpret.build_query(chart, question)
        rag = build_rag_provider()
        try:
            excerpts = normalize_rag_excerpts(
                await rag.search(query, category=settings.qimen_rag_category)
            )
        except RuntimeError as err:
            raise HTTPException(status_code=503, detail=str(err)) from err

    summary: str | None = None
    agent_id: str | None = None
    if chat is not None and chat.enabled:
        prompt = build_qimen_interpret_prompt(
            chart,
            knowledge_hits,
            excerpts,
            birth_profile=birth,
            style=body.style,
        )
        try:
            summary, agent_id = await chat.interpret(prompt, body.model)
            if agent_id:
                session_store = get_session_store(request)
                session_store.bind(_interpret.chart_key(chart), agent_id)
        except (AgentRunError, RuntimeError) as err:
            logger.warning("qimen ai interpret failed: %s", err)

    payload = _interpret.build_response(
        chart,
        knowledge_hits,
        excerpts,
        summary=summary,
        agent_id=agent_id,
    )
    return QimenInterpretResponse(chart=chart, interpretation=payload)


@router.post("/chat/init", response_model=ChatInitResponse)
async def chat_init(
    body: QimenChatInitRequest,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
) -> ChatInitResponse:
    if chat is None:
        raise HTTPException(status_code=404, detail="chat not configured")
    birth = _birth_profile_dict(body) or body.chart.get("birthProfile")
    chart = _merge_birth_profile(body.chart, birth)
    hits = body.knowledgeHits if body.knowledgeHits is not None else _knowledge_hits_dict(chart)
    bootstrap = build_qimen_chat_init_prompt(
        chart,
        hits,
        body.excerpts or [],
        birth_profile=birth,
    )
    try:
        session_id = await chat.create_session()
        chat.set_bootstrap(session_id, bootstrap)
        chat.bind_chart(_interpret.chart_key(chart), session_id)
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    return ChatInitResponse(agentId=session_id)
