"""Profile HTTP controller."""

from flask import request

from app.schemas.profile_schemas import request_email_change_schema, update_profile_schema
from app.services.profile_service import ProfileService
from app.utils.responses import success_response


def get_profile():
    return success_response(data=ProfileService.get_profile())


def update_profile():
    payload = update_profile_schema.load(request.get_json() or {})
    data = ProfileService.update_profile(
        name=payload.get("name"),
        phone=payload.get("phone"),
    )
    return success_response(data=data)


def request_email_change():
    payload = request_email_change_schema.load(request.get_json() or {})
    data = ProfileService.request_email_change(payload["new_email"])
    return success_response(data=data)
