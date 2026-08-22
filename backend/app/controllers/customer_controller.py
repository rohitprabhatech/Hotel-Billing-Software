"""Customer HTTP controller."""

from flask import request

from app.schemas.customer_schemas import (
    create_customer_schema,
    status_schema,
    update_customer_schema,
)
from app.services.customer_service import CustomerService
from app.utils.responses import success_response


def list_customers():
    q = request.args.get("q")
    is_active = request.args.get("is_active")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    active_filter = None
    if is_active is not None and str(is_active).strip() != "":
        active_filter = str(is_active).lower() in {"1", "true", "yes"}
    data, meta = CustomerService.list_customers(
        q=q,
        is_active=active_filter,
        page=page,
        per_page=per_page,
    )
    return success_response(data=data, meta=meta)


def get_customer(customer_id: str):
    return success_response(data=CustomerService.get_customer(customer_id))


def create_customer():
    payload = create_customer_schema.load(request.get_json() or {})
    data = CustomerService.create_customer(
        name=payload["name"],
        phone_country_code=payload.get("phone_country_code"),
        phone=payload.get("phone"),
        email=payload.get("email"),
        credit_limit=payload.get("credit_limit"),
        notes=payload.get("notes"),
    )
    return success_response(data=data, status_code=201)


def update_customer(customer_id: str):
    raw = request.get_json() or {}
    payload = update_customer_schema.load(raw)
    data = CustomerService.update_customer(
        customer_id,
        name=payload.get("name") if "name" in raw else None,
        phone_country_code=payload.get("phone_country_code") if "phone" in raw or "phone_country_code" in raw else None,
        phone=payload.get("phone") if "phone" in raw or "phone_country_code" in raw else None,
        phone_provided="phone" in raw or "phone_country_code" in raw,
        email=payload.get("email") if "email" in raw else None,
        email_provided="email" in raw,
        credit_limit=payload.get("credit_limit") if "credit_limit" in raw else None,
        credit_limit_provided="credit_limit" in raw,
        notes=payload.get("notes") if "notes" in raw else None,
        notes_provided="notes" in raw,
    )
    return success_response(data=data)


def deactivate_customer(customer_id: str):
    data = CustomerService.deactivate_customer(customer_id)
    return success_response(data=data)


def set_customer_status(customer_id: str):
    payload = status_schema.load(request.get_json() or {})
    data = CustomerService.set_status(customer_id, payload["is_active"])
    return success_response(data=data)


def list_customer_bills(customer_id: str):
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    data, meta = CustomerService.list_customer_bills(
        customer_id,
        page=page,
        per_page=per_page,
    )
    return success_response(data=data, meta=meta)
