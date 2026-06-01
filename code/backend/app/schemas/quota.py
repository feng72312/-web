from pydantic import BaseModel, Field


class TierQuotaItem(BaseModel):
    tier: str
    remaining: int
    limit: int


class QuotaStatusResponse(BaseModel):
    deviceId: str
    phone: str | None = None
    freeRemaining: int
    freeDailyLimit: int
    creditBalance: int
    tierQuotas: list[TierQuotaItem] = Field(default_factory=list)


class QuotaRedeemRequest(BaseModel):
    deviceId: str = Field(min_length=8, max_length=64)
    key: str = Field(min_length=8, max_length=64)


class QuotaRedeemResponse(BaseModel):
    addedCredits: int
    creditBalance: int


class QuotaBindPhoneRequest(BaseModel):
    deviceId: str = Field(min_length=8, max_length=64)
    phone: str = Field(min_length=11, max_length=11)
