from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.core.admin.session import AdminSessionStore
from app.core.quota.service import QuotaService
from app.core.quota.store import QuotaStore
from app.core.stats.store import UsageStatsStore
from app.main import app


@pytest.fixture()
def admin_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(settings, "admin_password", "test-admin")
    store = QuotaStore(tmp_path / "quota.db")
    app.state.quota_service = QuotaService(store)
    app.state.stats_store = UsageStatsStore(tmp_path / "usage_stats.db")
    app.state.admin_session_store = AdminSessionStore(ttl_seconds=3600)
    return TestClient(app)


def _login_headers(client: TestClient) -> dict[str, str]:
    login = client.post(
        "/api/v1/admin/login",
        json={"username": "fengge", "password": "test-admin"},
    )
    assert login.status_code == 200
    token = login.json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_admin_login_and_generate(admin_client: TestClient) -> None:
    bad = admin_client.post(
        "/api/v1/admin/login",
        json={"username": "fengge", "password": "wrong"},
    )
    assert bad.status_code == 401

    headers = _login_headers(admin_client)

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

    overview = admin_client.get("/api/v1/admin/overview")
    assert overview.status_code == 401


def test_admin_overview(admin_client: TestClient) -> None:
    headers = _login_headers(admin_client)

    before = admin_client.get("/api/v1/admin/overview", headers=headers)
    assert before.status_code == 200
    before_body = before.json()
    assert before_body["licenseSummary"]["totalKeys"] == 0

    gen = admin_client.post(
        "/api/v1/admin/keys/generate",
        headers=headers,
        json={"tier": 20, "count": 1, "note": "overview-note"},
    )
    assert gen.status_code == 200

    after = admin_client.get("/api/v1/admin/overview", headers=headers)
    assert after.status_code == 200
    after_body = after.json()
    assert after_body["licenseSummary"]["totalKeys"] == 1
    assert after_body["licenseSummary"]["unusedKeys"] == 1
    assert after_body["licenseSummary"]["totalCreditsIssued"] == 50
    assert after_body["usageStats"]["online"] >= 0
    assert "quotaDbPath" in after_body["persistence"]


def test_admin_list_filters_and_pagination(admin_client: TestClient) -> None:
    headers = _login_headers(admin_client)

    for tier, note in ((10, "buyer-a"), (20, "buyer-b"), (10, "buyer-a-extra")):
        response = admin_client.post(
            "/api/v1/admin/keys/generate",
            headers=headers,
            json={"tier": tier, "count": 1, "note": note},
        )
        assert response.status_code == 200

    unused = admin_client.get(
        "/api/v1/admin/keys",
        headers=headers,
        params={"status": "unused", "tier": 10, "note": "buyer-a"},
    )
    assert unused.status_code == 200
    unused_body = unused.json()
    assert unused_body["total"] == 2
    assert len(unused_body["items"]) == 2
    assert all(item["tierLabel"] == "10" for item in unused_body["items"])

    page_one = admin_client.get(
        "/api/v1/admin/keys",
        headers=headers,
        params={"limit": 2, "offset": 0},
    )
    page_two = admin_client.get(
        "/api/v1/admin/keys",
        headers=headers,
        params={"limit": 2, "offset": 2},
    )
    assert page_one.status_code == 200
    assert page_two.status_code == 200
    assert page_one.json()["total"] >= 3
    assert len(page_one.json()["items"]) == 2
    assert len(page_two.json()["items"]) >= 1


def test_admin_disabled_without_password(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "admin_password", None)
    client = TestClient(app)
    response = client.post(
        "/api/v1/admin/login",
        json={"username": "fengge", "password": "anything"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "admin disabled: set ADMIN_PASSWORD"
