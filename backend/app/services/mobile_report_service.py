"""Mobile sales reports and customer purchase history (BIZ-32)."""

from app.constants.permissions import PERM_CUSTOMERS_READ
from app.extensions import db
from app.repositories.bill_repository import BillRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.mobile_report_repository import MobileReportRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.audit_service import AuditService
from app.services.customer_service import CustomerService
from app.services.module_service import ModuleService
from app.services.report_service import ReportService
from app.utils.exceptions import NotFoundError
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context

MODULE = "serial_imei"


class MobileReportService:
    @staticmethod
    def _require_module():
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, MODULE)
        return ctx

    @staticmethod
    def _filters(brand=None, model_name=None, category_id=None):
        return {
            "brand": (brand or "").strip() or None,
            "model_name": (model_name or "").strip() or None,
            "category_id": (category_id or "").strip() or None,
        }

    @staticmethod
    def _period_bounds(*, date=None, from_date=None, to_date=None):
        if from_date and to_date:
            start, end, label, *_ = ReportService._bounds("custom", from_date, to_date)
            return start, end, label, "custom"
        if date:
            start, end, label, *_ = ReportService._bounds("custom", date, date)
            return start, end, label, "daily"
        start, end, label, *_ = ReportService._bounds("today")
        return start, end, label, "daily"

    @staticmethod
    def sales_report(
        *,
        date=None,
        from_date=None,
        to_date=None,
        payment_method=None,
        brand=None,
        model_name=None,
        category_id=None,
    ):
        ctx = ReportService._ensure_reports_access()
        MobileReportService._require_module()
        start, end, label, period = MobileReportService._period_bounds(
            date=date, from_date=from_date, to_date=to_date
        )
        method = ReportService._normalize_filter(payment_method)
        filters = MobileReportService._filters(
            brand=brand, model_name=model_name, category_id=category_id
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
            "by_brand": MobileReportRepository.by_brand(
                ctx.tenant_id, start, end, **kwargs
            ),
            "by_model": MobileReportRepository.by_model(
                ctx.tenant_id, start, end, **kwargs
            ),
            "by_category": MobileReportRepository.by_category(
                ctx.tenant_id, start, end, **kwargs
            ),
            "serial_stock_summary": MobileReportRepository.serial_stock_summary(
                ctx.tenant_id
            ),
            "serial_stock": MobileReportRepository.serial_stock(
                ctx.tenant_id, **filters
            ),
            "returns": MobileReportRepository.returns_summary(
                ctx.tenant_id, start, end
            ),
        }
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="VIEW_MOBILE_REPORT",
            entity_type="REPORT",
            new_data={"label": label, "period": period, "filters": filters},
        )
        db.session.commit()
        return report

    @staticmethod
    def customer_history(customer_id: str, *, page=1, per_page=50):
        require_permission(PERM_CUSTOMERS_READ)
        ctx = MobileReportService._require_module()
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
            action="VIEW_MOBILE_CUSTOMER_HISTORY",
            entity_type="CUSTOMER",
            entity_id=customer.id,
        )
        db.session.commit()
        return payload, {
            "page": max(int(page or 1), 1),
            "per_page": min(max(int(per_page or 50), 1), 100),
            "total": total,
        }
