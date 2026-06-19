from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.interpret_deps import consume_interpret_quota
from app.config import settings
from app.core.agent.chat_orchestrator import ChatOrchestrator
from app.core.agent.prompts_tarot import (
    build_tarot_chat_init_prompt,
    build_tarot_interpret_prompt,
)
from app.core.agent.service import AgentRunError
from app.core.rag.base import normalize_rag_excerpts
from app.core.rag.factory import build_rag_provider
from app.core.tarot.decks import list_deck_cards, list_decks, list_spreads
from app.core.tarot.engine import TarotEngine
from app.core.tarot.interpret_service import TarotInterpretService
from app.core.tarot.models import TarotInput
from app.core.tarot.spread_matcher import suggest_spread
from app.schemas.chat import ChatInitResponse
from app.schemas.tarot import (
    TarotBuildRequest,
    TarotChatInitRequest,
    TarotDeckCardsResponse,
    TarotDecksResponse,
    TarotDrawRequest,
    TarotDrawResponse,
    TarotInterpretRequest,
    TarotInterpretResponse,
    TarotRagSearchRequest,
    TarotRagSearchResponse,
    TarotRevealRequest,
    TarotShuffleRequest,
    TarotShuffleResponse,
    TarotSpreadsResponse,
    TarotSuggestSpreadRequest,
    TarotSuggestSpreadResponse,
)

router = APIRouter(prefix="/api/v1/tarot", tags=["tarot"])
logger = logging.getLogger(__name__)

_engine = TarotEngine()
_interpret = TarotInterpretService()


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


def _request_to_input(body: TarotDrawRequest) -> TarotInput:
    return TarotInput(
        question=body.question,
        deck=body.deck,
        spread=body.spread,
        allow_reversed=body.allowReversed,
        seed=body.seed,
    )


@router.get("/decks", response_model=TarotDecksResponse)
async def decks() -> TarotDecksResponse:
    return TarotDecksResponse(decks=list_decks())


@router.get("/deck/{deck_id}/cards", response_model=TarotDeckCardsResponse)
async def deck_cards(deck_id: str) -> TarotDeckCardsResponse:
    try:
        cards = list_deck_cards(deck_id)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    return TarotDeckCardsResponse(cards=cards)


@router.get("/spreads", response_model=TarotSpreadsResponse)
async def spreads() -> TarotSpreadsResponse:
    return TarotSpreadsResponse(spreads=list_spreads())


@router.post("/suggest-spread", response_model=TarotSuggestSpreadResponse)
async def suggest(body: TarotSuggestSpreadRequest) -> TarotSuggestSpreadResponse:
    result = suggest_spread(body.question)
    return TarotSuggestSpreadResponse(**result)


@router.post("/draw", response_model=TarotDrawResponse)
async def draw(body: TarotDrawRequest) -> TarotDrawResponse:
    try:
        reading = _engine.draw(_request_to_input(body)).to_dict()
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    return TarotDrawResponse(reading=reading)


@router.post("/shuffle", response_model=TarotShuffleResponse)
async def shuffle(body: TarotShuffleRequest) -> TarotShuffleResponse:
    try:
        token, deck_size = _engine.shuffle(body.deck)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    return TarotShuffleResponse(sessionToken=token, deckSize=deck_size)


@router.post("/reveal", response_model=TarotDrawResponse)
async def reveal(body: TarotRevealRequest) -> TarotDrawResponse:
    try:
        reading = _engine.reveal(
            question=body.question,
            deck_id=body.deck,
            spread_id=body.spread,
            allow_reversed=body.allowReversed,
            seed=body.sessionToken,
            picks=body.picks,
        ).to_dict()
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    return TarotDrawResponse(reading=reading)


@router.post("/build", response_model=TarotDrawResponse)
async def build(body: TarotBuildRequest) -> TarotDrawResponse:
    try:
        reading = _engine.build(
            question=body.question,
            deck_id=body.deck,
            spread_id=body.spread,
            manual=[card.model_dump() for card in body.cards],
        ).to_dict()
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    return TarotDrawResponse(reading=reading)


@router.post("/rag/search", response_model=TarotRagSearchResponse)
async def rag_search(body: TarotRagSearchRequest) -> TarotRagSearchResponse:
    query = _interpret.build_query(body.reading, body.question)
    rag = build_rag_provider()
    try:
        excerpts = await rag.search(query, category=settings.tarot_rag_category)
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    excerpts = normalize_rag_excerpts(excerpts)
    return TarotRagSearchResponse(query=query, excerpts=excerpts)


@router.post("/interpret", response_model=TarotInterpretResponse)
async def interpret(
    body: TarotInterpretRequest,
    request: Request,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
    _quota: str = Depends(consume_interpret_quota),
) -> TarotInterpretResponse:
    reading = body.reading
    question = body.question or reading.get("input", {}).get("question", "")

    if body.excerpts is not None:
        excerpts = normalize_rag_excerpts(body.excerpts)
    else:
        query = _interpret.build_query(reading, question)
        rag = build_rag_provider()
        try:
            excerpts = await rag.search(query, category=settings.tarot_rag_category)
        except RuntimeError as err:
            raise HTTPException(status_code=503, detail=str(err)) from err
        excerpts = normalize_rag_excerpts(excerpts)

    summary: str | None = None
    agent_id: str | None = None
    if chat is not None and chat.enabled:
        prompt = build_tarot_interpret_prompt(reading, excerpts, style=body.style)
        try:
            summary, agent_id = await chat.interpret(prompt, body.model)
            if agent_id:
                session_store = get_session_store(request)
                session_store.bind(_interpret.reading_key(reading), agent_id)
        except (AgentRunError, RuntimeError) as err:
            logger.warning("tarot ai interpret failed: %s", err)

    payload = _interpret.build_response(
        reading,
        excerpts,
        summary=summary,
        agent_id=agent_id,
    )
    payload["riskTips"] = ["塔罗解读仅供参考, 不构成医疗/法律/投资决策依据."]
    payload["fusionMode"] = "question"
    payload["moduleId"] = "13"
    return TarotInterpretResponse(reading=reading, interpretation=payload)


@router.post("/chat/init", response_model=ChatInitResponse)
async def chat_init(
    body: TarotChatInitRequest,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
) -> ChatInitResponse:
    if chat is None:
        raise HTTPException(status_code=404, detail="chat not configured")
    bootstrap = build_tarot_chat_init_prompt(body.reading, body.excerpts or [])
    try:
        session_id = await chat.create_session()
        chat.set_bootstrap(session_id, bootstrap)
        chat.bind_chart(_interpret.reading_key(body.reading), session_id)
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    return ChatInitResponse(agentId=session_id)
