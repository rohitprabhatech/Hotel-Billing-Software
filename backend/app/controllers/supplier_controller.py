"""Supplier HTTP controller."""

from flask import request

from app.schemas.supplier_schemas import (
    create_supplier_schema,
    status_schema,
    update_supplier_schema,
)
from app.services.supplier_service import SupplierService
from app.utils.responses import success_response


def list_suppliers():
    q = request.args.get("q")
    is_active = request.args.get("is_active")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    active_filter = None
    if is_active is not None and str(is_active).strip() != "":
        active_filter = str(is_active).lower() in {"1", "true", "yes"}
    data, meta = SupplierService.list_suppliers(
        q=q,
        is_active=active_filter,
        page=page,
        per_page=per_page,
    )
    return success_response(data=data, meta=meta)


def get_supplier(supplier_id: str):
    return success_response(data=SupplierService.get_supplier(supplier_id))


def create_supplier():
    payload = create_supplier_schema.load(request.get_json() or {})
    data = SupplierService.create_supplier(
        name=payload["name"],
        phone_country_code=payload.get("phone_country_code"),
        phone=payload.get("phone"),
        gstin=payload.get("gstin"),
        email=payload.get("email"),
        address=payload.get("address"),
        notes=payload.get("notes"),
    )
    return success_response(data=data, status_code=201)


def update_supplier(supplier_id: str):
    raw = request.get_json() or {}
    payload = update_supplier_schema.load(raw)
    data = SupplierService.update_supplier(
        supplier_id,
        name=payload.get("name") if "name" in raw else None,
        phone_country_code=payload.get("phone_country_code")
        if "phone" in raw or "phone_country_code" in raw
        else None,
        phone=payload.get("phone") if "phone" in raw or "phone_country_code" in raw else None,
        phone_provided="phone" in raw or "phone_country_code" in raw,
        gstin=payload.get("gstin") if "gstin" in raw else None,
        gstin_provided="gstin" in raw,
        email=payload.get("email") if "email" in raw else None,
        email_provided="email" in raw,
        address=payload.get("address") if "address" in raw else None,
        address_provided="address" in raw,
        notes=payload.get("notes") if "notes" in raw else None,
        notes_provided="notes" in raw,
    )
    return success_response(data=data)


def deactivate_supplier(supplier_id: str):
    data = SupplierService.deactivate_supplier(supplier_id)
    return success_response(data=data)


def set_supplier_status(supplier_id: str):
    payload = status_schema.load(request.get_json() or {})
    data = SupplierService.set_status(supplier_id, payload["is_active"])
    return success_response(data=data)
