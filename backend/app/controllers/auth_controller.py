"""Auth HTTP controller."""

from flask import request

from app.repositories.user_repository import UserRepository
from app.schemas.auth_schemas import login_schema
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