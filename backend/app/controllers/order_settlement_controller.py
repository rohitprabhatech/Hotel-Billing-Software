"""Order settlement HTTP controller (BIZ-15)."""

from flask import request

from app.schemas.order_settlement_schemas import settle_order_schema, split_order_bills_schema
from app.services.order_settlement_service import OrderSettlementService
from app.utils.responses import success_response


def settle_order(order_id: str):
    payload = settle_order_schema.load(request.get_json() or {})
    data = OrderSettlementService.settle_order(
        order_id,
        discount=payload.get("discount"),
        service_charge=payload.get("service_charge"),
        service_charge_percent=payload.get("service_charge_percent"),
        payment_method=payload.get("payment_method"),
        customer_id=payload.get("customer_id"),
        customer_name=payload.get("customer_name"),
        customer_phone_country_code=payload.get("customer_phone_country_code"),
        customer_phone=payload.get("customer_phone"),
        customer_email=payload.get("customer_email"),
        splits=payload.get("splits"),
    )
    return success_response(data=data, status_code=201)


def split_order_bills():
    payload = split_order_bills_schema.load(request.get_json() or {})
    data = OrderSettlementService.split_order_bills(
        order_id=payload["order_id"],
        discount=payload.get("discount"),
        service_charge=payload.get("service_charge"),
        service_charge_percent=payload.get("service_charge_percent"),
        splits=payload.get("splits") or [],
    )
    return success_response(data=data, status_code=201)
