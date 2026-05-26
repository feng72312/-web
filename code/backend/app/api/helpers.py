from app.core.paipan.models import PaipanInput
from app.schemas.paipan import PaipanRequest


def request_to_input(body: PaipanRequest) -> PaipanInput:
    return PaipanInput(
        name=body.name.strip(),
        calendar_type=body.calendarType,
        year=body.year,
        month=body.month,
        day=body.day,
        is_leap_month=body.isLeapMonth,
        hour=body.hour,
        minute=body.minute,
        second=body.second,
        gender=body.gender,
    )
