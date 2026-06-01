from pydantic import BaseModel, Field


class StatsHeartbeatRequest(BaseModel):
    visitorId: str = Field(min_length=8, max_length=64)
    countVisit: bool = False


class StatsOverviewResponse(BaseModel):
    online: int
    total: int
    visits: int
