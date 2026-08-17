"""Category HTTP controller."""

from flask import request

from app.schemas.category_schemas import (
    create_category_schema,
    status_schema,
    update_category_schema,
)
from app.services.category_service import CategoryService
from app.utils.responses import success_response


def list_categories():
    return success_response(data=CategoryService.list_categories())


def get_category(category_id: str):
    return success_response(data=CategoryService.get_category(category_id))


def create_category():
    payload = create_category_schema.load(request.get_json() or {})
    data = CategoryService.create_category(
        name=payload["name"],
        description=payload.get("description"),
        parent_id=payload.get("parent_id"),
    )
    return success_response(data=data, status_code=201)


def update_category(category_id: str):
    raw = request.get_json() or {}
    payload = update_category_schema.load(raw)
    parent_provided = "parent_id" in raw or "parent_category_id" in raw
    data = CategoryService.update_category(
        category_id,
        name=payload.get("name") if "name" in raw else None,
        description=payload.get("description") if "description" in raw else None,
        parent_id=payload.get("parent_id") if parent_provided else None,
        parent_id_provided=parent_provided,
    )
    return success_response(data=data)


def set_category_status(category_id: str):
    payload = status_schema.load(request.get_json() or {})
    data = CategoryService.set_status(category_id, payload["is_active"])
    return success_response(data=data)