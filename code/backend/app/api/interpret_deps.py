from __future__ import annotations

from typing import AsyncIterator

from fastapi import Depends, Header, HTTPException, Request

from app.api.auth_deps import optional_cloudbase_user
from app.api.quota_deps import get_quota_service, validate_device_id
from app.core.agent.models import tier_for_model
from app.core.auth.cloudbase import CloudbaseUser
from app.core.concurrency.interpret_limit import InterpretConcurrencyLimiter, InterpretQueueBusyError
from app.core.quota.service import QuotaExceededError


def get_interpret_limiter(request: Request) -> InterpretConcurrencyLimiter:
    limiter = getattr(request.app.state, "interpret_limiter", None)
    if limiter is None:
        raise HTTPException(status_code=503, detail="interpret limiter not initialized")
    return limiter


async def consume_interpret_quota(
    request: Request,
    user: CloudbaseUser | None = Depends(optional_cloudbase_user),
    x_model_id: str | None = Header(default=None, alias="X-Model-Id"),
    x_device_id: str | None = Header(default=None, alias="X-Device-Id"),
) -> AsyncIterator[str]:
    limiter = get_interpret_limiter(request)
    try:
        await limiter.acquire()
    except InterpretQueueBusyError as err:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "INTERPRET_QUEUED",
                "message": "当前解读人数较多, 请稍后重试",
                "active": err.active,
                "waiting": err.waiting,
                "maxConcurrent": err.max_concurrent,
            },
        ) from err
    try:
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
        yield account_id
    finally:
        limiter.release()
