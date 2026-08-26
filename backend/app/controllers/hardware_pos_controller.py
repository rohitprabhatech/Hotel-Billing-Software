"""Hardware POS / quote HTTP controller (BIZ-35)."""

from flask import request

from app.constants.perf import POS_CATALOG_DEFAULT_LIMIT
from app.services.hardware_pos_service import HardwarePosService
from app.utils.exceptions import ValidationError
from app.utils.responses import success_response


def units_catalog():
    return success_response(data=HardwarePosService.units_catalog())


def pos_catalog():
    return success_response(
        data=HardwarePosService.pos_catalog(
            q=request.args.get("q"),
            limit=int(request.args.get("limit", POS_CATALOG_DEFAULT_LIMIT)),
        )
    )


def quote():
    payload = request.get_json() or {}
    item_id = (payload.get("item_id") or "").strip()
    if not item_id:
        raise ValidationError("item_id is required")
    if "quantity" not in payload:
        raise ValidationError("quantity is required")
    return success_response(
        data=HardwarePosService.quote(item_id=item_id, quantity=payload.get("quantity"))
    )


def convert():
    payload = request.get_json() or {}
    if "quantity" not in payload:
        raise ValidationError("quantity is required")
    from_uom = (payload.get("from_uom") or "").strip()
    to_uom = (payload.get("to_uom") or "").strip()
    if not from_uom or not to_uom:
        raise ValidationError("from_uom and to_uom are required")
    return success_response(
        data=HardwarePosService.convert(
            quantity=payload.get("quantity"),
            from_uom=from_uom,
            to_uom=to_uom,
        )
    )
