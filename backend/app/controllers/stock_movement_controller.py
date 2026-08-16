"""Stock movement HTTP controller."""

from flask import request

from app.services.stock_movement_service import StockMovementService
from app.utils.responses import success_response


def list_movements():
    data, meta = StockMovementService.list_movements(
        item_id=request.args.get("item_id"),
        source=request.args.get("source"),
        from_date=request.args.get("from"),
        to_date=request.args.get("to"),
        page=int(request.args.get("page", 1)),
        per_page=int(request.args.get("per_page", 50)),
    )
    return success_response(data=data, meta=meta)
