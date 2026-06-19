from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.interpret_deps import consume_interpret_quota
from app.config import settings
from app.core.agent.chat_orchestrator import ChatOrchestrator
from app.core.agent.prompts_utils import (
    build_cewen_interpret_prompt,
    build_jiemeng_interpret_prompt,
    build_naming_interpret_prompt,
    build_zhuge_interpret_prompt,
)
from app.core.agent.service import AgentRunError
from app.core.rag.base import normalize_rag_excerpts
from app.core.rag.factory import build_rag_provider
from app.core.utils.interpret_service import UtilsInterpretService
from app.core.utils.jiemeng_index import search_dreams
from app.core.utils.naming_engine import analyze_name
from app.core.utils.shuowen_index import lookup_chars
from app.core.utils.zhuge_engine import divine_three_chars
from app.schemas.utils import (
    CewenRagSearchRequest,
    JiemengSearchRequest,
    JiemengSearchResponse,
    NamingAnalyzeRequest,
    NamingAnalyzeResponse,
    NamingLookupRequest,
    NamingLookupResponse,
    NamingRagSearchRequest,
    UtilsInterpretRequest,
    UtilsInterpretResponse,
    UtilsRagSearchResponse,
    ZhugeDivineRequest,
    ZhugeDivineResponse,
)

router = APIRouter(prefix="/api/v1/utils", tags=["utils"])
logger = logging.getLogger(__name__)
_interpret = UtilsInterpretService()


async def _search_utils_rag(query: str, *, required: bool) -> list[dict[str, str]]:
    rag = build_rag_provider()
    try:
        raw = await rag.search(query, category=settings.utils_rag_category)
        return normalize_rag_excerpts(raw)
    except RuntimeError as err:
        if required:
            raise HTTPException(status_code=503, detail=str(err)) from err
        logger.warning("utils rag unavailable, interpret without excerpts: %s", err)
        return []


def get_chat_orchestrator(request: Request) -> ChatOrchestrator | None:
    orchestrator = getattr(request.app.state, "chat_orchestrator", None)
    if orchestrator is None or not orchestrator.enabled:
        return None
    return orchestrator


@router.post("/zhuge/divine", response_model=ZhugeDivineResponse)
async def zhuge_divine(body: ZhugeDivineRequest) -> ZhugeDivineResponse:
    chars = "".join(body.chars.split())
    if len(chars) != 3:
        raise HTTPException(status_code=400, detail="zhuge requires exactly three characters")
    try:
        result = divine_three_chars(chars, strokes=body.strokes)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    return ZhugeDivineResponse(**result)


@router.post("/jiemeng/search", response_model=JiemengSearchResponse)
async def jiemeng_search(body: JiemengSearchRequest) -> JiemengSearchResponse:
    try:
        matches = search_dreams(body.dream, limit=body.limit)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    from app.schemas.utils import JiemengMatch

    return JiemengSearchResponse(
        dream=body.dream,
        matches=[JiemengMatch(**row) for row in matches],
    )


@router.post("/cewen/rag/search", response_model=UtilsRagSearchResponse)
async def cewen_rag_search(body: CewenRagSearchRequest) -> UtilsRagSearchResponse:
    query = _interpret.build_cewen_query(body.chars, body.question)
    excerpts = await _search_utils_rag(query, required=True)
    return UtilsRagSearchResponse(query=query, excerpts=excerpts)


@router.post("/naming/lookup", response_model=NamingLookupResponse)
async def naming_lookup(body: NamingLookupRequest) -> NamingLookupResponse:
    chars = "".join(ch for ch in body.chars if "\u4e00" <= ch <= "\u9fff")
    if not chars:
        raise HTTPException(status_code=400, detail="chars required")
    return NamingLookupResponse(chars=chars, entries=lookup_chars(chars))


@router.post("/naming/analyze", response_model=NamingAnalyzeResponse)
async def naming_analyze(body: NamingAnalyzeRequest) -> NamingAnalyzeResponse:
    try:
        birth = body.birth.model_dump() if body.birth else None
        analysis = analyze_name(
            surname=body.surname,
            given_name=body.givenName,
            stroke_overrides=body.strokeOverrides,
            birth=birth,
        )
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    return NamingAnalyzeResponse(analysis=analysis)


@router.post("/naming/rag/search", response_model=UtilsRagSearchResponse)
async def naming_rag_search(body: NamingRagSearchRequest) -> UtilsRagSearchResponse:
    try:
        birth = body.birth.model_dump() if body.birth else None
        analysis = analyze_name(
            surname=body.surname,
            given_name=body.givenName,
            stroke_overrides=body.strokeOverrides,
            birth=birth,
        )
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    query = _interpret.build_naming_query(analysis, body.question)
    excerpts = await _search_utils_rag(query, required=True)
    return UtilsRagSearchResponse(query=query, excerpts=excerpts)


@router.post("/zhuge/rag/search", response_model=UtilsRagSearchResponse)
async def zhuge_rag_search(body: ZhugeDivineRequest) -> UtilsRagSearchResponse:
    try:
        result = divine_three_chars(body.chars, strokes=body.strokes)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    query = _interpret.build_zhuge_query(result, body.question)
    excerpts = await _search_utils_rag(query, required=True)
    return UtilsRagSearchResponse(query=query, excerpts=excerpts)


@router.post("/jiemeng/rag/search", response_model=UtilsRagSearchResponse)
async def jiemeng_rag_search(body: JiemengSearchRequest) -> UtilsRagSearchResponse:
    try:
        matches = search_dreams(body.dream, limit=body.limit)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    query = _interpret.build_jiemeng_query(matches, body.dream)
    excerpts = await _search_utils_rag(query, required=True)
    return UtilsRagSearchResponse(query=query, excerpts=excerpts)


@router.post("/interpret", response_model=UtilsInterpretResponse)
async def interpret(
    body: UtilsInterpretRequest,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
    _quota: str = Depends(consume_interpret_quota),
) -> UtilsInterpretResponse:
    tool = body.tool.strip().lower()
    payload = dict(body.payload)
    question = body.question or ""

    if body.excerpts is not None:
        excerpts = normalize_rag_excerpts(body.excerpts)
    else:
        if tool == "zhuge":
            query = _interpret.build_zhuge_query(payload, question)
        elif tool == "jiemeng":
            matches = payload.get("matches") or []
            query = _interpret.build_jiemeng_query(matches, question or payload.get("dream", ""))
        elif tool == "cewen":
            query = _interpret.build_cewen_query(payload.get("chars", ""), question)
        elif tool == "naming":
            query = _interpret.build_naming_query(payload.get("analysis") or {}, question)
        else:
            raise HTTPException(status_code=400, detail=f"unknown tool: {tool}")
        excerpts = await _search_utils_rag(query, required=False)

    if chat is None or not chat.enabled:
        raise HTTPException(
            status_code=503,
            detail="AI 解读未配置, 请在 backend/.env 配置 BAZI_DEEPSEEK_API_KEY 或 BAZI_CURSOR_API_KEY 后重启后端",
        )

    if tool == "zhuge":
        prompt = build_zhuge_interpret_prompt(payload, excerpts, style=body.style)
    elif tool == "jiemeng":
        prompt = build_jiemeng_interpret_prompt(
            question or payload.get("dream", ""),
            payload.get("matches") or [],
            excerpts,
            style=body.style,
        )
    elif tool == "cewen":
        prompt = build_cewen_interpret_prompt(
            payload.get("chars", ""),
            question,
            excerpts,
            style=body.style,
        )
    elif tool == "naming":
        prompt = build_naming_interpret_prompt(
            payload.get("analysis") or {},
            question,
            excerpts,
            style=body.style,
        )
    else:
        raise HTTPException(status_code=400, detail=f"unknown tool: {tool}")

    try:
        summary, agent_id = await chat.interpret(prompt, body.model)
    except (AgentRunError, RuntimeError) as err:
        logger.warning("utils ai interpret failed: %s", err)
        raise HTTPException(status_code=503, detail=f"AI 解读失败: {err}") from err

    if not summary:
        raise HTTPException(status_code=503, detail="AI 解读未返回内容, 请稍后重试")

    interpretation = _interpret.build_response(
        tool=tool,
        payload=payload,
        excerpts=excerpts,
        summary=summary,
        agent_id=agent_id,
    )
    return UtilsInterpretResponse(interpretation=interpretation)
