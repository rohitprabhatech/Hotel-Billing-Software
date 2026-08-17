"""Auth HTTP controller."""

from flask import request

from app.repositories.user_repository import UserRepository
from app.schemas.auth_schemas import (
    change_password_schema,
    email_only_schema,
    login_schema,
    register_business_schema,
    reset_password_schema,
    token_schema,
)
from app.services.auth_service import AuthService
from app.utils.request_context import require_request_context
from app.utils.responses import success_response


def _client_meta():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if ip and "," in ip:
        ip = ip.split(",")[0].strip()
    return ip, request.headers.get("User-Agent")


def login():
    payload = login_schema.load(request.get_json() or {})
    ip, ua = _client_meta()
    data = AuthService.login(payload["email"], payload["password"], ip, ua)
    return success_response(data=data)


def logout():
    ctx = require_request_context()
    user = UserRepository.get_by_id(ctx.user_id)
    ip, ua = _client_meta()
    data = AuthService.logout(user, ip, ua)
    return success_response(data=data)


def me():
    ctx = require_request_context()
    user = UserRepository.get_by_id(ctx.user_id)
    return success_response(data=AuthService.me(user))


def register_business():
    payload = register_business_schema.load(request.get_json() or {})
    data = AuthService.register_business(payload)
    return success_response(data=data, status_code=201)


def register_hotel():
    """Legacy endpoint alias for register_business."""
    return register_business()


def verify_email():
    payload = token_schema.load(request.get_json() or {})
    data = AuthService.verify_email(payload["token"])
    return success_response(data=data)


def resend_verification():
    payload = email_only_schema.load(request.get_json() or {})
    data = AuthService.resend_verification(payload["email"])
    return success_response(data=data)


def forgot_password():
    payload = email_only_schema.load(request.get_json() or {})
    data = AuthService.forgot_password(payload["email"])
    return success_response(data=data)


def reset_password():
    payload = reset_password_schema.load(request.get_json() or {})
    data = AuthService.reset_password(
        payload["token"], payload["password"], payload["confirm_password"]
    )
    return success_response(data=data)


def change_password():
    ctx = require_request_context()
    user = UserRepository.get_by_id(ctx.user_id)
    payload = change_password_schema.load(request.get_json() or {})
    data = AuthService.change_password(
        user,
        current_password=payload["current_password"],
        new_password=payload["new_password"],
        confirm_password=payload["confirm_password"],
    )
    return success_response(data=data)
