"""Supported base units of measure (BIZ-08 / BIZ-35)."""

from __future__ import annotations

UOM_PCS = "pcs"
UOM_KG = "kg"
UOM_G = "g"
UOM_L = "l"
UOM_ML = "ml"
UOM_M = "m"
UOM_CM = "cm"
UOM_FT = "ft"
UOM_SQM = "sqm"
UOM_SQFT = "sqft"
UOM_BOX = "box"
UOM_PACK = "pack"

DEFAULT_UOM = UOM_PCS

ALLOWED_UOMS: frozenset[str] = frozenset(
    {
        UOM_PCS,
        UOM_KG,
        UOM_G,
        UOM_L,
        UOM_ML,
        UOM_M,
        UOM_CM,
        UOM_FT,
        UOM_SQM,
        UOM_SQFT,
        UOM_BOX,
        UOM_PACK,
    }
)

UOM_LABELS: dict[str, str] = {
    UOM_PCS: "Pieces",
    UOM_KG: "Kilogram",
    UOM_G: "Gram",
    UOM_L: "Litre",
    UOM_ML: "Millilitre",
    UOM_M: "Metre",
    UOM_CM: "Centimetre",
    UOM_FT: "Foot",
    UOM_SQM: "Square metre",
    UOM_SQFT: "Square foot",
    UOM_BOX: "Box",
    UOM_PACK: "Pack",
}


def normalize_uom(value: str | None, *, default: str = DEFAULT_UOM) -> str:
    if value is None or not str(value).strip():
        return default
    code = str(value).strip().lower()
    if code not in ALLOWED_UOMS:
        allowed = ", ".join(sorted(ALLOWED_UOMS))
        raise ValueError(f"Invalid unit of measure. Allowed: {allowed}")
    return code
