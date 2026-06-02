from __future__ import annotations

from fastapi import Depends, Header, HTTPException, Request

from app.api.auth_deps import optional_cloudbase_user
from app.core.agent.models import tier_for_model
from app.core.auth.cloudbase import CloudbaseUser
from app.core.quota.service import QuotaExceededError, QuotaService


def get_quota_service(request: Request) -> QuotaService:
    service = getattr(request.app.state, "quota_service", None)
    if service is None:
        raise HTTPException(status_code=503, detail="quota service not initialized")
    return service


def validate_device_id(raw: str) -> str:
    device_id = raw.strip()
    if len(device_id) < 8 or len(device_id) > 64:
        raise HTTPException(
            status_code=400,
            detail="device id required (8-64 chars)",
        )
    return device_id


def resolve_device_id(
    x_device_id: str | None = Header(default=None, alias="X-Device-Id"),
) -> str:
    if not x_device_id:
        raise HTTPException(
            status_code=400,
            detail="X-Device-Id header required (8-64 chars)",
        )
    return validate_device_id(x_device_id)


def resolve_quota_account_id(
    user: CloudbaseUser | None = Depends(optional_cloudbase_user),
    x_device_id: str | None = Header(default=None, alias="X-Device-Id"),
) -> str:
    if user is not None:
        return user.uid
    if not x_device_id:
        raise HTTPException(
            status_code=400,
            detail="X-Device-Id header required when not logged in",
        )
    return validate_device_id(x_device_id)


def consume_ai_quota(
    request: Request,
    user: CloudbaseUser | None = Depends(optional_cloudbase_user),
    x_model_id: str | None = Header(default=None, alias="X-Model-Id"),
    x_device_id: str | None = Header(default=None, alias="X-Device-Id"),
) -> str:
    service = get_quota_service(request)
    if user is not None:
        account_id = user.uid
        if x_device_id:
            device_id = validate_device_id(x_device_id)
            if device_id != user.uid:
                service.merge_device_into_user(device_id, user.uid)
    else:
        if not x_device_id:
            raise HTTPException(status_code=401, detail="authentication required")
        account_id = validate_device_id(x_device_id)
    tier_name = tier_for_model(x_model_id)
    try:
        service.consume_one(account_id, tier_name=tier_name)
    except QuotaExceededError as err:
        raise HTTPException(
            status_code=402,
            detail={
                "code": "QUOTA_EXCEEDED",
                "message": "今日 AI 次数已用完, 请登录兑换秘钥或明日再试",
                "freeRemaining": err.free_remaining,
                "creditBalance": err.credit_balance,
            },
        ) from err
    return account_id
