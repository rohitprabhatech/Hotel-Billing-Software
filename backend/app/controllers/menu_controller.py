"""Restaurant menu HTTP controller (BIZ-11)."""

from flask import request

from app.services.menu_service import MenuService
from app.utils.responses import success_response


def _parse_bool(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    return str(value).lower() in {"1", "true", "yes"}


def list_menu():
    is_veg = _parse_bool(request.args.get("is_veg"))
    data = MenuService.list_menu(is_veg=is_veg)
    return success_response(data=data, meta={"total_sections": len(data), "total_items": sum(len(s["items"]) for s in data)})
