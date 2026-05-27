from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from cursor_sdk import CursorAgentError
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.config import settings
from app.core.agent.prompts import build_chat_init_prompt, build_interpret_prompt
from app.core.agent.service import AgentRunError, CursorAgentService
from app.core.agent.session_store import AgentSessionStore
from app.core.analysis.registry import AnalysisRegistry, build_default_registry
from app.core.interpret.service import InterpretService
from app.core.paipan.engine import PaipanEngine
from app.core.paipan.luck_builder import build_liuri_by_year
from app.api.helpers import request_to_input
from app.core.paipan.rules import PaipanRules
from app.core.rag.factory import build_rag_provider
from app.schemas.chat import (
    ChatInitRequest,
    ChatInitResponse,
    ChatSendRequest,
    ChatSendResponse,
    ChatStatusResponse,
    RagSearchResponse,
)
from app.schemas.paipan import InterpretRequest, PaipanRequest, PaipanResponse

router = APIRouter(prefix="/api/v1", tags=["bazi"])
logger = logging.getLogger(__name__)

_registry: Optional[AnalysisRegistry] = None
_engine: Optional[PaipanEngine] = None
_interpret = InterpretService()
_session_store = AgentSessionStore()


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
    agent_service: CursorAgentService | None = Depends(get_agent_service),
) -> ChatStatusResponse:
    enabled = agent_service is not None and agent_service.enabled
    model = agent_service.model if agent_service else settings.cursor_model
    runtime = agent_service.runtime if agent_service else ""
    return ChatStatusResponse(enabled=enabled, model=model, runtime=runtime)


@router.post("/chat/send", response_model=ChatSendResponse)
async def chat_send(
    body: ChatSendRequest,
    agent_service: CursorAgentService | None = Depends(get_agent_service),
) -> ChatSendResponse:
    if agent_service is None:
        raise HTTPException(status_code=404, detail="cursor not configured")
    bootstrap = _session_store.pop_bootstrap(body.agentId)
    try:
        text, run_id = await agent_service.send_once(
            body.agentId, body.message, bootstrap=bootstrap
        )
    except CursorAgentError as err:
        raise HTTPException(status_code=503, detail=err.message) from err
    except AgentRunError as err:
        raise HTTPException(status_code=502, detail=f"run failed: {err.run_id}") from err
    return ChatSendResponse(agentId=body.agentId, runId=run_id, text=text)


@router.post("/chat/stream")
async def chat_stream(
    body: ChatSendRequest,
    agent_service: CursorAgentService | None = Depends(get_agent_service),
) -> StreamingResponse:
    if agent_service is None:
        raise HTTPException(status_code=404, detail="cursor not configured")

    async def event_generator():
        try:
            bootstrap = _session_store.pop_bootstrap(body.agentId)
            async for chunk, run_id in agent_service.send_stream(
                body.agentId, body.message, bootstrap=bootstrap
            ):
                if run_id is not None:
                    payload = {"type": "done", "runId": run_id}
                    yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
                    return
                if chunk:
                    payload = {"type": "delta", "text": chunk}
                    yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
        except CursorAgentError as err:
            payload = {"type": "error", "message": err.message}
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
        except AgentRunError as err:
            payload = {"type": "error", "message": f"run failed: {err.run_id}"}
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
    excerpts = await rag.search(query)
    return RagSearchResponse(query=query, excerpts=excerpts)


@router.post("/chat/init", response_model=ChatInitResponse)
async def chat_init(
    body: ChatInitRequest,
    agent_service: CursorAgentService | None = Depends(get_agent_service),
) -> ChatInitResponse:
    if agent_service is None:
        raise HTTPException(status_code=404, detail="cursor not configured")
    chart = dict(body.chart)
    if body.sections:
        chart["sections"] = body.sections
    interpret_service = InterpretService()
    bootstrap = build_chat_init_prompt(chart, [])
    try:
        agent_id = await agent_service.create_session()
        _session_store.set_bootstrap(agent_id, bootstrap)
        _session_store.bind(interpret_service.chart_key(chart), agent_id)
    except (CursorAgentError, AgentRunError, RuntimeError) as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    return ChatInitResponse(agentId=agent_id)


@router.post("/interpret")
async def interpret(
    body: InterpretRequest,
    engine: PaipanEngine = Depends(get_engine),
    registry: AnalysisRegistry = Depends(get_registry),
    agent_service: CursorAgentService | None = Depends(get_agent_service),
) -> Dict[str, Any]:
    chart, sections = _chart_from_request(body, engine, registry)

    interpret_service = InterpretService()
    query = interpret_service.build_query(chart)
    if body.excerpts is not None:
        excerpts = body.excerpts
    else:
        rag = build_rag_provider()
        excerpts = await rag.search(query)

    summary: str | None = None
    agent_id: str | None = None

    if agent_service is not None:
        prompt = build_interpret_prompt(chart, excerpts)
        try:
            summary, agent_id = await agent_service.interpret(prompt)
            _session_store.bind(interpret_service.chart_key(chart), agent_id)
        except (CursorAgentError, AgentRunError, RuntimeError) as err:
            logger.warning("cursor interpret failed, using fallback: %s", err)
        except Exception as err:
            logger.exception("cursor interpret unexpected error, using fallback")

    payload = interpret_service.build_response(
        chart,
        excerpts,
        summary=summary,
        agent_id=agent_id,
    )
    return {
        "chart": chart,
        "sections": sections,
        "interpretation": payload,
    }
