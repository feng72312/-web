from pydantic import BaseModel, Field


class TianxiangPositionsRequest(BaseModel):
    year: int = Field(ge=1900, le=2100)
    month: int = Field(ge=1, le=12)
    day: int = Field(ge=1, le=31)
    hour: int = Field(default=12, ge=0, le=23)
    minute: int = Field(default=0, ge=0, le=59)
    second: int = Field(default=0, ge=0, le=59)
    longitude: float = Field(default=120.0, ge=-180.0, le=180.0)
    latitude: float = Field(default=35.0, ge=-90.0, le=90.0)
    useTrueSolarTime: bool = True


class TianxiangBodyOut(BaseModel):
    id: str
    label: str
    eclipticLongitude: float
    mansion: str
    mansionDegree: float
    retrograde: bool | None = None


class TianxiangPositionsResponse(BaseModel):
    julianDay: float
    ascendantLongitude: float
    bodies: list[TianxiangBodyOut]
    mansionTableVersion: str
