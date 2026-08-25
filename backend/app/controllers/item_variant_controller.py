"""Item variant HTTP controller (BIZ-25)."""

from flask import request

from app.schemas.item_variant_schemas import (
    create_item_variant_schema,
    replace_item_variants_schema,
    update_item_variant_schema,
)
from app.services.variant_service import VariantService
from app.utils.responses import success_response


def list_item_variants(item_id: str):
    return success_response(data=VariantService.list_for_item(item_id))


def create_item_variant(item_id: str):
    payload = create_item_variant_schema.load(request.get_json() or {})
    data = VariantService.create(
        item_id,
        size=payload["size"],
        color=payload["color"],
        brand=payload.get("brand"),
        sku=payload.get("sku"),
        barcode=payload.get("barcode"),
        stock_quantity=payload.get("stock_quantity") or 0,
        is_active=payload.get("is_active", True),
    )
    return success_response(data=data, status_code=201)


def replace_item_variants(item_id: str):
    payload = replace_item_variants_schema.load(request.get_json() or {})
    data = VariantService.replace(item_id, payload.get("variants") or [])
    return success_response(data=data)


def update_item_variant(item_id: str, variant_id: str):
    raw = request.get_json() or {}
    payload = update_item_variant_schema.load(raw)
    fields = {key: payload[key] for key in raw if key in payload}
    data = VariantService.update(item_id, variant_id, **fields)
    return success_response(data=data)


def delete_item_variant(item_id: str, variant_id: str):
    return success_response(data=VariantService.delete(item_id, variant_id))


def list_tenant_variants():
    item_id = request.args.get("item_id")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    data, meta = VariantService.list_all(item_id=item_id, page=page, per_page=per_page)
    return success_response(data=data, meta=meta)
