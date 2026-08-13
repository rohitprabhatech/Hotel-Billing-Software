"""User management controller (OWNER)."""

from flask import request

from app.schemas.user_schemas import (
    create_user_schema,
    reset_password_schema,
    update_user_schema,
)
from app.services.user_service import UserService
from app.utils.responses import success_response


def list_users():
    return success_response(data=UserService.list_users())


def get_user(user_id: str):
    return success_response(data=UserService.get_user(user_id))


def create_user():
    payload = create_user_schema.load(request.get_json() or {})
    data = UserService.create_billing_user(
        name=payload["name"],
        email=payload["email"],
        password=payload["password"],
    )
    return success_response(data=data, status_code=201)


def update_user(user_id: str):
    payload = update_user_schema.load(request.get_json() or {})
    data = UserService.update_user(
        user_id,
        name=payload.get("name"),
        email=payload.get("email"),
        is_active=payload.get("is_active"),
    )
    return success_response(data=data)


def reset_password(user_id: str):
    payload = reset_password_schema.load(request.get_json() or {})
    data = UserService.reset_password(user_id, payload["password"])
    return success_response(data=data)