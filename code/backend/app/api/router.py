from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from cursor_sdk import CursorAgentError
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.config import settings
from app.core.agent.chat_orchestrator import ChatOrchestrator
from app.core.agent.models import default_model, list_models
from app.core.agent.prompts import build_chat_init_prompt, build_interpret_prompt
from app.core.agent.service import AgentRunError, CursorAgentService
from app.core.agent.session_store import AgentSessionStore
from app.core.analysis.registry import AnalysisRegistry, build_default_registry
from app.core.interpret.service import InterpretService
from app.core.fusion.service import FusionInterpretService
from app.core.knowledge.factory import get_knowledge_service
from app.core.knowledge.rag_fallback import fetch_on_demand_rag
from app.core.paipan.engine import PaipanEngine
from app.core.paipan.luck_builder import build_liuri_by_year
from app.api.helpers import request_to_input
from app.api.quota_deps import consume_ai_quota
from app.core.paipan.rules import PaipanRules
from app.core.rag.base import normalize_rag_excerpts
from app.core.rag.factory import build_rag_provider
from app.core.rag.status import probe_rag_service
from app.schemas.chat import (
    ChatHistoryResponse,
    ChatInitRequest,
    ChatInitResponse,
    ChatHistoryMessage,
    ChatModelInfo,
    ChatSendRequest,
    ChatSendResponse,
    ChatStatusResponse,
    RagSearchResponse,
)
from app.schemas.paipan import InterpretRequest, PaipanRequest, PaipanResponse
from app.schemas.rag_status import RagStatusResponse
from app.schemas.knowledge import (
    KnowledgeHitOut,
    KnowledgeLookupRequest,
    KnowledgeLookupResponse,
    KnowledgeStatusResponse,
)

router = APIRouter(prefix="/api/v1", tags=["bazi"])
logger = logging.getLogger(__name__)

_registry: Optional[AnalysisRegistry] = None
_engine: Optional[PaipanEngine] = None
_interpret = InterpretService()

def get_registry() -> AnalysisRegistry:
    global _registry
    if _registry is None:
        _registry = build_default_registry()
    return _registry


def get_engine() -> PaipanEngine:
    global _engine
    if _engine is None:
        rules = PaipanRules(
            sect=settings.paipan_sect,
            early_zishi_mode=settings.early_zishi_mode,
        )
        _engine = PaipanEngine(rules=rules)
    return _engine


def get_agent_service(request: Request) -> CursorAgentService | None:
    service = getattr(request.app.state, "agent_service", None)
    if service is None or not service.enabled:
        return None
    return service


def get_chat_orchestrator(request: Request) -> ChatOrchestrator | None:
    orchestrator = getattr(request.app.state, "chat_orchestrator", None)
    if orchestrator is None or not orchestrator.enabled:
        return None
    return orchestrator


def get_session_store(request: Request) -> AgentSessionStore:
    store = getattr(request.app.state, "session_store", None)
    if store is None:
        raise HTTPException(status_code=503, detail="session store not initialized")
    return store


def _hits_to_out(hits) -> list[KnowledgeHitOut]:
    rows: list[KnowledgeHitOut] = []
    for hit in hits:
        rows.append(
            KnowledgeHitOut(
                id=hit.id,
                topic=hit.topic,
                lookupKey=hit.lookupKey,
                summary=hit.summary,
                claims=[claim.model_dump() for claim in hit.claims],
                agreementLevel=hit.agreementLevel,
                safeAutoAnswer=hit.safeAutoAnswer,
                sourceTier=hit.sourceTier,
                domain=hit.domain,
            )
        )
    return rows


@router.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok", "app": settings.app_name}


@router.get("/modules")
async def list_modules(registry: AnalysisRegistry = Depends(get_registry)) -> Dict[str, Any]:
    return {"analysisModules": registry.list_modules()}


@router.post("/paipan/luck-timeline")
async def paipan_luck_timeline(
    body: PaipanRequest,
    engine: PaipanEngine = Depends(get_engine),
) -> Dict[str, Any]:
    result = engine.calculate(request_to_input(body), include_luck_timeline=True)
    timeline = result.luck_timeline
    if not timeline:
        raise HTTPException(status_code=500, detail="luck timeline build failed")
    return {"luckTimeline": timeline}


@router.post("/paipan", response_model=PaipanResponse)
async def paipan(
    body: PaipanRequest,
    engine: PaipanEngine = Depends(get_engine),
    registry: AnalysisRegistry = Depends(get_registry),
) -> PaipanResponse:
    result = engine.calculate(request_to_input(body), include_luck_timeline=False)
    chart = result.to_dict()
    sections = registry.run_all(chart)
    return PaipanResponse(
        chart=chart,
        sections=sections,
        modules=registry.list_modules(),
    )


@router.get("/liuri/{year}")
async def liuri(year: int, dayMaster: str) -> Dict[str, Any]:
    return {"year": year, "months": build_liuri_by_year(year, dayMaster)}


@router.get("/chat/status", response_model=ChatStatusResponse)
async def chat_status(
    request: Request,
    agent_service: CursorAgentService | None = Depends(get_agent_service),
) -> ChatStatusResponse:
    orchestrator = getattr(request.app.state, "chat_orchestrator", None)
    cursor_enabled = agent_service is not None and agent_service.enabled
    deepseek_enabled = orchestrator is not None and orchestrator.deepseek_enabled
    enabled = cursor_enabled or deepseek_enabled
    model = default_model(cursor_enabled=cursor_enabled, deepseek_enabled=deepseek_enabled)
    runtime = agent_service.runtime if agent_service else ""
    models = list_models(cursor_enabled=cursor_enabled, deepseek_enabled=deepseek_enabled)
    return ChatStatusResponse(
        enabled=enabled,
        model=model,
        runtime=runtime,
        models=[ChatModelInfo(**item) for item in models],
        cursorEnabled=cursor_enabled,
        deepseekEnabled=deepseek_enabled,
    )


@router.get("/chat/history/{agent_id}", response_model=ChatHistoryResponse)
async def chat_history(
    agent_id: str,
    store: AgentSessionStore = Depends(get_session_store),
) -> ChatHistoryResponse:
    rows = store.get_messages(agent_id)
    messages = [
        ChatHistoryMessage(role=item["role"], content=item["content"])
        for item in rows
        if item.get("role") in ("user", "assistant") and item.get("content")
    ]
    return ChatHistoryResponse(agentId=agent_id, messages=messages)


@router.post("/chat/send", response_model=ChatSendResponse)
async def chat_send(
    body: ChatSendRequest,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
    _quota: str = Depends(consume_ai_quota),
) -> ChatSendResponse:
    if chat is None:
        raise HTTPException(status_code=404, detail="chat not configured")
    try:
        text, run_id = await chat.send_once(body.agentId, body.message, body.model)
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    return ChatSendResponse(agentId=body.agentId, runId=run_id, text=text)


@router.post("/chat/stream")
async def chat_stream(
    body: ChatSendRequest,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
    _quota: str = Depends(consume_ai_quota),
) -> StreamingResponse:
    if chat is None:
        raise HTTPException(status_code=404, detail="chat not configured")

    async def event_generator():
        try:
            async for chunk, run_id in chat.send_stream(
                body.agentId, body.message, body.model
            ):
                if run_id is not None:
                    payload = {"type": "done", "runId": run_id}
                    yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
                    return
                if chunk:
                    payload = {"type": "delta", "text": chunk}
                    yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
        except RuntimeError as err:
            payload = {"type": "error", "message": str(err)}
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
        except Exception as err:
            payload = {"type": "error", "message": str(err)}
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


def _chart_from_request(
    body: PaipanRequest,
    engine: PaipanEngine,
    registry: AnalysisRegistry,
    *,
    include_luck_timeline: bool = False,
) -> tuple[dict[str, Any], list[dict]]:
    result = engine.calculate(
        request_to_input(body),
        include_luck_timeline=include_luck_timeline,
    )
    chart = result.to_dict()
    sections = registry.run_all(chart)
    chart["sections"] = sections
    return chart, sections


@router.get("/rag/status", response_model=RagStatusResponse)
async def rag_status() -> RagStatusResponse:
    service_ok, message, chunks = await probe_rag_service()
    return RagStatusResponse(
        provider=settings.rag_provider,
        httpUrl=settings.rag_http_url or "",
        serviceOk=service_ok,
        serviceMessage=message,
        chunks=chunks,
    )


@router.post("/rag/search", response_model=RagSearchResponse)
async def rag_search(
    body: PaipanRequest,
    engine: PaipanEngine = Depends(get_engine),
    registry: AnalysisRegistry = Depends(get_registry),
) -> RagSearchResponse:
    chart, _sections = _chart_from_request(body, engine, registry)
    interpret_service = InterpretService()
    query = interpret_service.build_query(chart)
    rag = build_rag_provider()
    try:
        excerpts = await rag.search(query, category=settings.rag_default_category)
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    excerpts = normalize_rag_excerpts(excerpts)
    return RagSearchResponse(query=query, excerpts=excerpts)


@router.get("/knowledge/status", response_model=KnowledgeStatusResponse)
async def knowledge_status() -> KnowledgeStatusResponse:
    service = get_knowledge_service()
    stats = service.store.stats()
    by_topic = stats.get("byTopic") or {}
    return KnowledgeStatusResponse(
        enabled=bool(stats.get("enabled")),
        dataDir=str(service.store.data_dir),
        manifestVersion=str(stats.get("manifestVersion") or ""),
        nodeCount=int(stats.get("nodeCount") or 0),
        entryCounts=by_topic,
        filesIndexed01=int(stats.get("01FilesIndexed") or 0),
        crossCategoryCount=int(stats.get("crossCategoryCount") or 0),
        loadError=stats.get("loadError"),
    )


@router.post("/knowledge/lookup", response_model=KnowledgeLookupResponse)
async def knowledge_lookup(
    body: KnowledgeLookupRequest,
    engine: PaipanEngine = Depends(get_engine),
    registry: AnalysisRegistry = Depends(get_registry),
) -> KnowledgeLookupResponse:
    chart, _sections = _chart_from_request(body, engine, registry)
    service = get_knowledge_service()
    if not service.enabled:
        return KnowledgeLookupResponse(
            lookupKeys={},
            hits=[],
            missingTopics=["tiaohou", "shishen", "ganzhi"],
            autoAnswerSummary=None,
            directAnswer=None,
        )
    result = service.lookup_chart(chart, topics=body.topics)
    return KnowledgeLookupResponse(
        lookupKeys=result.lookupKeys,
        hits=_hits_to_out(result.hits),
        missingTopics=result.missingTopics,
        autoAnswerSummary=result.autoAnswerSummary,
        directAnswer=result.directAnswer,
    )


@router.post("/chat/init", response_model=ChatInitResponse)
async def chat_init(
    body: ChatInitRequest,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
) -> ChatInitResponse:
    if chat is None:
        raise HTTPException(status_code=404, detail="chat not configured")
    chart = dict(body.chart)
    if body.sections:
        chart["sections"] = body.sections
    interpret_service = InterpretService()
    knowledge = get_knowledge_service()
    compressed = (
        knowledge.resolve_for_chart(chart) if knowledge.enabled else None
    )
    bootstrap = build_chat_init_prompt(chart, compressed=compressed)
    try:
        session_id = await chat.create_session()
        chat.set_bootstrap(session_id, bootstrap)
        chat.bind_chart(interpret_service.chart_key(chart), session_id)
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    return ChatInitResponse(agentId=session_id)


@router.post("/interpret")
async def interpret(
    body: InterpretRequest,
    request: Request,
    engine: PaipanEngine = Depends(get_engine),
    registry: AnalysisRegistry = Depends(get_registry),
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
    _quota: str = Depends(consume_ai_quota),
) -> Dict[str, Any]:
    chart, sections = _chart_from_request(body, engine, registry)

    use_fusion = settings.fusion_enabled and body.fusion
    if use_fusion:
        fusion_service = FusionInterpretService()
        fusion, agent_id = await fusion_service.run(
            body,
            chart,
            chat,
            question=body.question or None,
            preset_excerpts=body.excerpts,
            model_id=body.model,
            style=body.style,
        )
        if agent_id:
            session_store = get_session_store(request)
            interpret_service = InterpretService()
            session_store.bind(interpret_service.chart_key(chart), agent_id)
        payload = fusion_service.build_interpretation_payload(
            chart,
            fusion,
            agent_id=agent_id,
        )
        return {
            "chart": chart,
            "sections": sections,
            "interpretation": payload,
        }

    interpret_service = InterpretService()
    query = interpret_service.build_query(chart)
    knowledge = get_knowledge_service()
    compressed = None
    excerpts: list[dict[str, str]]

    if body.excerpts is not None:
        excerpts = normalize_rag_excerpts(body.excerpts)
    elif settings.knowledge_use_legacy_rag_first or not knowledge.enabled:
        rag = build_rag_provider()
        try:
            excerpts = await rag.search(query, category=settings.rag_default_category)
        except RuntimeError as err:
            raise HTTPException(status_code=503, detail=str(err)) from err
        excerpts = normalize_rag_excerpts(excerpts)
    else:
        compressed = knowledge.resolve_for_chart(chart)
        excerpts = []
        if settings.knowledge_rag_fallback and compressed.missingTopics:
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
            except RuntimeError as err:
                logger.warning("knowledge rag fallback failed: %s", err)

    summary: str | None = None
    agent_id: str | None = None

    if (
        settings.knowledge_direct_answer_enabled
        and compressed is not None
        and compressed.directAnswer
        and not settings.knowledge_use_legacy_rag_first
    ):
        summary = compressed.directAnswer

    if summary is None and chat is not None and chat.enabled:
        prompt = build_interpret_prompt(
            chart,
            compressed=compressed,
            rag_excerpts=excerpts,
            style=body.style,
        )
        try:
            summary, agent_id = await chat.interpret(prompt, body.model)
            if agent_id:
                session_store = get_session_store(request)
                session_store.bind(interpret_service.chart_key(chart), agent_id)
        except (CursorAgentError, AgentRunError, RuntimeError) as err:
            logger.warning("ai interpret failed, using fallback: %s", err)
        except Exception:
            logger.exception("ai interpret unexpected error, using fallback")

    payload = interpret_service.build_response(
        chart,
        excerpts,
        summary=summary,
        agent_id=agent_id,
    )
    if compressed is not None:
        payload["knowledge"] = {
            "lookupKeys": compressed.lookupKeys,
            "hitsCount": len(compressed.hits),
            "missingTopics": compressed.missingTopics,
            "autoAnswerSummary": compressed.autoAnswerSummary,
            "directAnswer": compressed.directAnswer,
        }
    return {
        "chart": chart,
        "sections": sections,
        "interpretation": payload,
    }
