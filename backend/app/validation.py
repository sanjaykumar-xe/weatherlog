from datetime import date, datetime, timezone

from app import config
from app.errors import AppError


def today_utc() -> date:
    return datetime.now(timezone.utc).date()


def check_date_range(start: date, end: date) -> None:
    if start > end:
        raise AppError(422, "invalid_date_range", "The start date must not be after the end date.")
    if start < config.EARLIEST_DATE:
        raise AppError(422, "date_too_early", f"Historical data starts on {config.EARLIEST_DATE.isoformat()}.")
    if end > today_utc():
        raise AppError(422, "future_date", "Historical searches cannot include future dates.")
    if (end - start).days + 1 > config.MAX_RANGE_DAYS:
        raise AppError(422, "range_too_long", f"The date range cannot be longer than {config.MAX_RANGE_DAYS} days.")
