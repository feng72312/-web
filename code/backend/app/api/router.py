from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends

from app.config import settings
from app.core.analysis.registry import AnalysisRegistry, build_default_registry
from app.core.interpret.service import InterpretService
from app.core.paipan.engine import PaipanEngine
from app.core.paipan.luck_builder import build_liuri_by_year
from app.api.helpers import request_to_input
from app.core.paipan.rules import PaipanRules
from app.core.rag.factory import build_rag_provider
from app.schemas.paipan import PaipanRequest, PaipanResponse

router = APIRouter(prefix="/api/v1", tags=["bazi"])

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


@router.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok", "app": settings.app_name}


@router.get("/modules")
async def list_modules(registry: AnalysisRegistry = Depends(get_registry)) -> Dict[str, Any]:
    return {"analysisModules": registry.list_modules()}


@router.post("/paipan", response_model=PaipanResponse)
async def paipan(
    body: PaipanRequest,
    engine: PaipanEngine = Depends(get_engine),
    registry: AnalysisRegistry = Depends(get_registry),
) -> PaipanResponse:
    result = engine.calculate(request_to_input(body))
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


@router.post("/interpret")
async def interpret(
    body: PaipanRequest,
    engine: PaipanEngine = Depends(get_engine),
    registry: AnalysisRegistry = Depends(get_registry),
) -> Dict[str, Any]:
    result = engine.calculate(request_to_input(body))
    chart = result.to_dict()
    sections = registry.run_all(chart)
    chart["sections"] = sections

    rag = build_rag_provider()
    interpret_service = InterpretService()
    query = interpret_service.build_query(chart)
    excerpts = await rag.search(query)
    payload = interpret_service.build_response(chart, excerpts)
    return {
        "chart": chart,
        "sections": sections,
        "interpretation": payload,
    }
