from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.admin_deps import (
    get_admin_session_store,
    require_admin,
    verify_admin_credentials,
)
from app.api.quota_deps import get_quota_service
from app.config import settings
from app.core.admin.session import AdminSessionStore
from app.core.quota.service import QuotaService
from app.schemas.admin import (
    AdminGenerateKeysRequest,
    AdminGenerateKeysResponse,
    AdminGeneratedKeyItem,
    AdminLicenseKeyItem,
    AdminLicenseKeyListResponse,
    AdminLoginRequest,
    AdminLoginResponse,
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


@router.get("/keys", response_model=AdminLicenseKeyListResponse)
async def admin_list_keys(
    limit: int = 50,
    offset: int = 0,
    status: str | None = None,
    _token: str = Depends(require_admin),
    service: QuotaService = Depends(get_quota_service),
) -> AdminLicenseKeyListResponse:
    if status is not None and status not in {"unused", "redeemed"}:
        raise HTTPException(status_code=400, detail="status must be unused or redeemed")
    items, total = service.list_license_keys(limit=limit, offset=offset, status=status)
    return AdminLicenseKeyListResponse(
        items=[AdminLicenseKeyItem(**item) for item in items],
        total=total,
    )
