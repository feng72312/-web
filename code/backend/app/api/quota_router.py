from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.quota_deps import get_quota_service, validate_device_id
from app.core.quota.service import InvalidLicenseKeyError, PhoneAlreadyBoundError
from app.core.quota.persistence import inspect_sqlite_path
from app.core.stats.store import resolve_stats_db_path
from app.core.quota.store import resolve_quota_db_path
from app.schemas.quota import (
    QuotaBindPhoneRequest,
    QuotaRedeemRequest,
    QuotaRedeemResponse,
    QuotaStatusResponse,
)
from app.schemas.quota_persistence import QuotaPersistenceResponse

router = APIRouter(prefix="/api/v1/quota", tags=["quota"])


@router.get("/persistence", response_model=QuotaPersistenceResponse)
async def quota_persistence() -> QuotaPersistenceResponse:
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
    return QuotaPersistenceResponse(
        quotaDbPath=str(quota_path),
        statsDbPath=str(stats_path),
        quota=quota_info,
        stats=stats_info,
        likelyPersistent=likely,
        warning=warning,
    )


@router.get("/status", response_model=QuotaStatusResponse)
async def quota_status(
    deviceId: str,
    service=Depends(get_quota_service),
) -> QuotaStatusResponse:
    device_id = validate_device_id(deviceId)
    data = service.get_status(device_id)
    return QuotaStatusResponse(**data)


@router.post("/redeem", response_model=QuotaRedeemResponse)
async def quota_redeem(
    body: QuotaRedeemRequest,
    service=Depends(get_quota_service),
) -> QuotaRedeemResponse:
    try:
        result = service.redeem_key(body.deviceId.strip(), body.key)
    except InvalidLicenseKeyError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    return QuotaRedeemResponse(**result)


@router.post("/bind-phone")
async def quota_bind_phone(
    body: QuotaBindPhoneRequest,
    service=Depends(get_quota_service),
) -> dict[str, str]:
    try:
        service.bind_phone(body.deviceId.strip(), body.phone)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    except PhoneAlreadyBoundError as err:
        raise HTTPException(status_code=409, detail=str(err)) from err
    return {"status": "ok", "phone": body.phone.strip()}
