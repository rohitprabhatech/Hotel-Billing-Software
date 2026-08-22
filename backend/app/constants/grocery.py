"""Grocery POS constants (BIZ-20)."""

from app.constants.uom import UOM_G, UOM_KG, UOM_L, UOM_ML

# Units where fractional quantities are expected at the till.
WEIGHT_UOMS: frozenset[str] = frozenset({UOM_KG, UOM_G, UOM_L, UOM_ML})

DEFAULT_SCAN_QTY_PCS = 1
DEFAULT_SCAN_QTY_WEIGHT = 1


def is_weight_uom(uom: str | None) -> bool:
    if not uom:
        return False
    return str(uom).strip().lower() in WEIGHT_UOMS


def default_scan_quantity(uom: str | None):
    return DEFAULT_SCAN_QTY_WEIGHT if is_weight_uom(uom) else DEFAULT_SCAN_QTY_PCS
