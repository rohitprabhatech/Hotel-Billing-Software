"""Measurement UoM helpers for hardware / building material (BIZ-35)."""

from __future__ import annotations

from decimal import Decimal

from app.constants.uom import (
    UOM_CM,
    UOM_FT,
    UOM_G,
    UOM_KG,
    UOM_L,
    UOM_M,
    UOM_ML,
    UOM_PCS,
    UOM_SQFT,
    UOM_SQM,
)

KIND_COUNT = "count"
KIND_WEIGHT = "weight"
KIND_VOLUME = "volume"
KIND_LENGTH = "length"
KIND_AREA = "area"

MEASUREMENT_UOMS: frozenset[str] = frozenset(
    {
        UOM_KG,
        UOM_G,
        UOM_L,
        UOM_ML,
        UOM_M,
        UOM_CM,
        UOM_FT,
        UOM_SQM,
        UOM_SQFT,
    }
)

LENGTH_UOMS: frozenset[str] = frozenset({UOM_M, UOM_CM, UOM_FT})
WEIGHT_UOMS: frozenset[str] = frozenset({UOM_KG, UOM_G})
VOLUME_UOMS: frozenset[str] = frozenset({UOM_L, UOM_ML})
AREA_UOMS: frozenset[str] = frozenset({UOM_SQM, UOM_SQFT})

_KIND_BY_UOM: dict[str, str] = {
    UOM_PCS: KIND_COUNT,
    "box": KIND_COUNT,
    "pack": KIND_COUNT,
    UOM_KG: KIND_WEIGHT,
    UOM_G: KIND_WEIGHT,
    UOM_L: KIND_VOLUME,
    UOM_ML: KIND_VOLUME,
    UOM_M: KIND_LENGTH,
    UOM_CM: KIND_LENGTH,
    UOM_FT: KIND_LENGTH,
    UOM_SQM: KIND_AREA,
    UOM_SQFT: KIND_AREA,
}


def measurement_kind(uom: str | None) -> str:
    code = (uom or UOM_PCS).strip().lower()
    return _KIND_BY_UOM.get(code, KIND_COUNT)


def is_measurement_uom(uom: str | None) -> bool:
    return measurement_kind(uom) != KIND_COUNT


def qty_step_for_uom(uom: str | None) -> Decimal:
    return Decimal("0.001") if is_measurement_uom(uom) else Decimal("1")


def effective_sale_uom(*, uom: str | None, sale_uom: str | None) -> str:
    sale = (sale_uom or "").strip().lower()
    stock = (uom or UOM_PCS).strip().lower()
    return sale or stock
