"""Production HTTP controller (BIZ-40)."""

from flask import request

from app.schemas.production_schemas import create_production_schema
from app.services.production_service import ProductionService
from app.utils.responses import success_response


def list_productions():
    finished_item_id = request.args.get("finished_item_id") or request.args.get("item_id")
    from_date = request.args.get("from")
    to_date = request.args.get("to")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    data, meta = ProductionService.list_productions(
        finished_item_id=finished_item_id,
        from_date=from_date,
        to_date=to_date,
        page=page,
        per_page=per_page,
    )
    return success_response(data=data, meta=meta)


def get_production(run_id: str):
    return success_response(data=ProductionService.get_production(run_id))


def create_production():
    payload = create_production_schema.load(request.get_json() or {})
    data = ProductionService.create_production(
        recipe_id=payload["recipe_id"],
        quantity=payload["quantity"],
        notes=payload.get("notes"),
        run_date=payload.get("run_date"),
        expiry_date=payload.get("expiry_date"),
        batch_code=payload.get("batch_code"),
    )
    return success_response(data=data, status_code=201)
