from __future__ import annotations

from datetime import datetime

from app.config import settings
from app.core.tianxiang import bodies, ephemeris
from app.core.tianxiang.errors import EphemerisUnavailableError
from app.core.tianxiang.mansions import list_mansion_table, longitude_to_mansion
from app.core.tianxiang.models import BodyPosition, MansionPlacement, TianxiangInstant


class TianxiangService:
    def __init__(self) -> None:
        if settings.tianxiang_ephemeris_path:
            ephemeris.configure_ephemeris(settings.tianxiang_ephemeris_path)
        if not ephemeris.is_ephemeris_ready():
            raise EphemerisUnavailableError(ephemeris.ephemeris_error() or "ephemeris not ready")

    @staticmethod
    def ready() -> bool:
        return ephemeris.is_ephemeris_ready()

    def compute_positions(
        self,
        instant: TianxiangInstant,
        *,
        bodies_list: list[str] | None = None,
        mansion_table: str | None = None,
        si_yu_model: str | None = None,
    ) -> list[BodyPosition]:
        table = mansion_table or settings.tianxiang_mansion_table
        model = si_yu_model or settings.tianxiang_si_yu_model
        dt = datetime.fromisoformat(instant.utc_iso.replace("Z", "+00:00"))
        return bodies.compute_all_bodies(
            instant.julian_day,
            dt,
            mansion_table=table,
            si_yu_model=model,
            body_ids=bodies_list,
        )

    def ascendant(
        self,
        instant: TianxiangInstant,
    ) -> float:
        return ephemeris.ascendant_longitude(
            instant.julian_day,
            instant.latitude,
            instant.longitude,
        )

    def mansion_at_longitude(
        self,
        longitude: float,
        *,
        mansion_table: str | None = None,
    ) -> MansionPlacement:
        return longitude_to_mansion(
            longitude,
            mansion_table=mansion_table or settings.tianxiang_mansion_table,
        )

    @staticmethod
    def mansion_table(*, mansion_table: str | None = None) -> list[dict]:
        return list_mansion_table(mansion_table=mansion_table or settings.tianxiang_mansion_table)
