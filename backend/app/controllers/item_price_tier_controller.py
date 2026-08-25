"""Item price tier HTTP controller (BIZ-21)."""

from flask import request

from app.schemas.item_price_tier_schemas import create_price_tier_schema, replace_price_tiers_schema
from app.services.bulk_pricing_service import BulkPricingService
from app.utils.responses import success_response


def list_price_tiers(item_id: str):
    return success_response(data=BulkPricingService.list_tiers(item_id))


def create_price_tier(item_id: str):
    payload = create_price_tier_schema.load(request.get_json() or {})
    data = BulkPricingService.create_tier(
        item_id,
        min_quantity=payload["min_quantity"],
        unit_price=payload["unit_price"],
        is_active=payload.get("is_active", True),
    )
    return success_response(data=data, status_code=201)


def replace_price_tiers(item_id: str):
    payload = replace_price_tiers_schema.load(request.get_json() or {})
    data = BulkPricingService.replace_tiers(item_id, payload.get("tiers") or [])
    return success_response(data=data)


def delete_price_tier(item_id: str, tier_id: str):
    return success_response(data=BulkPricingService.delete_tier(item_id, tier_id))
