from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.quota.keys import generate_license_key, hash_license_key, normalize_license_key
from app.core.quota.service import QuotaService
from app.core.quota.store import QuotaStore
from app.main import app


@pytest.fixture()
def quota_store(tmp_path: Path) -> QuotaStore:
    return QuotaStore(tmp_path / "quota.db")


@pytest.fixture()
def quota_service(quota_store: QuotaStore) -> QuotaService:
    return QuotaService(quota_store)


def test_merge_device_credits_and_usage(quota_service: QuotaService) -> None:
    device = "device-merge-001"
    user = "cloudbase-user-001"
    plain = generate_license_key()
    quota_service._store.insert_license_keys(
        [(hash_license_key(normalize_license_key(plain)), 10, "10", None)]
    )
    quota_service.redeem_key(device, plain)
    quota_service.consume_one(device, tier_name="大师")
    merged = quota_service.merge_device_into_user(device, user)
    assert merged is True
    user_status = quota_service.get_status(user)
    assert user_status["creditBalance"] == 10
    merged_again = quota_service.merge_device_into_user(device, user)
    assert merged_again is False


def test_api_status_requires_device_or_auth(tmp_path: Path) -> None:
    store = QuotaStore(tmp_path / "quota.db")
    app.state.quota_service = QuotaService(store)
    client = TestClient(app)
    r = client.get("/api/v1/quota/status")
    assert r.status_code == 400
    device = "device-api-test-002"
    r2 = client.get(
        "/api/v1/quota/status",
        headers={"X-Device-Id": device},
    )
    assert r2.status_code == 200


def test_chat_send_anonymous_with_device_and_free_quota(tmp_path: Path) -> None:
    store = QuotaStore(tmp_path / "quota.db")
    app.state.quota_service = QuotaService(store)
    client = TestClient(app)
    device = "device-no-auth-001"
    r = client.post(
        "/api/v1/chat/send",
        json={"agentId": "agent-test-001", "message": "hello"},
        headers={"X-Device-Id": device},
    )
    assert r.status_code != 401


def test_chat_send_requires_auth_without_device(tmp_path: Path) -> None:
    store = QuotaStore(tmp_path / "quota.db")
    app.state.quota_service = QuotaService(store)
    client = TestClient(app)
    r = client.post(
        "/api/v1/chat/send",
        json={"agentId": "agent-test-001", "message": "hello"},
    )
    assert r.status_code == 401
