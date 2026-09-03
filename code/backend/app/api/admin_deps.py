from __future__ import annotations

import secrets

from fastapi import Depends, Header, HTTPException, Request

from app.config import settings
from app.core.admin.session import AdminSessionStore


def get_admin_session_store(request: Request) -> AdminSessionStore:
    store = getattr(request.app.state, "admin_session_store", None)
    if store is None:
        raise HTTPException(status_code=503, detail="admin session store not initialized")
    return store


def verify_admin_credentials(username: str, password: str) -> bool:
    expected_user = settings.admin_username.strip()
    expected_pass = settings.admin_password
    if not expected_pass:
        raise HTTPException(status_code=403, detail="admin disabled: set ADMIN_PASSWORD")
    if not expected_user:
        return False
    user_ok = secrets.compare_digest(username.strip(), expected_user)
    pass_ok = secrets.compare_digest(password, expected_pass)
    return user_ok and pass_ok


def require_admin(
    request: Request,
    authorization: str | None = Header(default=None),
    session_store: AdminSessionStore = Depends(get_admin_session_store),
) -> str:
    token = _extract_bearer_token(authorization)
    if not token or not session_store.validate(token):
        raise HTTPException(status_code=401, detail="admin authentication required")
    return token


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        return None
    token = authorization[len(prefix) :].strip()
    return token or None
