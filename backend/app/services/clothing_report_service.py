"""Clothing sales reports and customer purchase history (BIZ-28)."""

from app.constants.permissions import PERM_CUSTOMERS_READ
from app.extensions import db
from app.repositories.bill_repository import BillRepository
from app.repositories.clothing_report_repository import ClothingReportRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.report_repository import ReportRepository
from app.services.audit_service import AuditService
from app.services.customer_service import CustomerService
from app.services.report_service import ReportService
from app.utils.exceptions import NotFoundError
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context


class ClothingReportService:
    @staticmethod
    def _filters(brand=None, size=None, color=None, category_id=None):
        return {
            "brand": (brand or "").strip() or None,
            "size": (size or "").strip() or None,
            "color": (color or "").strip() or None,
            "category_id": (category_id or "").strip() or None,
        }

    @staticmethod
    def _period_bounds(*, date=None, from_date=None, to_date=None, period=None):
        if from_date and to_date:
            start, end, label, *_ = ReportService._bounds("custom", from_date, to_date)
            return start, end, label, "custom"
        if date:
            start, end, label, *_ = ReportService._bounds("custom", date, date)
            return start, end, label, "daily"
        if period:
            start, end, label, *_ = ReportService._bounds(period)
            return start, end, label, period
        start, end, label, *_ = ReportService._bounds("today")
        return start, end, label, "daily"

    @staticmethod
    def sales_report(
        *,
        date=None,
        from_date=None,
        to_date=None,
        period=None,
        payment_method=None,
        brand=None,
        size=None,
        color=None,
        category_id=None,
    ):
        ctx = ReportService._ensure_reports_access()
        start, end, label, period = ClothingReportService._period_bounds(
            date=date, from_date=from_date, to_date=to_date, period=period
        )
        method = ReportService._normalize_filter(payment_method)
        filters = ClothingReportService._filters(
            brand=brand, size=size, color=color, category_id=category_id
        )
        kwargs = {"payment_method": method, **filters}
        report = {
            "period": period,
            "label": label,
            "payment_method": method,
            "filters": filters,
            "metrics": ReportRepository.period_metrics(
                ctx.tenant_id, start, end, payment_method=method
            ),
            "by_brand": ClothingReportRepository.by_brand(
                ctx.tenant_id, start, end, **kwargs
            ),
            "by_size": ClothingReportRepository.by_size(
                ctx.tenant_id, start, end, **kwargs
            ),
            "by_color": ClothingReportRepository.by_color(
                ctx.tenant_id, start, end, **kwargs
            ),
            "by_category": ClothingReportRepository.by_category(
                ctx.tenant_id, start, end, **kwargs
            ),
            "variant_stock": ClothingReportRepository.variant_stock(
                ctx.tenant_id, **filters
            ),
            "returns": ClothingReportRepository.returns_summary(
                ctx.tenant_id, start, end
            ),
        }
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="VIEW_CLOTHING_REPORT",
            entity_type="REPORT",
            new_data={"label": label, "period": period, "filters": filters},
        )
        db.session.commit()
        return report

    @staticmethod
    def customer_history(customer_id: str, *, page=1, per_page=50):
        require_permission(PERM_CUSTOMERS_READ)
        ctx = require_request_context()
        customer = CustomerRepository.get_by_id_and_tenant(customer_id, ctx.tenant_id)
        if customer is None:
            raise NotFoundError("Customer not found")

        bills, total = BillRepository.list_by_tenant(
            ctx.tenant_id,
            customer_id=customer_id,
            page=page,
            per_page=per_page,
            load_items=True,
        )
        from app.services.bill_service import BillService

        payload = {
            "customer": CustomerService.serialize(customer),
            "bills": [
                BillService.serialize(bill, include_items=True) for bill in bills
            ],
        }
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="VIEW_CLOTHING_CUSTOMER_HISTORY",
            entity_type="CUSTOMER",
            entity_id=customer.id,
        )
        db.session.commit()
        return payload, {
            "page": max(int(page or 1), 1),
            "per_page": min(max(int(per_page or 50), 1), 100),
            "total": total,
        }
