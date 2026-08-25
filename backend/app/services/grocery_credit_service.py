"""Grocery credit aliases and kirana sales report (BIZ-23). Reuses BIZ-09 ledger."""

from app.constants.permissions import PERM_CUSTOMERS_READ, PERM_REPORTS
from app.repositories.party_ledger_repository import PartyLedgerRepository
from app.services.party_ledger_service import PartyLedgerService
from app.services.report_service import ReportService
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context


class GroceryCreditService:
    @staticmethod
    def sales_report(*, date: str | None = None, payment_method: str | None = None):
        require_permission(PERM_REPORTS)
        ctx = require_request_context()
        sales = ReportService.daily_sales(date, payment_method=payment_method)
        outstanding = PartyLedgerRepository.outstanding_summary(ctx.tenant_id)
        return {
            **sales,
            "outstanding": outstanding,
        }

    @staticmethod
    def list_outstanding(*, page=1, per_page=50):
        require_permission(PERM_CUSTOMERS_READ)
        return PartyLedgerService.list_outstanding(page=page, per_page=per_page)

    @staticmethod
    def customer_credit(customer_id: str, *, page=1, per_page=50):
        require_permission(PERM_CUSTOMERS_READ)
        return PartyLedgerService.list_customer_ledger(
            customer_id, page=page, per_page=per_page
        )

    @staticmethod
    def record_payment(customer_id: str, *, amount, notes=None, collection_method=None):
        return PartyLedgerService.record_customer_payment(
            customer_id,
            amount=amount,
            notes=notes,
            collection_method=collection_method,
        )
