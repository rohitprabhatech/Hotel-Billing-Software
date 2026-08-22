"""Unit-of-measure quantity conversion helpers (BIZ-08)."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from app.constants.uom import UOM_CM, UOM_G, UOM_KG, UOM_L, UOM_M, UOM_ML
from app.utils.exceptions import ValidationError

_CONVERSIONS: dict[tuple[str, str], Decimal] = {
    (UOM_KG, UOM_G): Decimal("1000"),
    (UOM_G, UOM_KG): Decimal("0.001"),
    (UOM_L, UOM_ML): Decimal("1000"),
    (UOM_ML, UOM_L): Decimal("0.001"),
    (UOM_M, UOM_CM): Decimal("100"),
    (UOM_CM, UOM_M): Decimal("0.01"),
}


def convert_quantity(quantity, from_uom: str, to_uom: str) -> Decimal:
    """Convert quantity between compatible base units."""
    try:
        qty = Decimal(str(quantity))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValidationError("Invalid quantity") from exc

    source = (from_uom or "").strip().lower()
    target = (to_uom or "").strip().lower()
    if source == target:
        return qty
    factor = _CONVERSIONS.get((source, target))
    if factor is None:
        raise ValidationError(
            f"Cannot convert from '{source}' to '{target}'. Units must match or be compatible."
        )
    return (qty * factor).quantize(Decimal("0.001"))
