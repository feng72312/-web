from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.admin_deps import (
    get_admin_session_store,
    require_admin,
    verify_admin_credentials,
)
from app.api.quota_deps import get_quota_service
from app.api.stats import get_stats_store
from app.config import settings
from app.core.admin.session import AdminSessionStore
from app.core.quota.persistence import inspect_sqlite_path
from app.core.quota.service import QuotaService
from app.core.quota.store import resolve_quota_db_path
from app.core.stats.store import UsageStatsStore, resolve_stats_db_path
from app.schemas.admin import (
    AdminGenerateKeysRequest,
    AdminGenerateKeysResponse,
    AdminGeneratedKeyItem,
    AdminLicenseKeyItem,
    AdminLicenseKeyListResponse,
    AdminLicenseSummary,
    AdminLoginRequest,
    AdminLoginResponse,
    AdminOverviewResponse,
    AdminPersistenceSummary,
    AdminUsageStatsSummary,
)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(
    body: AdminLoginRequest,
    session_store: AdminSessionStore = Depends(get_admin_session_store),
) -> AdminLoginResponse:
    if not verify_admin_credentials(body.username, body.password):
        raise HTTPException(status_code=401, detail="invalid username or password")
    token = session_store.create()
    return AdminLoginResponse(
        token=token,
        username=settings.admin_username.strip(),
        expiresInSeconds=settings.admin_session_ttl_hours * 3600,
    )


@router.post("/logout")
async def admin_logout(
    token: str = Depends(require_admin),
    session_store: AdminSessionStore = Depends(get_admin_session_store),
) -> dict[str, str]:
    session_store.revoke(token)
    return {"status": "ok"}


@router.get("/me")
async def admin_me(
    token: str = Depends(require_admin),
) -> dict[str, str]:
    return {"username": settings.admin_username.strip(), "status": "ok"}


@router.post("/keys/generate", response_model=AdminGenerateKeysResponse)
async def admin_generate_keys(
    body: AdminGenerateKeysRequest,
    _token: str = Depends(require_admin),
    service: QuotaService = Depends(get_quota_service),
) -> AdminGenerateKeysResponse:
    generated = service.generate_license_keys(body.tier, body.count, body.note)
    keys = [
        AdminGeneratedKeyItem(
            key=str(item["key"]),
            tier=int(item["tier"]),
            credits=int(item["credits"]),
        )
        for item in generated
    ]
    return AdminGenerateKeysResponse(keys=keys, count=len(keys))


@router.get("/overview", response_model=AdminOverviewResponse)
async def admin_overview(
    _token: str = Depends(require_admin),
    service: QuotaService = Depends(get_quota_service),
    stats_store: UsageStatsStore = Depends(get_stats_store),
) -> AdminOverviewResponse:
    license_summary = service.license_key_summary()
    usage = stats_store.overview()
    quota_path = resolve_quota_db_path()
    stats_path = resolve_stats_db_path()
    quota_info = inspect_sqlite_path(quota_path)
    stats_info = inspect_sqlite_path(stats_path)
    likely = bool(quota_info["likelyPersistent"] and stats_info["likelyPersistent"])
    warning = None
    if not likely:
        warning = (
            "quota data is not on persistent COS storage; "
            "redeploy or container restart resets free usage and license keys"
        )
    return AdminOverviewResponse(
        licenseSummary=AdminLicenseSummary(**license_summary),
        usageStats=AdminUsageStatsSummary(
            online=int(usage["online"]),
            totalVisitors=int(usage["total"]),
            visits=int(usage["visits"]),
        ),
        persistence=AdminPersistenceSummary(
            likelyPersistent=likely,
            warning=warning,
            quotaDbPath=str(quota_path),
            statsDbPath=str(stats_path),
        ),
    )


@router.get("/keys", response_model=AdminLicenseKeyListResponse)
async def admin_list_keys(
    limit: int = 20,
    offset: int = 0,
    status: str | None = None,
    tier: int | None = None,
    note: str | None = None,
    redeemedDeviceId: str | None = None,
    createdFrom: float | None = None,
    createdTo: float | None = None,
    _token: str = Depends(require_admin),
    service: QuotaService = Depends(get_quota_service),
) -> AdminLicenseKeyListResponse:
    if status is not None and status not in {"unused", "redeemed"}:
        raise HTTPException(status_code=400, detail="status must be unused or redeemed")
    if tier is not None and tier not in {10, 20, 50, 100}:
        raise HTTPException(status_code=400, detail="tier must be 10, 20, 50, or 100")
    items, total = service.list_license_keys(
        limit=limit,
        offset=offset,
        status=status,
        tier=tier,
        note=(note or "").strip() or None,
        redeemed_device_id=(redeemedDeviceId or "").strip() or None,
        created_from=createdFrom,
        created_to=createdTo,
    )
    return AdminLicenseKeyListResponse(
        items=[AdminLicenseKeyItem(**item) for item in items],
        total=total,
    )
