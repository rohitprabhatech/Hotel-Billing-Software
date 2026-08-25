"""Item accessory HTTP controller (BIZ-30)."""

from flask import request

from app.schemas.item_accessory_schemas import replace_item_accessories_schema
from app.services.item_accessory_service import ItemAccessoryService
from app.utils.responses import success_response


def list_item_accessories(item_id: str):
    data = ItemAccessoryService.list_accessories(item_id)
    return success_response(data)


def replace_item_accessories(item_id: str):
    payload = replace_item_accessories_schema.load(request.get_json() or {})
    data = ItemAccessoryService.replace_accessories(
        item_id, payload.get("accessory_item_ids") or []
    )
    return success_response(data)
