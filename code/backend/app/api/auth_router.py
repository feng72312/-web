from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException

from app.api.auth_deps import require_cloudbase_user
from app.api.quota_deps import get_quota_service, validate_device_id
from app.core.auth.cloudbase import CloudbaseUser
from app.schemas.auth import AuthMergeDeviceRequest, AuthMergeDeviceResponse, AuthProfileResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.get("/profile", response_model=AuthProfileResponse)
async def auth_profile(
    user: CloudbaseUser = Depends(require_cloudbase_user),
) -> AuthProfileResponse:
    return AuthProfileResponse(
        uid=user.uid,
        username=user.username,
        phone=user.phone,
    )


@router.post("/merge-device", response_model=AuthMergeDeviceResponse)
async def merge_device_quota(
    body: AuthMergeDeviceRequest,
    user: CloudbaseUser = Depends(require_cloudbase_user),
    x_device_id: str | None = Header(default=None, alias="X-Device-Id"),
    service=Depends(get_quota_service),
) -> AuthMergeDeviceResponse:
    raw_device = (body.deviceId or x_device_id or "").strip()
    if not raw_device:
        status = service.get_status(user.uid)
        return AuthMergeDeviceResponse(
            merged=False,
            creditBalance=int(status["creditBalance"]),
            freeRemaining=int(status["freeRemaining"]),
        )
    device_id = validate_device_id(raw_device)
    merged = service.merge_device_into_user(device_id, user.uid)
    status = service.get_status(user.uid)
    return AuthMergeDeviceResponse(
        merged=merged,
        creditBalance=int(status["creditBalance"]),
        freeRemaining=int(status["freeRemaining"]),
    )
