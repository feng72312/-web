from __future__ import annotations

import logging
from typing import Any

from cursor_sdk import CursorAgentError
from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.quota_deps import consume_ai_quota
from app.api.router import get_engine, get_registry
from app.config import settings
from app.core.agent.chat_orchestrator import ChatOrchestrator
from app.core.agent.prompts_hepan import (
    build_hepan_chat_init_prompt,
    build_hepan_interpret_prompt,
)
from app.core.agent.service import AgentRunError
from app.core.analysis.registry import AnalysisRegistry
from app.core.hepan.interpret_service import HepanInterpretService
from app.core.hepan.scene import SCENE_DEFAULT_DISCIPLINE, SCENE_DEFAULT_QUESTION, SCENE_LABELS
from app.core.hepan.service import HepanService
from app.core.paipan.engine import PaipanEngine
from app.core.rag.base import normalize_rag_excerpts
from app.core.rag.factory import build_rag_provider
from app.core.ziwei.engine import ZiweiEngine
from app.schemas.chat import ChatInitResponse
from app.schemas.hepan import (
    HepanChartRequest,
    HepanChartResponse,
    HepanChatInitRequest,
    HepanCrossNote,
    HepanInterpretRequest,
    HepanInterpretResponse,
    HepanPersonChartsOut,
    HepanRagSearchRequest,
    HepanRagSearchResponse,
    HepanSceneOption,
    HepanScenesResponse,
)

router = APIRouter(prefix="/api/v1/hepan", tags=["hepan"])
logger = logging.getLogger(__name__)

_ziwei_engine = ZiweiEngine()
_interpret = HepanInterpretService()


def _hepan_service(
    engine: PaipanEngine = Depends(get_engine),
    registry: AnalysisRegistry = Depends(get_registry),
) -> HepanService:
    return HepanService(engine, _ziwei_engine, registry)


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


def _result_to_response(result) -> HepanChartResponse:
    data = result.to_dict()
    return HepanChartResponse(
        scene=data["scene"],
        discipline=data["discipline"],
        personA=HepanPersonChartsOut(**data["personA"]),
        personB=HepanPersonChartsOut(**data["personB"]),
        crossNotes=[HepanCrossNote(**n) for n in data["crossNotes"]],
        summaryTags=data["summaryTags"],
        question=data["question"],
    )


@router.get("/scenes", response_model=HepanScenesResponse)
async def scenes() -> HepanScenesResponse:
    options = [
        HepanSceneOption(
            id=scene_id,
            label=SCENE_LABELS[scene_id],
            defaultDiscipline=SCENE_DEFAULT_DISCIPLINE[scene_id],
            defaultQuestion=SCENE_DEFAULT_QUESTION[scene_id],
        )
        for scene_id in ("romance", "marriage", "partnership")
    ]
    return HepanScenesResponse(scenes=options)


@router.post("/chart", response_model=HepanChartResponse)
async def chart(
    body: HepanChartRequest,
    service: HepanService = Depends(_hepan_service),
) -> HepanChartResponse:
    try:
        result = service.build_charts(body)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    return _result_to_response(result)


@router.post("/rag/search", response_model=HepanRagSearchResponse)
async def rag_search(body: HepanRagSearchRequest) -> HepanRagSearchResponse:
    hepan = body.hepan
    question = body.question or hepan.get("question") or ""
    discipline = hepan.get("discipline", "bazi")
    query = _interpret.build_query(hepan, question)
    rag = build_rag_provider()
    category = _interpret.rag_category(discipline)
    try:
        excerpts = await rag.search(query, category=category)
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    return HepanRagSearchResponse(
        query=query,
        excerpts=normalize_rag_excerpts(excerpts),
    )


@router.post("/interpret", response_model=HepanInterpretResponse)
async def interpret(
    body: HepanInterpretRequest,
    request: Request,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
    _quota: str = Depends(consume_ai_quota),
) -> HepanInterpretResponse:
    hepan = body.hepan
    question = body.question or hepan.get("question") or ""
    discipline = hepan.get("discipline", "bazi")
    knowledge_hits: list[dict[str, Any]] = []

    if body.excerpts is not None:
        excerpts = normalize_rag_excerpts(body.excerpts)
    else:
        query = _interpret.build_query(hepan, question)
        rag = build_rag_provider()
        try:
            excerpts = normalize_rag_excerpts(
                await rag.search(query, category=_interpret.rag_category(discipline))
            )
        except RuntimeError as err:
            raise HTTPException(status_code=503, detail=str(err)) from err

    summary: str | None = None
    agent_id: str | None = None
    if chat is not None and chat.enabled:
        prompt = build_hepan_interpret_prompt(
            hepan, knowledge_hits, excerpts, style=body.style
        )
        try:
            summary, agent_id = await chat.interpret(prompt, body.model)
            if agent_id:
                get_session_store(request).bind(HepanService.chart_key(hepan), agent_id)
        except (CursorAgentError, AgentRunError, RuntimeError) as err:
            logger.warning("hepan ai interpret failed: %s", err)

    payload = _interpret.build_response(
        hepan, knowledge_hits, excerpts, summary=summary, agent_id=agent_id
    )
    return HepanInterpretResponse(hepan=hepan, interpretation=payload)


@router.post("/chat/init", response_model=ChatInitResponse)
async def chat_init(
    body: HepanChatInitRequest,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
) -> ChatInitResponse:
    if chat is None:
        raise HTTPException(status_code=404, detail="chat not configured")
    bootstrap = build_hepan_chat_init_prompt(
        body.hepan,
        body.knowledgeHits or [],
        body.excerpts or [],
    )
    try:
        session_id = await chat.create_session()
        chat.set_bootstrap(session_id, bootstrap)
        chat.bind_chart(HepanService.chart_key(body.hepan), session_id)
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    return ChatInitResponse(agentId=session_id)
