"""Reports HTTP controller."""

from flask import request

from app.services.report_service import ReportService
from app.utils.responses import success_response


def summary():
    period = request.args.get("period", "today")
    data = ReportService.summary(
        period=period,
        from_date=request.args.get("from"),
        to_date=request.args.get("to"),
    )
    return success_response(data=data)


def daily_sales():
    data = ReportService.daily_sales(request.args.get("date"))
    return success_response(data=data)


def monthly_sales():
    year = request.args.get("year")
    month = request.args.get("month")
    data = ReportService.monthly_sales(
        int(year) if year else None,
        int(month) if month else None,
    )
    return success_response(data=data)


def custom_sales():
    data = ReportService.custom_sales(
        request.args.get("from"),
        request.args.get("to"),
    )
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
    )