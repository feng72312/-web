from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.core.tianxiang import ephemeris
from app.core.tianxiang.errors import EphemerisUnavailableError, InvalidInstantError
from app.core.tianxiang.mansions import MANSION_TABLE_VERSION, list_mansion_table
from app.core.tianxiang.service import TianxiangService
from app.core.qimen.solar_time import apply_true_solar_time
from app.core.calendar.china_dst import apply_china_dst
from app.schemas.tianxiang import (
    TianxiangBodyOut,
    TianxiangPositionsRequest,
    TianxiangPositionsResponse,
)

router = APIRouter(prefix="/api/v1/tianxiang", tags=["tianxiang"])


@router.get("/mansions")
async def mansions() -> dict:
    return {
        "mansionTableVersion": MANSION_TABLE_VERSION,
        "mansions": list_mansion_table(),
    }


@router.post("/positions", response_model=TianxiangPositionsResponse)
async def positions(body: TianxiangPositionsRequest) -> TianxiangPositionsResponse:
    try:
        svc = TianxiangService()
    except EphemerisUnavailableError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err
    dt = datetime(
        body.year,
        body.month,
        body.day,
        body.hour,
        body.minute,
        body.second,
    )
    dt = apply_china_dst(dt)
    if body.useTrueSolarTime:
        dt = apply_true_solar_time(dt, body.longitude)
    utc_dt = dt.astimezone(timezone.utc)
    try:
        jd = ephemeris.datetime_to_julian(utc_dt)
        from app.core.tianxiang.models import TianxiangInstant

        instant = TianxiangInstant(
            utc_iso=utc_dt.isoformat(),
            julian_day=jd,
            latitude=body.latitude,
            longitude=body.longitude,
            true_solar_time=dt.strftime("%Y-%m-%d %H:%M:%S"),
        )
        raw = svc.compute_positions(instant)
        asc = svc.ascendant(instant)
    except InvalidInstantError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    bodies = [
        TianxiangBodyOut(
            id=p.id,
            label=p.label,
            eclipticLongitude=p.ecliptic_longitude,
            mansion=p.mansion,
            mansionDegree=p.mansion_degree,
            retrograde=p.retrograde,
        )
        for p in raw
    ]
    return TianxiangPositionsResponse(
        julianDay=jd,
        ascendantLongitude=round(asc, 4),
        bodies=bodies,
        mansionTableVersion=MANSION_TABLE_VERSION,
    )
