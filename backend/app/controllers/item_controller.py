"""Item HTTP controller."""

from flask import request

from app.schemas.item_schemas import (
    adjust_stock_schema,
    create_item_schema,
    item_status_schema,
    update_item_schema,
)
from app.services.item_service import ItemService
from app.utils.exceptions import ForbiddenError
from app.utils.responses import success_response


def _parse_bool(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    return str(value).lower() in {"1", "true", "yes"}


def list_items():
    q = request.args.get("q")
    category_id = request.args.get("category_id")
    is_active = _parse_bool(request.args.get("is_active"))
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    data, meta = ItemService.list_items(
        q=q,
        category_id=category_id,
        is_active=is_active,
        page=page,
        per_page=per_page,
    )
    return success_response(data=data, meta=meta)


def get_item(item_id: str):
    return success_response(data=ItemService.get_item(item_id))


def create_item():
    payload = create_item_schema.load(request.get_json() or {})
    data = ItemService.create_item(
        name=payload["name"],
        category_id=payload["category_id"],
        description=payload.get("description"),
        price=payload["price"],
        gst_percentage=payload.get("gst_percentage", 0),
        sku=payload.get("sku"),
        cost_price=payload.get("cost_price"),
        stock_quantity=payload.get("stock_quantity"),
        minimum_stock_level=payload.get("minimum_stock_level"),
    )
    return success_response(data=data, status_code=201)


def update_item(item_id: str):
    raw = request.get_json() or {}
    payload = update_item_schema.load(raw)
    data = ItemService.update_item(
        item_id,
        name=payload.get("name") if "name" in raw else None,
        category_id=payload.get("category_id") if "category_id" in raw else None,
        description=payload.get("description") if "description" in raw else None,
        price=payload.get("price") if "price" in raw else None,
        gst_percentage=payload.get("gst_percentage") if "gst_percentage" in raw else None,
        sku=payload.get("sku") if "sku" in raw else None,
        sku_provided="sku" in raw,
        cost_price=payload.get("cost_price") if "cost_price" in raw else None,
        cost_price_provided="cost_price" in raw,
        stock_quantity=payload.get("stock_quantity") if "stock_quantity" in raw else None,
        stock_quantity_provided="stock_quantity" in raw,
        minimum_stock_level=(
            payload.get("minimum_stock_level") if "minimum_stock_level" in raw else None
        ),
        minimum_stock_level_provided="minimum_stock_level" in raw,
    )
    return success_response(data=data)


def set_item_status(item_id: str):
    payload = item_status_schema.load(request.get_json() or {})
    data = ItemService.set_status(
        item_id,
        payload["is_active"],
        reason=payload.get("reason"),
    )
    return success_response(data=data)


def adjust_stock(item_id: str):
    payload = adjust_stock_schema.load(request.get_json() or {})
    data = ItemService.adjust_stock(
        item_id,
        delta=payload["delta"],
        reason=payload.get("reason"),
    )
    return success_response(data=data)


def delete_item(item_id: str):
    raise ForbiddenError(
        "Permanent item deletion is not allowed. Deactivate the item instead."
    )
