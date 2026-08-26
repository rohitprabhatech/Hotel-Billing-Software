"""Mobile report HTTP controller (BIZ-32)."""

from flask import request

from app.services.mobile_report_service import MobileReportService
from app.utils.responses import success_response


def sales_report():
    data = MobileReportService.sales_report(
        date=request.args.get("date"),
        from_date=request.args.get("from"),
        to_date=request.args.get("to"),
        payment_method=request.args.get("payment_method"),
        brand=request.args.get("brand"),
        model_name=request.args.get("model_name") or request.args.get("model"),
        category_id=request.args.get("category_id"),
    )
    return success_response(data=data)


def customer_history():
    customer_id = (request.args.get("customer_id") or "").strip()
    data, meta = MobileReportService.customer_history(
        customer_id,
        page=int(request.args.get("page", 1)),
        per_page=int(request.args.get("per_page", 50)),
    )
    return success_response(data=data, meta=meta)
