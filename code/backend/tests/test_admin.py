from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.admin.session import AdminSessionStore
from app.core.quota.service import QuotaService
from app.core.quota.store import QuotaStore
from app.main import app


@pytest.fixture()
def admin_client(tmp_path: Path) -> TestClient:
    store = QuotaStore(tmp_path / "quota.db")
    app.state.quota_service = QuotaService(store)
    app.state.admin_session_store = AdminSessionStore(ttl_seconds=3600)
    return TestClient(app)


def test_admin_login_and_generate(admin_client: TestClient) -> None:
    bad = admin_client.post(
        "/api/v1/admin/login",
        json={"username": "fengge", "password": "wrong"},
    )
    assert bad.status_code == 401

    login = admin_client.post(
        "/api/v1/admin/login",
        json={"username": "fengge", "password": "1234567890.0aa"},
    )
    assert login.status_code == 200
    token = login.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    me = admin_client.get("/api/v1/admin/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["username"] == "fengge"

    gen = admin_client.post(
        "/api/v1/admin/keys/generate",
        headers=headers,
        json={"tier": 10, "count": 2, "note": "admin-test"},
    )
    assert gen.status_code == 200
    body = gen.json()
    assert body["count"] == 2
    assert len(body["keys"]) == 2
    assert body["keys"][0]["credits"] == 20

    listing = admin_client.get("/api/v1/admin/keys", headers=headers)
    assert listing.status_code == 200
    assert listing.json()["total"] >= 2


def test_admin_requires_auth(admin_client: TestClient) -> None:
    response = admin_client.get("/api/v1/admin/keys")
    assert response.status_code == 401
