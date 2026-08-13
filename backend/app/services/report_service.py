"""Owner sales reporting and exports."""

import calendar
import csv
import io
import re
from datetime import datetime

from flask import current_app, send_file
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.extensions import db
from app.models.role import ROLE_OWNER
from app.repositories.report_repository import ReportRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.audit_service import AuditService
from app.utils.exceptions import ForbiddenError, ValidationError
from app.utils.periods import resolve_period
from app.utils.request_context import require_request_context


class ReportService:
    @staticmethod
    def _ensure_owner():
        ctx = require_request_context()
        if ctx.role != ROLE_OWNER:
            raise ForbiddenError("Only hotel owners can access reports")
        return ctx

    @staticmethod
    def _tz():
        return current_app.config.get("REPORT_TIMEZONE", "Asia/Kolkata")

    @staticmethod
    def _bounds(period: str, from_date=None, to_date=None):
        try:
            return resolve_period(period, ReportService._tz(), from_date, to_date)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

    @staticmethod
    def _build_report(tenant_id: str, start, end, label: str, period: str):
        return {
            "period": period,
            "label": label,
            "metrics": ReportRepository.period_metrics(tenant_id, start, end),
            "item_wise": ReportRepository.item_wise(tenant_id, start, end),
            "day_wise": ReportRepository.day_wise(tenant_id, start, end),
        }

    @staticmethod
    def summary(period: str = "today", from_date=None, to_date=None):
        ctx = ReportService._ensure_owner()
        start, end, label, prev_start, prev_end, prev_label = ReportService._bounds(
            period, from_date, to_date
        )
        current = ReportRepository.period_metrics(ctx.tenant_id, start, end)
        previous = ReportRepository.period_metrics(ctx.tenant_id, prev_start, prev_end)
        return {
            "period": period,
            "label": label,
            "previous_label": prev_label,
            "current": current,
            "previous": previous,
            "item_wise": ReportRepository.item_wise(ctx.tenant_id, start, end)[:10],
            "day_wise": ReportRepository.day_wise(ctx.tenant_id, start, end),
        }

    @staticmethod
    def daily_sales(date: str | None = None):
        ctx = ReportService._ensure_owner()
        if date:
            start, end, label, *_ = ReportService._bounds("custom", date, date)
        else:
            start, end, label, *_ = ReportService._bounds("today")
        return ReportService._build_report(ctx.tenant_id, start, end, label, "daily")

    @staticmethod
    def monthly_sales(year: int | None = None, month: int | None = None):
        ctx = ReportService._ensure_owner()
        if year and month:
            last = calendar.monthrange(int(year), int(month))[1]
            from_date = f"{int(year):04d}-{int(month):02d}-01"
            to_date = f"{int(year):04d}-{int(month):02d}-{last:02d}"
            start, end, label, *_ = ReportService._bounds("custom", from_date, to_date)
        else:
            start, end, label, *_ = ReportService._bounds("this_month")
        return ReportService._build_report(ctx.tenant_id, start, end, label, "monthly")

    @staticmethod
    def custom_sales(from_date: str, to_date: str):
        ctx = ReportService._ensure_owner()
        start, end, label, *_ = ReportService._bounds("custom", from_date, to_date)
        return ReportService._build_report(ctx.tenant_id, start, end, label, "custom")

    @staticmethod
    def export(
        *,
        report_type: str,
        fmt: str,
        date=None,
        from_date=None,
        to_date=None,
        year=None,
        month=None,
    ):
        ctx = ReportService._ensure_owner()
        fmt = (fmt or "xlsx").lower()
        if fmt not in {"xlsx", "csv", "pdf"}:
            raise ValidationError("format must be xlsx, csv, or pdf")

        report_type = (report_type or "daily").lower()
        if report_type == "daily":
            report = ReportService.daily_sales(date)
        elif report_type == "monthly":
            report = ReportService.monthly_sales(
                int(year) if year else None,
                int(month) if month else None,
            )
        elif report_type == "custom":
            report = ReportService.custom_sales(from_date, to_date)
        else:
            raise ValidationError("type must be daily, monthly, or custom")

        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        business = (tenant.business_name if tenant else "Hotel").strip() or "Hotel"
        safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", business)
        safe_period = re.sub(r"[^A-Za-z0-9_-]+", "_", report["label"])
        filename = f"{safe_name}_{safe_period}_Sales.{fmt}"

        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="EXPORT_REPORT",
            entity_type="REPORT",
            entity_id=None,
            new_data={
                "type": report_type,
                "label": report["label"],
                "format": fmt,
                "filename": filename,
            },
        )
        db.session.commit()

        if fmt == "csv":
            return ReportService._export_csv(report, filename)
        if fmt == "pdf":
            return ReportService._export_pdf(report, filename, business)
        return ReportService._export_xlsx(report, filename)

    @staticmethod
    def _export_csv(report, filename):
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["Metric", "Value"])
        for key, value in report["metrics"].items():
            writer.writerow([key, value])
        writer.writerow([])
        writer.writerow(["Item", "Quantity", "Revenue"])
        for row in report["item_wise"]:
            writer.writerow([row["item_name"], row["quantity"], row["revenue"]])
        writer.writerow([])
        writer.writerow(["Date", "Sales", "Bills"])
        for row in report["day_wise"]:
            writer.writerow([row["date"], row["total_sales"], row["bill_count"]])

        mem = io.BytesIO(buffer.getvalue().encode("utf-8"))
        mem.seek(0)
        return send_file(
            mem,
            mimetype="text/csv",
            as_attachment=True,
            download_name=filename,
        )

    @staticmethod
    def _export_xlsx(report, filename):
        wb = Workbook()
        ws = wb.active
        ws.title = "Summary"
        ws.append(["Metric", "Value"])
        for key, value in report["metrics"].items():
            ws.append([key, value])

        ws2 = wb.create_sheet("Item Wise")
        ws2.append(["Item", "Quantity", "Revenue"])
        for row in report["item_wise"]:
            ws2.append([row["item_name"], row["quantity"], row["revenue"]])

        ws3 = wb.create_sheet("Day Wise")
        ws3.append(["Date", "Sales", "Bills"])
        for row in report["day_wise"]:
            ws3.append([row["date"], row["total_sales"], row["bill_count"]])

        mem = io.BytesIO()
        wb.save(mem)
        mem.seek(0)
        return send_file(
            mem,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=filename,
        )

    @staticmethod
    def _export_pdf(report, filename, business_name):
        mem = io.BytesIO()
        c = canvas.Canvas(mem, pagesize=A4)
        width, height = A4
        y = height - 50
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, f"{business_name} - Sales Report")
        y -= 24
        c.setFont("Helvetica", 11)
        c.drawString(40, y, f"Period: {report['label']}")
        y -= 20
        c.drawString(40, y, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        y -= 30
        for key, value in report["metrics"].items():
            c.drawString(40, y, f"{key}: {value}")
            y -= 16
            if y < 80:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 11)
        c.showPage()
        c.save()
        mem.seek(0)
        return send_file(
            mem,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename,
        )
