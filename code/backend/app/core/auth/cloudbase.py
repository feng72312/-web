from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx
from fastapi import HTTPException

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CloudbaseUser:
    uid: str
    username: str | None = None
    phone: str | None = None


def _auth_api_base() -> str:
    """CloudBase Auth HTTP API (same host as @cloudbase/js-sdk)."""
    env_id = settings.cloudbase_env_id.strip()
    if not env_id:
        raise HTTPException(status_code=503, detail="cloudbase env not configured")
    region = settings.cloudbase_region.strip() or "ap-shanghai"
    return f"https://{env_id}.{region}.tcb-api.tencentcloudapi.com"


def _parse_user_payload(data: object) -> CloudbaseUser:
    if not isinstance(data, dict):
        raise HTTPException(status_code=401, detail="invalid auth response")
    nested = data.get("user")
    if isinstance(nested, dict):
        payload = nested
    else:
        payload = data
    uid = payload.get("id") or payload.get("sub") or payload.get("uid")
    if not uid or not isinstance(uid, str):
        raise HTTPException(status_code=401, detail="invalid auth response")
    if uid.strip() in {"anon", "anonymous"}:
        raise HTTPException(status_code=401, detail="anonymous session not allowed")
    username = payload.get("username")
    if username is not None and not isinstance(username, str):
        username = None
    phone = payload.get("phone")
    if phone is not None and not isinstance(phone, str):
        phone = None
    meta = payload.get("user_metadata")
    if isinstance(meta, dict) and not username:
        raw_name = meta.get("username")
        if isinstance(raw_name, str):
            username = raw_name
    return CloudbaseUser(uid=uid.strip(), username=username, phone=phone)


async def verify_access_token(access_token: str) -> CloudbaseUser:
    token = access_token.strip()
    if not token:
        raise HTTPException(status_code=401, detail="authentication required")
    url = f"{_auth_api_base()}/auth/v1/user/me"
    env_id = settings.cloudbase_env_id.strip()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                url,
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-Project-Id": env_id,
                },
            )
    except httpx.HTTPError as err:
        logger.warning("cloudbase auth request failed: %s", err)
        raise HTTPException(status_code=503, detail="auth service unavailable") from err
    if response.status_code == 401:
        raise HTTPException(status_code=401, detail="invalid or expired token")
    if response.status_code >= 400:
        logger.warning("cloudbase auth status=%s body=%s", response.status_code, response.text[:200])
        raise HTTPException(status_code=401, detail="authentication failed")
    try:
        data = response.json()
    except ValueError as err:
        raise HTTPException(status_code=401, detail="invalid auth response") from err
    return _parse_user_payload(data)
