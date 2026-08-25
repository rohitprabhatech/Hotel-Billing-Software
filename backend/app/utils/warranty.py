"""Warranty date helpers (BIZ-30)."""

from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime


def add_months(base: date, months: int) -> date:
    if months <= 0:
        return base
    y = base.year + (base.month - 1 + months) // 12
    m = (base.month - 1 + months) % 12 + 1
    d = min(base.day, monthrange(y, m)[1])
    return date(y, m, d)


def warranty_until_date(sale_at: datetime | date, months: int | None) -> date | None:
    if months is None or int(months) <= 0:
        return None
    base = sale_at.date() if isinstance(sale_at, datetime) else sale_at
    return add_months(base, int(months))


def resolve_warranty_months(*, item, serial_unit=None) -> int | None:
    if serial_unit is not None and serial_unit.warranty_months is not None:
        return int(serial_unit.warranty_months)
    item_months = getattr(item, "warranty_months", None)
    if item_months is not None:
        return int(item_months)
    return None
