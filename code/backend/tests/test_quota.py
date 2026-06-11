from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.quota.keys import (
    FREE_DAILY_LIMIT,
    TIER_FREE_DAILY_LIMITS,
    credits_for_tier,
    generate_license_key,
    hash_license_key,
    normalize_license_key,
)
from app.core.quota.service import QuotaService
from app.core.quota.store import QuotaExceededError, QuotaStore
from app.main import app


@pytest.fixture()
def quota_store(tmp_path: Path) -> QuotaStore:
    return QuotaStore(tmp_path / "quota.db")


@pytest.fixture()
def quota_service(quota_store: QuotaStore) -> QuotaService:
    return QuotaService(quota_store)


def test_tier_mapping() -> None:
    assert credits_for_tier(10) == 20
    assert credits_for_tier(100) == 500


def test_consume_tier_free_then_shared_then_paid(quota_service: QuotaService) -> None:
    device = "test-device-tier-001"
    tier_limit = TIER_FREE_DAILY_LIMITS["大师"]

    for _ in range(tier_limit):
        result = quota_service.consume_one(device, tier_name="大师")
        assert result["source"] == "tier_free"

    result = quota_service.consume_one(device, tier_name="大师")
    assert result["source"] == "shared_free"

    for _ in range(FREE_DAILY_LIMIT - 1):
        result = quota_service.consume_one(device, tier_name="大师")
        assert result["source"] == "shared_free"

    plain = generate_license_key()
    quota_service._store.insert_license_keys(
        [(hash_license_key(normalize_license_key(plain)), 5, "10", None)]
    )
    quota_service.redeem_key(device, plain)

    result = quota_service.consume_one(device, tier_name="大师")
    assert result["source"] == "paid"


def test_tier_quotas_are_independent(quota_service: QuotaService) -> None:
    device = "test-device-tier-002"
    quota_service.consume_one(device, tier_name="小师傅")
    status = quota_service.get_status(device)
    tiers = {item["tier"]: item for item in status["tierQuotas"]}
    assert tiers["小师傅"]["remaining"] == TIER_FREE_DAILY_LIMITS["小师傅"] - 1
    assert tiers["大师"]["remaining"] == TIER_FREE_DAILY_LIMITS["大师"]


def test_consume_free_then_paid(quota_service: QuotaService) -> None:
    device = "test-device-001"
    for _ in range(TIER_FREE_DAILY_LIMITS["大师"]):
        quota_service.consume_one(device, tier_name="大师")
    for _ in range(FREE_DAILY_LIMIT):
        quota_service.consume_one(device, tier_name="大师")

    plain = generate_license_key()
    quota_service._store.insert_license_keys(
        [(hash_license_key(normalize_license_key(plain)), 5, "10", None)]
    )
    quota_service.redeem_key(device, plain)

    result = quota_service.consume_one(device, tier_name="大师")
    assert result["source"] == "paid"


def test_quota_exceeded(quota_service: QuotaService) -> None:
    device = "test-device-002"
    for _ in range(TIER_FREE_DAILY_LIMITS["大师"]):
        quota_service.consume_one(device, tier_name="大师")
    for _ in range(FREE_DAILY_LIMIT):
        quota_service.consume_one(device, tier_name="大师")
    with pytest.raises(QuotaExceededError):
        quota_service.consume_one(device, tier_name="大师")


def test_redeem_once(quota_service: QuotaService) -> None:
    device = "test-device-003"
    plain = generate_license_key()
    quota_service._store.insert_license_keys(
        [(hash_license_key(normalize_license_key(plain)), 20, "10", None)]
    )
    out = quota_service.redeem_key(device, plain)
    assert out["addedCredits"] == 20
    assert out["creditBalance"] == 20


def test_api_persistence(tmp_path: Path) -> None:
    store = QuotaStore(tmp_path / "quota.db")
    app.state.quota_service = QuotaService(store)

    client = TestClient(app)
    r = client.get("/api/v1/quota/persistence")
    assert r.status_code == 200
    body = r.json()
    assert "likelyPersistent" in body
    assert body["likelyPersistent"] is False


def test_api_status_and_redeem(tmp_path: Path) -> None:
    store = QuotaStore(tmp_path / "quota.db")
    app.state.quota_service = QuotaService(store)

    device = "device-api-test-001"
    client = TestClient(app)
    r = client.get(
        "/api/v1/quota/status",
        headers={"X-Device-Id": device},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["freeRemaining"] == FREE_DAILY_LIMIT
    assert len(body["tierQuotas"]) == 3
    assert body["tierQuotas"][0]["tier"] == "小师傅"
    assert body["tierQuotas"][0]["remaining"] == TIER_FREE_DAILY_LIMITS["小师傅"]

    plain = generate_license_key()
    store.insert_license_keys(
        [(hash_license_key(normalize_license_key(plain)), 50, "20", "test")]
    )
    r2 = client.post(
        "/api/v1/quota/redeem",
        json={"deviceId": device, "key": plain},
        headers={"X-Device-Id": device},
    )
    assert r2.status_code == 200
    assert r2.json()["addedCredits"] == 50
