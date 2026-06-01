from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class AdminLoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class AdminLoginResponse(BaseModel):
    token: str
    username: str
    expiresInSeconds: int


class AdminGenerateKeysRequest(BaseModel):
    tier: Literal[10, 20, 50, 100]
    count: int = Field(default=1, ge=1, le=100)
    note: str = Field(default="", max_length=200)


class AdminGeneratedKeyItem(BaseModel):
    key: str
    tier: int
    credits: int


class AdminGenerateKeysResponse(BaseModel):
    keys: list[AdminGeneratedKeyItem]
    count: int


class AdminLicenseKeyItem(BaseModel):
    id: int
    credits: int
    tierLabel: str
    status: str
    note: str | None
    createdAt: float
    redeemedDeviceId: str | None
    redeemedAt: float | None


class AdminLicenseKeyListResponse(BaseModel):
    items: list[AdminLicenseKeyItem]
    total: int
