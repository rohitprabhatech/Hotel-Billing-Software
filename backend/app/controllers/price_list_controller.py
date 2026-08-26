"""Price list HTTP controller (BIZ-51)."""

from flask import request

from app.schemas.price_list_schemas import (
    assign_customer_price_list_schema,
    create_price_list_schema,
    replace_price_list_items_schema,
    update_price_list_schema,
)
from app.services.price_list_service import PriceListService
from app.utils.responses import success_response


def list_price_lists():
    data, meta = PriceListService.list_price_lists(
        list_type=request.args.get("list_type"),
        page=int(request.args.get("page", 1)),
        per_page=int(request.args.get("per_page", 100)),
    )
    return success_response(data=data, meta=meta)


def get_price_list(price_list_id: str):
    return success_response(data=PriceListService.get_price_list(price_list_id))


def create_price_list():
    payload = create_price_list_schema.load(request.get_json() or {})
    data = PriceListService.create(
        name=payload["name"],
        list_type=payload.get("list_type"),
        is_default=payload.get("is_default", False),
        is_active=payload.get("is_active", True),
        notes=payload.get("notes"),
    )
    return success_response(data=data, status_code=201)


def update_price_list(price_list_id: str):
    payload = update_price_list_schema.load(request.get_json() or {})
    data = PriceListService.update(price_list_id, **payload)
    return success_response(data=data)


def delete_price_list(price_list_id: str):
    return success_response(data=PriceListService.delete(price_list_id))


def replace_price_list_items(price_list_id: str):
    payload = replace_price_list_items_schema.load(request.get_json() or {})
    data = PriceListService.replace_items(price_list_id, payload["items"])
    return success_response(data=data)


def list_customer_assignments():
    data = PriceListService.list_assignments(price_list_id=request.args.get("price_list_id"))
    return success_response(data=data)


def assign_customer_price_list(customer_id: str):
    payload = assign_customer_price_list_schema.load(request.get_json() or {})
    data = PriceListService.assign_customer(
        customer_id, price_list_id=payload["price_list_id"]
    )
    return success_response(data=data)


def unassign_customer_price_list(customer_id: str):
    return success_response(data=PriceListService.unassign_customer(customer_id))
