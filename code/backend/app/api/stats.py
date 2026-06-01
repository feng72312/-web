from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.stats.store import UsageStatsStore
from app.schemas.stats import StatsHeartbeatRequest, StatsOverviewResponse

router = APIRouter(prefix="/api/v1/stats", tags=["stats"])


def get_stats_store(request: Request) -> UsageStatsStore:
    store = getattr(request.app.state, "stats_store", None)
    if store is None:
        raise HTTPException(status_code=503, detail="stats store not initialized")
    return store


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


@router.get("/overview", response_model=StatsOverviewResponse)
async def stats_overview(
    store: UsageStatsStore = Depends(get_stats_store),
) -> StatsOverviewResponse:
    data = store.overview()
    return StatsOverviewResponse(**data)


@router.post("/heartbeat", response_model=StatsOverviewResponse)
async def stats_heartbeat(
    body: StatsHeartbeatRequest,
    request: Request,
    store: UsageStatsStore = Depends(get_stats_store),
) -> StatsOverviewResponse:
    data = store.heartbeat(
        body.visitorId.strip(),
        ip=_client_ip(request),
        user_agent=request.headers.get("user-agent"),
        count_visit=body.countVisit,
    )
    return StatsOverviewResponse(**data)
