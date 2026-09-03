from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.config import settings
from app.core.agent.ai_text import sanitize_ai_text
from app.core.agent.chat_orchestrator import ChatOrchestrator
from app.core.agent.chat_scope import is_chat_message_in_scope
from app.core.agent.models import default_model, list_models, tier_for_model
from app.core.agent.prompts import (
    GENERAL_CHAT_SCENARIOS,
    build_chat_init_prompt,
    build_general_chat_bootstrap,
    build_interpret_prompt,
)
from app.core.agent.prompts_fusion import build_fusion_chat_init_prompt
from app.core.agent.service import AgentRunError, CursorAgentService
from app.core.agent.session_store import AgentSessionStore
from app.core.analysis.registry import AnalysisRegistry, build_default_registry
from app.core.interpret.service import InterpretService
from app.core.interpret.segments import build_interpret_segments
from app.core.fusion.bazi_ziwei_service import BaziZiweiFusionService
from app.core.fusion.service import FusionInterpretService
from app.core.fusion.triple_service import TripleFusionInterpretService
from app.core.knowledge.factory import get_knowledge_service
from app.core.knowledge.models import CompressedContext
from app.core.knowledge.service import KnowledgeService
from app.core.knowledge.rag_fallback import fetch_on_demand_rag
from app.core.paipan.engine import PaipanEngine
from app.core.paipan.luck_builder import build_liuri_by_year
from app.api.helpers import request_to_input
from app.api.interpret_deps import consume_interpret_quota
from app.api.quota_deps import (
    consume_quota_for_account,
    resolve_quota_account_id,
)
from app.core.paipan.rules import PaipanRules
from app.core.rag.base import normalize_rag_excerpts
from app.core.rag.factory import build_rag_provider
from app.core.rag.status import probe_rag_service
from app.schemas.chat import (
    ChatGeneralInitRequest,
    ChatGeneralInitResponse,
    ChatFusionInitRequest,
    ChatFusionInitResponse,
    ChatHistoryResponse,
    ChatSeedInterpretRequest,
    ChatSeedInterpretResponse,
    ChatInitRequest,
    ChatInitResponse,
    ChatHistoryMessage,
    ChatModelInfo,
    ChatSendRequest,
    ChatSendResponse,
    ChatStatusResponse,
    RagSearchResponse,
)
from app.core.judgement.chain import BaziJudgementChain
from app.core.judgement.evidence import extract_rule_id_refs
from app.core.knowledge.evidence import knowledge_hits_to_evidence
from app.schemas.judgement import JudgementResponse, PaipanJudgementRequest
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


@dataclass
class BaziInterpretContext:
    chart: Dict[str, Any]
    sections: list[dict]
    excerpts: list[dict[str, str]]
    compressed: CompressedContext | None
    judgement_dict: dict[str, Any]
    tiered: dict[str, Any]
    prompt: str
    interpret_service: InterpretService
    knowledge: KnowledgeService


async def _prepare_bazi_interpret(
    body: InterpretRequest,
    chart: Dict[str, Any],
    sections: list[dict],
    request: Request,
) -> BaziInterpretContext:
    interpret_service = InterpretService()
    query = interpret_service.build_query(chart)
    knowledge = get_knowledge_service()
    compressed = None
    excerpts: list[dict[str, str]]

    judgement_chain = BaziJudgementChain(use_rag=settings.rag_provider == "http")
    judgement_report = await judgement_chain.run(chart, question=body.question or "")
    judgement_dict = judgement_report.to_dict()

    tiered = judgement_dict.get("tieredEvidence") or {}
    grounded_excerpts = (
        list(tiered.get("primaryEvidence") or [])
        + list(tiered.get("secondaryEvidence") or [])
    )

    if body.excerpts is not None:
        excerpts = normalize_rag_excerpts(body.excerpts)
    elif grounded_excerpts:
        excerpts = normalize_rag_excerpts(grounded_excerpts)
    elif settings.knowledge_use_legacy_rag_first or not knowledge.enabled:
        rag = build_rag_provider()
        try:
            excerpts = await rag.search(
                query,
                category=settings.rag_default_category,
                authority_tiers=["S", "A"],
                exclude_benchmark=True,
            )
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

    prompt = build_interpret_prompt(
        chart,
        compressed=compressed,
        rag_excerpts=excerpts,
        judgement_report=judgement_dict,
        style=body.style,
    )
    return BaziInterpretContext(
        chart=chart,
        sections=sections,
        excerpts=excerpts,
        compressed=compressed,
        judgement_dict=judgement_dict,
        tiered=tiered,
        prompt=prompt,
        interpret_service=interpret_service,
        knowledge=knowledge,
    )


def _finalize_bazi_interpret_payload(
    ctx: BaziInterpretContext,
    summary: str | None,
    agent_id: str | None,
) -> dict[str, Any]:
    payload = ctx.interpret_service.build_response(
        ctx.chart,
        ctx.excerpts,
        summary=summary,
        agent_id=agent_id,
    )
    if ctx.compressed is not None:
        payload["knowledge"] = {
            "lookupKeys": ctx.compressed.lookupKeys,
            "hitsCount": len(ctx.compressed.hits),
            "missingTopics": ctx.compressed.missingTopics,
            "autoAnswerSummary": ctx.compressed.autoAnswerSummary,
            "directAnswer": ctx.compressed.directAnswer,
        }
    payload["judgement"] = ctx.judgement_dict
    payload["ruleIdRefs"] = extract_rule_id_refs(ctx.judgement_dict)
    payload["tieredEvidence"] = ctx.tiered
    payload["tieredEvidenceSummary"] = ctx.judgement_dict.get("tieredEvidenceSummary") or {}
    payload["knowledgeEvidence"] = knowledge_hits_to_evidence(
        ctx.knowledge.resolve_for_chart(ctx.chart).hits if ctx.knowledge.enabled else [],
        limit=6,
    )
    arb = ctx.judgement_dict.get("arbitration") or {}
    payload["confidenceBand"] = arb.get("confidenceBand")
    payload["confidenceScore"] = arb.get("confidenceScore")
    segment_bundle = build_interpret_segments(
        str(payload.get("summary") or ""),
        ctx.judgement_dict,
        rule_id_refs=payload.get("ruleIdRefs") or [],
        confidence_band=payload.get("confidenceBand"),
    )
    payload["segments"] = segment_bundle["segments"]
    payload["segmentStats"] = segment_bundle["stats"]
    if segment_bundle.get("confidenceNote"):
        payload["confidenceNote"] = segment_bundle["confidenceNote"]
    if segment_bundle.get("confidenceBand"):
        payload["confidenceBand"] = segment_bundle["confidenceBand"]
    stats = segment_bundle.get("stats") or {}
    anchored_ratio = float(stats.get("anchoredRatio") or 0.0)
    if stats.get("total", 0) > 0 and anchored_ratio < 0.3:
        payload["confidenceBand"] = "weak"
        note = payload.get("confidenceNote") or ""
        extra = "解读段落锚点不足, 已强制下调置信度"
        payload["confidenceNote"] = f"{note}; {extra}".strip("; ").strip()
    return payload


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


@router.post("/paipan/judgement", response_model=JudgementResponse)
async def paipan_judgement(
    body: PaipanJudgementRequest,
    engine: PaipanEngine = Depends(get_engine),
    registry: AnalysisRegistry = Depends(get_registry),
) -> JudgementResponse:
    chart, sections = _chart_from_request(body, engine, registry)
    chain = BaziJudgementChain(use_rag=settings.rag_provider == "http")
    report = await chain.run(chart, question=body.question or "")
    payload = report.to_dict()
    payload["ruleIdRefs"] = extract_rule_id_refs(payload)
    return JudgementResponse(
        chart=chart,
        sections=sections,
        judgement=payload,
        tieredEvidenceSummary=payload.get("tieredEvidenceSummary") or {},
    )


@router.get("/liuri/{year}")
async def liuri(
    year: int,
    dayMaster: str,
    dayZhi: str = "",
    yearGan: str = "",
    yearZhi: str = "",
    monthZhi: str = "",
    gender: int = 1,
) -> Dict[str, Any]:
    from app.core.paipan.shensha import make_shen_sha_context

    ctx = make_shen_sha_context(
        day_gan=dayMaster,
        day_zhi=dayZhi,
        year_gan=yearGan,
        year_zhi=yearZhi,
        month_zhi=monthZhi,
        gender=gender,
    )
    return {"year": year, "months": build_liuri_by_year(year, ctx)}


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


@router.post("/chat/seed-interpretation", response_model=ChatSeedInterpretResponse)
async def chat_seed_interpretation(
    body: ChatSeedInterpretRequest,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
) -> ChatSeedInterpretResponse:
    if chat is None:
        raise HTTPException(status_code=404, detail="chat not configured")
    try:
        added = chat.seed_interpret_summaries(
            body.agentId,
            summary_plain=body.summaryPlain,
            summary_professional=body.summaryProfessional,
            model_id=body.model or "deepseek-chat",
        )
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    return ChatSeedInterpretResponse(agentId=body.agentId, added=added)


@router.post("/chat/send", response_model=ChatSendResponse)
async def chat_send(
    body: ChatSendRequest,
    request: Request,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
    account_id: str = Depends(resolve_quota_account_id),
    x_model_id: str | None = Header(default=None, alias="X-Model-Id"),
) -> ChatSendResponse:
    if chat is None:
        raise HTTPException(status_code=404, detail="chat not configured")
    allowed, refusal = is_chat_message_in_scope(body.message)
    if not allowed:
        raise HTTPException(status_code=400, detail=refusal)
    consume_quota_for_account(
        request,
        account_id,
        tier_name=tier_for_model(x_model_id or body.model),
    )
    try:
        text, run_id = await chat.send_once(body.agentId, body.message, body.model)
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    return ChatSendResponse(agentId=body.agentId, runId=run_id, text=text)


@router.post("/chat/stream")
async def chat_stream(
    body: ChatSendRequest,
    request: Request,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
    account_id: str = Depends(resolve_quota_account_id),
    x_model_id: str | None = Header(default=None, alias="X-Model-Id"),
) -> StreamingResponse:
    if chat is None:
        raise HTTPException(status_code=404, detail="chat not configured")
    allowed, refusal = is_chat_message_in_scope(body.message)
    if not allowed:
        raise HTTPException(status_code=400, detail=refusal)
    consume_quota_for_account(
        request,
        account_id,
        tier_name=tier_for_model(x_model_id or body.model),
    )

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


@router.get("/platform/pricing-tiers")
async def platform_pricing_tiers() -> dict[str, Any]:
    return {
        "tiers": [
            {
                "id": "free",
                "label": "免费层",
                "features": ["基础排盘", "有限解读次数", "单牌/三牌塔罗"],
            },
            {
                "id": "pro",
                "label": "进阶层",
                "features": [
                    "深度报告",
                    "跨术数联判",
                    "扩展追问额度",
                    "流式解读",
                ],
            },
            {
                "id": "expert",
                "label": "专业层",
                "features": [
                    "批量档案",
                    "专业视图",
                    "导出与复盘",
                    "案例资产库",
                ],
            },
        ]
    }


@router.get("/rag/status", response_model=RagStatusResponse)
async def rag_status() -> RagStatusResponse:
    from app.core.rag.status import load_index_report_summary

    service_ok, message, chunks = await probe_rag_service()
    report = load_index_report_summary()
    return RagStatusResponse(
        provider=settings.rag_provider,
        httpUrl=settings.rag_http_url or "",
        serviceOk=service_ok,
        serviceMessage=message,
        chunks=chunks,
        filesTotal=int(report.get("filesTotal", 0) or 0),
        chunksTotal=int(report.get("chunksTotal", 0) or 0),
        builtAt=report.get("builtAt"),
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


@router.post("/chat/init/general", response_model=ChatGeneralInitResponse)
async def chat_init_general(
    body: ChatGeneralInitRequest,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
) -> ChatGeneralInitResponse:
    if chat is None:
        raise HTTPException(status_code=404, detail="chat not configured")
    scenario = body.scenario.strip() if body.scenario else "general"
    if scenario not in GENERAL_CHAT_SCENARIOS:
        raise HTTPException(
            status_code=400,
            detail=f"invalid scenario: {scenario}",
        )
    title = (body.title or "").strip() or GENERAL_CHAT_SCENARIOS[scenario]
    bootstrap = build_general_chat_bootstrap(
        scenario,
        title=title,
        initial_prompt=(body.initialPrompt or "").strip() or None,
    )
    try:
        session_id = await chat.create_session()
        chat.set_bootstrap(session_id, bootstrap)
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    return ChatGeneralInitResponse(
        agentId=session_id,
        title=title,
        scenario=scenario,
    )


@router.post("/chat/init/fusion", response_model=ChatFusionInitResponse)
async def chat_init_fusion(
    body: ChatFusionInitRequest,
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
) -> ChatFusionInitResponse:
    if chat is None:
        raise HTTPException(status_code=404, detail="chat not configured")
    sources = [item.model_dump() for item in body.sources]
    bootstrap = build_fusion_chat_init_prompt(sources)
    labels = [item.moduleLabel.strip() for item in body.sources if item.moduleLabel.strip()]
    default_title = f"融合分析 · {' + '.join(labels)}" if labels else "融合分析"
    title = (body.title or "").strip() or default_title
    try:
        session_id = await chat.create_session()
        chat.set_bootstrap(session_id, bootstrap)
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    return ChatFusionInitResponse(
        agentId=session_id,
        title=title,
        scenario="review_result",
        sourceCount=len(body.sources),
    )


@router.post("/interpret")
async def interpret(
    body: InterpretRequest,
    request: Request,
    engine: PaipanEngine = Depends(get_engine),
    registry: AnalysisRegistry = Depends(get_registry),
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
    _quota: str = Depends(consume_interpret_quota),
) -> Dict[str, Any]:
    chart, sections = _chart_from_request(body, engine, registry)

    use_fusion = settings.fusion_enabled and body.fusion
    if use_fusion and body.fusionMode == "bazi_ziwei":
        bz_service = BaziZiweiFusionService()
        bz_fusion, agent_id = await bz_service.run(
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
        payload = bz_service.build_interpretation_payload(
            chart,
            bz_fusion,
            agent_id=agent_id,
        )
        return {
            "chart": chart,
            "sections": sections,
            "interpretation": payload,
        }
    if use_fusion and body.fusionMode == "triple":
        triple_service = TripleFusionInterpretService()
        triple, agent_id = await triple_service.run(
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
        payload = triple_service.build_interpretation_payload(
            chart,
            triple,
            agent_id=agent_id,
        )
        return {
            "chart": chart,
            "sections": sections,
            "interpretation": payload,
        }
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

    ctx = await _prepare_bazi_interpret(body, chart, sections, request)

    summary: str | None = None
    agent_id: str | None = None

    if (
        settings.knowledge_direct_answer_enabled
        and ctx.compressed is not None
        and ctx.compressed.directAnswer
        and not settings.knowledge_use_legacy_rag_first
    ):
        summary = ctx.compressed.directAnswer

    if summary is None and chat is not None and chat.enabled:
        try:
            summary, agent_id = await chat.interpret(ctx.prompt, body.model)
            if agent_id:
                session_store = get_session_store(request)
                session_store.bind(ctx.interpret_service.chart_key(chart), agent_id)
        except (AgentRunError, RuntimeError) as err:
            logger.warning("ai interpret failed, using fallback: %s", err)
        except Exception:
            logger.exception("ai interpret unexpected error, using fallback")

    return {
        "chart": chart,
        "sections": sections,
        "interpretation": _finalize_bazi_interpret_payload(ctx, summary, agent_id),
    }


@router.post("/interpret/stream")
async def interpret_stream(
    body: InterpretRequest,
    request: Request,
    engine: PaipanEngine = Depends(get_engine),
    registry: AnalysisRegistry = Depends(get_registry),
    chat: ChatOrchestrator | None = Depends(get_chat_orchestrator),
    _quota: str = Depends(consume_interpret_quota),
) -> StreamingResponse:
    if chat is None or not chat.enabled:
        raise HTTPException(status_code=404, detail="chat not configured")
    if body.fusion:
        raise HTTPException(status_code=400, detail="stream interpret supports fusion=false only")

    chart, sections = _chart_from_request(body, engine, registry)

    async def event_generator():
        yield f"data: {json.dumps({'type': 'stage', 'text': '排盘判定'}, ensure_ascii=False)}\n\n"
        try:
            ctx = await _prepare_bazi_interpret(body, chart, sections, request)
        except HTTPException as err:
            yield f"data: {json.dumps({'type': 'error', 'message': str(err.detail)}, ensure_ascii=False)}\n\n"
            return
        except Exception as err:
            yield f"data: {json.dumps({'type': 'error', 'message': str(err)}, ensure_ascii=False)}\n\n"
            return

        excerpt_count = len(ctx.excerpts)
        stage_text = f"检索典籍 ({excerpt_count} 条)" if excerpt_count else "检索典籍"
        yield f"data: {json.dumps({'type': 'stage', 'text': stage_text}, ensure_ascii=False)}\n\n"

        try:
            session_store = get_session_store(request)
            chart_key = ctx.interpret_service.chart_key(chart)
            agent_id = await chat.create_session()
            chat.set_bootstrap(agent_id, ctx.prompt)
            chat.bind_chart(chart_key, agent_id)
            session_store.bind(chart_key, agent_id)

            yield f"data: {json.dumps({'type': 'stage', 'text': 'AI 解读'}, ensure_ascii=False)}\n\n"
            full = ""
            async for chunk, run_id in chat.send_stream(agent_id, ctx.prompt, body.model):
                if run_id is not None:
                    payload = _finalize_bazi_interpret_payload(
                        ctx,
                        sanitize_ai_text(full),
                        agent_id,
                    )
                    done = {
                        "type": "done",
                        "chart": ctx.chart,
                        "sections": ctx.sections,
                        "interpretation": payload,
                    }
                    yield f"data: {json.dumps(done, ensure_ascii=False)}\n\n"
                    return
                if chunk:
                    full += chunk
                    yield f"data: {json.dumps({'type': 'delta', 'text': chunk}, ensure_ascii=False)}\n\n"
        except Exception as err:
            yield f"data: {json.dumps({'type': 'error', 'message': str(err)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
