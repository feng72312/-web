from app.core.ziwei.calendar_bridge import _hour_to_time_index
from app.core.ziwei.models import ZiweiInput
from app.core.ziwei.rules import ZiweiRules
from app.core.ziwei.calendar_bridge import resolve_calendar


def test_combined_zi_hour_maps_23_to_early_zi() -> None:
    assert _hour_to_time_index(23, "combined") == 0
    assert _hour_to_time_index(23, "split") == 12


def test_resolve_calendar_true_solar_default() -> None:
    data = ZiweiInput(
        calendar_type="solar",
        year=1990,
        month=5,
        day=15,
        hour=11,
        minute=30,
        gender=1,
        use_true_solar_time=True,
        longitude=120.0,
    )
    ctx = resolve_calendar(data, ZiweiRules())
    assert ctx.true_solar_time.startswith("1990-")
    assert ctx.four_pillars["year"]
