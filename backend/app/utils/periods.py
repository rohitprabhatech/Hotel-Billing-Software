"""Reporting period helpers in tenant timezone."""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo


def get_tz(tz_name: str = "Asia/Kolkata") -> ZoneInfo:
    return ZoneInfo(tz_name)


def local_now(tz_name: str = "Asia/Kolkata") -> datetime:
    return datetime.now(get_tz(tz_name))


def to_utc_naive(dt_local: datetime) -> datetime:
    if dt_local.tzinfo is None:
        raise ValueError("Expected timezone-aware local datetime")
    return dt_local.astimezone(timezone.utc).replace(tzinfo=None)


def day_bounds(day_local: datetime) -> tuple[datetime, datetime]:
    start_local = day_local.replace(hour=0, minute=0, second=0, microsecond=0)
    end_local = start_local + timedelta(days=1)
    return to_utc_naive(start_local), to_utc_naive(end_local)


def parse_date(value: str, tz_name: str = "Asia/Kolkata") -> datetime:
    tz = get_tz(tz_name)
    parsed = datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=tz)
    return parsed


def resolve_period(period: str, tz_name: str = "Asia/Kolkata", from_date=None, to_date=None):
    """
    Returns (start_utc_naive, end_utc_naive_exclusive, label, previous_start, previous_end)
    """
    now = local_now(tz_name)
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    period = (period or "today").lower()

    if period == "today":
        start, end = day_bounds(today)
        prev_start, prev_end = day_bounds(today - timedelta(days=1))
        return start, end, "Today", prev_start, prev_end, "Yesterday"

    if period == "yesterday":
        day = today - timedelta(days=1)
        start, end = day_bounds(day)
        prev_start, prev_end = day_bounds(day - timedelta(days=1))
        return start, end, "Yesterday", prev_start, prev_end, "Day Before"

    if period == "this_week":
        start_local = today - timedelta(days=today.weekday())  # Monday
        end_local = start_local + timedelta(days=7)
        prev_start_local = start_local - timedelta(days=7)
        return (
            to_utc_naive(start_local),
            to_utc_naive(end_local),
            "This Week",
            to_utc_naive(prev_start_local),
            to_utc_naive(start_local),
            "Last Week",
        )

    if period == "this_month":
        start_local = today.replace(day=1)
        if start_local.month == 12:
            end_local = start_local.replace(year=start_local.year + 1, month=1)
        else:
            end_local = start_local.replace(month=start_local.month + 1)
        prev_end_local = start_local
        prev_start_local = (start_local - timedelta(days=1)).replace(day=1)
        return (
            to_utc_naive(start_local),
            to_utc_naive(end_local),
            "This Month",
            to_utc_naive(prev_start_local),
            to_utc_naive(prev_end_local),
            "Last Month",
        )

    if period == "last_month":
        first_this = today.replace(day=1)
        end_local = first_this
        prev_month_last = first_this - timedelta(days=1)
        start_local = prev_month_last.replace(day=1)
        before_start = (start_local - timedelta(days=1)).replace(day=1)
        return (
            to_utc_naive(start_local),
            to_utc_naive(end_local),
            "Last Month",
            to_utc_naive(before_start),
            to_utc_naive(start_local),
            "Previous Month",
        )

    if period == "custom":
        if not from_date or not to_date:
            raise ValueError("from and to dates are required for custom period")
        start_local = parse_date(from_date, tz_name)
        end_day = parse_date(to_date, tz_name)
        end_local = end_day + timedelta(days=1)
        if end_local <= start_local:
            raise ValueError("to date must be on or after from date")
        days = (end_day.date() - start_local.date()).days + 1
        from app.constants.report_registry import MAX_CUSTOM_RANGE_DAYS

        if days > MAX_CUSTOM_RANGE_DAYS:
            raise ValueError(
                f"Custom range cannot exceed {MAX_CUSTOM_RANGE_DAYS} days "
                f"(requested {days} days). Narrow the date range."
            )
        prev_end_local = start_local
        prev_start_local = start_local - timedelta(days=days)
        return (
            to_utc_naive(start_local),
            to_utc_naive(end_local),
            f"{from_date} to {to_date}",
            to_utc_naive(prev_start_local),
            to_utc_naive(prev_end_local),
            "Previous Period",
        )

    if period == "last_7_days":
        end_local = today + timedelta(days=1)
        start_local = today - timedelta(days=6)
        prev_end_local = start_local
        prev_start_local = start_local - timedelta(days=7)
        return (
            to_utc_naive(start_local),
            to_utc_naive(end_local),
            "Last 7 Days",
            to_utc_naive(prev_start_local),
            to_utc_naive(prev_end_local),
            "Previous 7 Days",
        )

    if period == "last_30_days":
        end_local = today + timedelta(days=1)
        start_local = today - timedelta(days=29)
        prev_end_local = start_local
        prev_start_local = start_local - timedelta(days=30)
        return (
            to_utc_naive(start_local),
            to_utc_naive(end_local),
            "Last 30 Days",
            to_utc_naive(prev_start_local),
            to_utc_naive(prev_end_local),
            "Previous 30 Days",
        )

    if period == "this_year":
        start_local = today.replace(month=1, day=1)
        end_local = today + timedelta(days=1)
        prev_start_local = start_local.replace(year=start_local.year - 1)
        prev_end_local = start_local
        return (
            to_utc_naive(start_local),
            to_utc_naive(end_local),
            "This Year",
            to_utc_naive(prev_start_local),
            to_utc_naive(prev_end_local),
            "Last Year",
        )

    raise ValueError("Invalid period")
