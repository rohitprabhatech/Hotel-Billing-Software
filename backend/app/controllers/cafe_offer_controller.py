"""Cafe add-on and combo HTTP controller (BIZ-17)."""

from flask import request

from app.schemas.cafe_offer_schemas import create_addon_group_schema, create_combo_schema
from app.services.cafe_dashboard_service import CafeDashboardService
from app.services.cafe_offer_service import AddonService, CafeMenuService, ComboService
from app.utils.responses import success_response


def list_addons():
    return success_response(data=AddonService.list_menu_addons())


def create_addon_group():
    payload = create_addon_group_schema.load(request.get_json() or {})
    data = AddonService.create_group(
        menu_item_id=payload["menu_item_id"],
        name=payload["name"],
        is_required=payload.get("is_required", False),
        max_selections=payload.get("max_selections"),
        addons=payload.get("addons") or [],
    )
    return success_response(data=data, status_code=201)


def delete_addon_group(group_id: str):
    return success_response(data=AddonService.delete_group(group_id))


def list_combos():
    popular_only = request.args.get("popular") in {"1", "true", "yes"}
    return success_response(data=ComboService.list_combos(popular_only=popular_only))


def get_combo(combo_id: str):
    return success_response(data=ComboService.get_combo(combo_id))


def create_combo():
    payload = create_combo_schema.load(request.get_json() or {})
    data = ComboService.create_combo(
        name=payload["name"],
        combo_price=payload["combo_price"],
        description=payload.get("description"),
        is_popular=payload.get("is_popular", False),
        items=payload.get("items") or [],
    )
    return success_response(data=data, status_code=201)


def delete_combo(combo_id: str):
    return success_response(data=ComboService.delete_combo(combo_id))


def quick_pos_catalog():
    return success_response(data=CafeMenuService.quick_pos_catalog())


def cafe_dashboard():
    period = (request.args.get("period") or "last_7_days").strip() or "last_7_days"
    return success_response(data=CafeDashboardService.dashboard(period=period))
