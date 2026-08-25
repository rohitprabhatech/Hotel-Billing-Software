"""Clothing reports HTTP controller (BIZ-28)."""

from flask import request

from app.services.clothing_report_service import ClothingReportService
from app.utils.exceptions import ValidationError
from app.utils.responses import success_response


def sales_report():
    data = ClothingReportService.sales_report(
        date=request.args.get("date"),
        from_date=request.args.get("from") or request.args.get("from_date"),
        to_date=request.args.get("to") or request.args.get("to_date"),
        payment_method=request.args.get("payment_method"),
        brand=request.args.get("brand"),
        size=request.args.get("size"),
        color=request.args.get("color"),
        category_id=request.args.get("category_id"),
    )
    return success_response(data=data)


def customer_history():
    customer_id = (request.args.get("customer_id") or "").strip()
    if not customer_id:
        raise ValidationError("customer_id is required")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    data, meta = ClothingReportService.customer_history(
        customer_id, page=page, per_page=per_page
    )
    return success_response(data=data, meta=meta)
