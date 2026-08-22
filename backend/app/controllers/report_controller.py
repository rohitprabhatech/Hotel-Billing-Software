"""Report HTTP controller."""

from flask import request

from app.services.report_service import ReportService
from app.utils.responses import success_response


def summary():
    period = request.args.get("period", "today")
    from_date = request.args.get("from")
    to_date = request.args.get("to")
    data = ReportService.summary(period=period, from_date=from_date, to_date=to_date)
    return success_response(data=data)


def daily_sales():
    date = request.args.get("date")
    payment_method = request.args.get("payment_method")
    data = ReportService.daily_sales(date, payment_method=payment_method)
    return success_response(data=data)


def weekly_sales():
    payment_method = request.args.get("payment_method")
    data = ReportService.weekly_sales(payment_method=payment_method)
    return success_response(data=data)


def monthly_sales():
    year = request.args.get("year")
    month = request.args.get("month")
    payment_method = request.args.get("payment_method")
    data = ReportService.monthly_sales(
        int(year) if year else None,
        int(month) if month else None,
        payment_method=payment_method,
    )
    return success_response(data=data)


def custom_sales():
    from_date = request.args.get("from")
    to_date = request.args.get("to")
    payment_method = request.args.get("payment_method")
    data = ReportService.custom_sales(
        from_date, to_date, payment_method=payment_method
    )
    return success_response(data=data)


def fb_report():
    date = request.args.get("date")
    from_date = request.args.get("from")
    to_date = request.args.get("to")
    data = ReportService.fb_report(date=date, from_date=from_date, to_date=to_date)
    return success_response(data=data)


def export_report():
    return ReportService.export(
        report_type=request.args.get("type", "daily"),
        fmt=request.args.get("format", "xlsx"),
        date=request.args.get("date"),
        from_date=request.args.get("from"),
        to_date=request.args.get("to"),
        year=request.args.get("year"),
        month=request.args.get("month"),
        payment_method=request.args.get("payment_method"),
    )
