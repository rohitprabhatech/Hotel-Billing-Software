"""Coupon HTTP controller (Sprint 5)."""

from flask import request

from app.schemas.coupon_schemas import (
    create_coupon_schema,
    preview_coupon_schema,
    update_coupon_schema,
)
from app.services.coupon_service import CouponService
from app.utils.responses import success_response


def list_coupons():
    active_only = request.args.get("active") in {"1", "true", "yes"}
    return success_response(data=CouponService.list_coupons(active_only=active_only))


def get_coupon(coupon_id: str):
    return success_response(data=CouponService.get_coupon(coupon_id))


def create_coupon():
    payload = create_coupon_schema.load(request.get_json() or {})
    data = CouponService.create_coupon(**payload)
    return success_response(data=data, status_code=201)


def update_coupon(coupon_id: str):
    payload = update_coupon_schema.load(request.get_json() or {})
    data = CouponService.update_coupon(coupon_id, **payload)
    return success_response(data=data)


def deactivate_coupon(coupon_id: str):
    return success_response(data=CouponService.deactivate_coupon(coupon_id))


def preview_coupon():
    payload = preview_coupon_schema.load(request.get_json() or {})
    return success_response(data=CouponService.preview(**payload))
