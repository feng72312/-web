from __future__ import annotations

from pydantic import BaseModel, Field


class AuthProfileResponse(BaseModel):
    uid: str
    username: str | None = None
    phone: str | None = None


class AuthMergeDeviceRequest(BaseModel):
    deviceId: str = Field(default="", max_length=64)


class AuthMergeDeviceResponse(BaseModel):
    merged: bool
    creditBalance: int
    freeRemaining: int | None = None
