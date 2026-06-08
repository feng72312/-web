from __future__ import annotations

import pytest

swisseph = pytest.importorskip("swisseph")

from app.core.tianxiang import ephemeris
from app.core.tianxiang.mansions import longitude_to_mansion


def test_sidereal_sun_in_range():
    jd = ephemeris.datetime_to_julian(
        __import__("datetime").datetime(1990, 6, 15, 4, 0, 0, tzinfo=__import__("datetime").timezone.utc)
    )
    lon, _retro = ephemeris.sidereal_longitude(jd, swisseph.SUN)
    assert 0 <= lon < 360


def test_mansion_partition():
    m = longitude_to_mansion(0.0)
    assert m.mansion == "\u89d2"
    assert m.index == 0
