from __future__ import annotations

from fastapi import Depends, Header, HTTPException

from app.core.auth.cloudbase import CloudbaseUser, verify_access_token


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        return None
    token = authorization[len(prefix) :].strip()
    return token or None


async def require_cloudbase_user(
    authorization: str | None = Header(default=None),
) -> CloudbaseUser:
    token = _extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="authentication required")
    return await verify_access_token(token)


async def optional_cloudbase_user(
    authorization: str | None = Header(default=None),
) -> CloudbaseUser | None:
    token = _extract_bearer_token(authorization)
    if not token:
        return None
    try:
        return await verify_access_token(token)
    except HTTPException as exc:
        # Invalid or stale Bearer token: fall back to X-Device-Id for quota APIs.
        if exc.status_code == 401:
            return None
        raise
