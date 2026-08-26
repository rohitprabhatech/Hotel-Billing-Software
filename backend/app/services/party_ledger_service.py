"""Customer credit / party ledger business logic (BIZ-09)."""

from decimal import Decimal, InvalidOperation

from app.constants.permissions import (
    PERM_CUSTOMERS_READ,
    PERM_CUSTOMERS_WRITE,
    PERM_SUPPLIERS_READ,
    PERM_SUPPLIERS_WRITE,
)
from app.constants.payments import PAYMENT_CASH, PAYMENT_CREDIT, PAYMENT_ONLINE
from app.extensions import db
from app.models.party_ledger_entry import (
    ENTRY_BILL_CANCEL,
    ENTRY_CREDIT_PURCHASE,
    ENTRY_CREDIT_SALE,
    ENTRY_PAYMENT,
    PARTY_CUSTOMER,
    PARTY_SUPPLIER,
    REF_BILL,
    REF_PAYMENT,
    REF_PURCHASE,
    PartyLedgerEntry,
)
from app.repositories.customer_repository import CustomerRepository
from app.repositories.party_ledger_repository import PartyLedgerRepository
from app.repositories.supplier_repository import SupplierRepository
from app.services.audit_service import AuditService
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import money
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context


class PartyLedgerService:
    @staticmethod
    def _parse_amount(value, *, field_name: str = "amount") -> Decimal:
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise ValidationError(f"Invalid {field_name}") from exc
        if amount <= 0:
            raise ValidationError(f"{field_name} must be greater than zero")
        return money(amount)

    @staticmethod
    def _normalize_collection_method(value: str | None) -> str:
        method = (value or PAYMENT_CASH).strip().lower()
        if method not in {PAYMENT_CASH, PAYMENT_ONLINE}:
            raise ValidationError("Collection method must be cash or online")
        return method

    @staticmethod
    def _apply_balance(customer, delta: Decimal) -> Decimal:
        current = money(Decimal(customer.balance or 0))
        new_balance = money(current + delta)
        if new_balance < 0:
            raise ValidationError(
                f"Payment exceeds outstanding balance. Balance: {float(current):.2f}"
            )
        if customer.credit_limit is not None and new_balance > Decimal(customer.credit_limit):
            raise ValidationError(
                f"Credit limit exceeded. Limit: {float(customer.credit_limit):.2f}, "
                f"new balance would be {float(new_balance):.2f}"
            )
        customer.balance = new_balance
        return new_balance

    @staticmethod
    def _apply_supplier_balance(supplier, delta: Decimal) -> Decimal:
        current = money(Decimal(getattr(supplier, "balance", 0) or 0))
        new_balance = money(current + delta)
        if new_balance < 0:
            raise ValidationError(
                f"Payment exceeds outstanding balance. Balance: {float(current):.2f}"
            )
        limit = getattr(supplier, "credit_limit", None)
        if limit is not None and new_balance > Decimal(limit):
            raise ValidationError(
                f"Supplier credit limit exceeded. Limit: {float(limit):.2f}, "
                f"new balance would be {float(new_balance):.2f}"
            )
        supplier.balance = new_balance
        return new_balance

    @staticmethod
    def record_credit_sale(
        *,
        tenant_id: str,
        customer_id: str,
        amount,
        bill_id: str,
        bill_number: str,
        created_by: str,
    ):
        amount_value = PartyLedgerService._parse_amount(amount)
        existing = PartyLedgerRepository.get_by_reference(
            tenant_id,
            reference_type=REF_BILL,
            reference_id=bill_id,
            entry_type=ENTRY_CREDIT_SALE,
        )
        if existing is not None:
            return existing

        customer = PartyLedgerRepository.lock_customer(customer_id, tenant_id)
        if customer is None or not customer.is_active:
            raise ValidationError("Customer not found or inactive")

        balance_after = PartyLedgerService._apply_balance(customer, amount_value)
        entry = PartyLedgerEntry(
            id=new_uuid(),
            tenant_id=tenant_id,
            party_type=PARTY_CUSTOMER,
            party_id=customer.id,
            entry_type=ENTRY_CREDIT_SALE,
            amount=amount_value,
            balance_after=balance_after,
            reference_type=REF_BILL,
            reference_id=bill_id,
            notes=f"Credit sale {bill_number}",
            created_by=created_by,
        )
        PartyLedgerRepository.add(entry)
        AuditService.log(
            tenant_id=tenant_id,
            action="CREDIT_SALE",
            entity_type="CUSTOMER",
            entity_id=customer.id,
            new_data={
                "amount": float(amount_value),
                "balance_after": float(balance_after),
                "bill_id": bill_id,
                "bill_number": bill_number,
            },
        )
        from app.services.notification_service import NotificationService

        NotificationService.notify_credit_due(
            tenant_id=tenant_id,
            customer_id=customer.id,
            customer_name=customer.name,
            amount=amount_value,
            balance_after=balance_after,
            bill_number=bill_number,
        )
        return entry

    @staticmethod
    def record_bill_cancel_reversal(
        *,
        tenant_id: str,
        customer_id: str,
        amount,
        bill_id: str,
        bill_number: str,
        created_by: str,
        reason: str,
    ):
        amount_value = PartyLedgerService._parse_amount(amount)
        existing = PartyLedgerRepository.get_by_reference(
            tenant_id,
            reference_type=REF_BILL,
            reference_id=bill_id,
            entry_type=ENTRY_BILL_CANCEL,
        )
        if existing is not None:
            return existing

        customer = PartyLedgerRepository.lock_customer(customer_id, tenant_id)
        if customer is None:
            raise ValidationError("Customer not found")

        balance_after = PartyLedgerService._apply_balance(customer, -amount_value)
        entry = PartyLedgerEntry(
            id=new_uuid(),
            tenant_id=tenant_id,
            party_type=PARTY_CUSTOMER,
            party_id=customer.id,
            entry_type=ENTRY_BILL_CANCEL,
            amount=-amount_value,
            balance_after=balance_after,
            reference_type=REF_BILL,
            reference_id=bill_id,
            notes=f"Bill cancel {bill_number}: {reason}",
            created_by=created_by,
        )
        PartyLedgerRepository.add(entry)
        AuditService.log(
            tenant_id=tenant_id,
            action="CREDIT_BILL_CANCEL",
            entity_type="CUSTOMER",
            entity_id=customer.id,
            new_data={
                "amount": float(-amount_value),
                "balance_after": float(balance_after),
                "bill_id": bill_id,
            },
        )
        return entry

    @staticmethod
    def record_customer_payment(
        customer_id: str,
        *,
        amount,
        notes: str | None = None,
        collection_method: str | None = None,
    ):
        require_permission(PERM_CUSTOMERS_WRITE)
        ctx = require_request_context()
        amount_value = PartyLedgerService._parse_amount(amount)
        method = PartyLedgerService._normalize_collection_method(collection_method)

        customer = PartyLedgerRepository.lock_customer(customer_id, ctx.tenant_id)
        if customer is None or not customer.is_active:
            raise NotFoundError("Customer not found")

        current = money(Decimal(customer.balance or 0))
        if current <= 0:
            raise ValidationError("Customer has no outstanding balance")

        balance_after = PartyLedgerService._apply_balance(customer, -amount_value)
        payment_id = new_uuid()
        notes_text = (notes or "").strip() or None
        entry = PartyLedgerEntry(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            party_type=PARTY_CUSTOMER,
            party_id=customer.id,
            entry_type=ENTRY_PAYMENT,
            amount=-amount_value,
            balance_after=balance_after,
            reference_type=REF_PAYMENT,
            reference_id=payment_id,
            notes=notes_text or f"Collection via {method}",
            created_by=ctx.user_id,
        )
        PartyLedgerRepository.add(entry)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="COLLECT_CREDIT_PAYMENT",
            entity_type="CUSTOMER",
            entity_id=customer.id,
            new_data={
                "amount": float(amount_value),
                "balance_after": float(balance_after),
                "collection_method": method,
            },
        )
        db.session.commit()
        db.session.refresh(entry)
        return PartyLedgerService.serialize_entry(entry)

    @staticmethod
    def list_customer_ledger(customer_id: str, *, page=1, per_page=50):
        require_permission(PERM_CUSTOMERS_READ)
        ctx = require_request_context()
        customer = CustomerRepository.get_by_id_and_tenant(customer_id, ctx.tenant_id)
        if customer is None:
            raise NotFoundError("Customer not found")

        rows, total = PartyLedgerRepository.list_for_party(
            ctx.tenant_id,
            party_type=PARTY_CUSTOMER,
            party_id=customer_id,
            page=page,
            per_page=per_page,
        )
        return (
            {
                "customer_id": customer.id,
                "customer_name": customer.name,
                "balance": float(customer.balance or 0),
                "credit_limit": (
                    float(customer.credit_limit) if customer.credit_limit is not None else None
                ),
                "entries": [PartyLedgerService.serialize_entry(row) for row in rows],
            },
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def list_outstanding(*, page=1, per_page=50):
        require_permission(PERM_CUSTOMERS_READ)
        ctx = require_request_context()
        rows, total = PartyLedgerRepository.list_outstanding_customers(
            ctx.tenant_id,
            page=page,
            per_page=per_page,
        )
        from app.services.customer_service import CustomerService

        return (
            [CustomerService.serialize(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def outstanding_summary():
        require_permission(PERM_CUSTOMERS_READ)
        ctx = require_request_context()
        return PartyLedgerRepository.outstanding_summary(ctx.tenant_id)

    @staticmethod
    def serialize_entry(entry: PartyLedgerEntry):
        return {
            "id": entry.id,
            "party_type": entry.party_type,
            "party_id": entry.party_id,
            "entry_type": entry.entry_type,
            "amount": float(entry.amount),
            "balance_after": float(entry.balance_after),
            "reference_type": entry.reference_type,
            "reference_id": entry.reference_id,
            "notes": entry.notes,
            "created_by": entry.created_by,
            "created_by_name": entry.creator.name if entry.creator else None,
            "created_at": entry.created_at.isoformat() if entry.created_at else None,
        }

    @staticmethod
    def record_credit_purchase(
        *,
        tenant_id: str,
        supplier_id: str,
        amount,
        purchase_id: str,
        purchase_number: str,
        created_by: str,
    ):
        amount_value = PartyLedgerService._parse_amount(amount)
        existing = PartyLedgerRepository.get_by_reference(
            tenant_id,
            reference_type=REF_PURCHASE,
            reference_id=purchase_id,
            entry_type=ENTRY_CREDIT_PURCHASE,
        )
        if existing is not None:
            return existing

        supplier = PartyLedgerRepository.lock_supplier(supplier_id, tenant_id)
        if supplier is None or not supplier.is_active:
            raise ValidationError("Supplier not found or inactive")

        balance_after = PartyLedgerService._apply_supplier_balance(supplier, amount_value)
        entry = PartyLedgerEntry(
            id=new_uuid(),
            tenant_id=tenant_id,
            party_type=PARTY_SUPPLIER,
            party_id=supplier.id,
            entry_type=ENTRY_CREDIT_PURCHASE,
            amount=amount_value,
            balance_after=balance_after,
            reference_type=REF_PURCHASE,
            reference_id=purchase_id,
            notes=f"Credit purchase {purchase_number}",
            created_by=created_by,
        )
        PartyLedgerRepository.add(entry)
        AuditService.log(
            tenant_id=tenant_id,
            action="CREDIT_PURCHASE",
            entity_type="SUPPLIER",
            entity_id=supplier.id,
            new_data={
                "amount": float(amount_value),
                "balance_after": float(balance_after),
                "purchase_id": purchase_id,
                "purchase_number": purchase_number,
            },
        )
        return entry

    @staticmethod
    def record_purchase_cancel_reversal(
        *,
        tenant_id: str,
        supplier_id: str,
        amount,
        purchase_id: str,
        purchase_number: str,
        created_by: str,
        reason: str,
    ):
        amount_value = PartyLedgerService._parse_amount(amount)
        existing = PartyLedgerRepository.get_by_reference(
            tenant_id,
            reference_type=REF_PURCHASE,
            reference_id=purchase_id,
            entry_type=ENTRY_BILL_CANCEL,
        )
        if existing is not None:
            return existing

        # Only reverse if a credit purchase was posted.
        credit = PartyLedgerRepository.get_by_reference(
            tenant_id,
            reference_type=REF_PURCHASE,
            reference_id=purchase_id,
            entry_type=ENTRY_CREDIT_PURCHASE,
        )
        if credit is None:
            return None

        supplier = PartyLedgerRepository.lock_supplier(supplier_id, tenant_id)
        if supplier is None:
            raise ValidationError("Supplier not found")

        balance_after = PartyLedgerService._apply_supplier_balance(supplier, -amount_value)
        entry = PartyLedgerEntry(
            id=new_uuid(),
            tenant_id=tenant_id,
            party_type=PARTY_SUPPLIER,
            party_id=supplier.id,
            entry_type=ENTRY_BILL_CANCEL,
            amount=-amount_value,
            balance_after=balance_after,
            reference_type=REF_PURCHASE,
            reference_id=purchase_id,
            notes=f"Purchase cancel {purchase_number}: {reason}",
            created_by=created_by,
        )
        PartyLedgerRepository.add(entry)
        AuditService.log(
            tenant_id=tenant_id,
            action="CREDIT_PURCHASE_CANCEL",
            entity_type="SUPPLIER",
            entity_id=supplier.id,
            new_data={
                "amount": float(-amount_value),
                "balance_after": float(balance_after),
                "purchase_id": purchase_id,
            },
        )
        return entry

    @staticmethod
    def record_supplier_payment(
        supplier_id: str,
        *,
        amount,
        notes: str | None = None,
        collection_method: str | None = None,
    ):
        require_permission(PERM_SUPPLIERS_WRITE)
        ctx = require_request_context()
        amount_value = PartyLedgerService._parse_amount(amount)
        method = PartyLedgerService._normalize_collection_method(collection_method)

        supplier = PartyLedgerRepository.lock_supplier(supplier_id, ctx.tenant_id)
        if supplier is None or not supplier.is_active:
            raise NotFoundError("Supplier not found")

        current = money(Decimal(getattr(supplier, "balance", 0) or 0))
        if current <= 0:
            raise ValidationError("Supplier has no outstanding balance")

        balance_after = PartyLedgerService._apply_supplier_balance(supplier, -amount_value)
        payment_id = new_uuid()
        notes_text = (notes or "").strip() or None
        entry = PartyLedgerEntry(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            party_type=PARTY_SUPPLIER,
            party_id=supplier.id,
            entry_type=ENTRY_PAYMENT,
            amount=-amount_value,
            balance_after=balance_after,
            reference_type=REF_PAYMENT,
            reference_id=payment_id,
            notes=notes_text or f"Payment to supplier via {method}",
            created_by=ctx.user_id,
        )
        PartyLedgerRepository.add(entry)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="PAY_SUPPLIER_CREDIT",
            entity_type="SUPPLIER",
            entity_id=supplier.id,
            new_data={
                "amount": float(amount_value),
                "balance_after": float(balance_after),
                "collection_method": method,
            },
        )
        db.session.commit()
        db.session.refresh(entry)
        return PartyLedgerService.serialize_entry(entry)

    @staticmethod
    def list_supplier_ledger(supplier_id: str, *, page=1, per_page=50):
        require_permission(PERM_SUPPLIERS_READ)
        ctx = require_request_context()
        supplier = SupplierRepository.get_by_id_and_tenant(supplier_id, ctx.tenant_id)
        if supplier is None:
            raise NotFoundError("Supplier not found")

        rows, total = PartyLedgerRepository.list_for_party(
            ctx.tenant_id,
            party_type=PARTY_SUPPLIER,
            party_id=supplier_id,
            page=page,
            per_page=per_page,
        )
        return (
            {
                "supplier_id": supplier.id,
                "supplier_name": supplier.name,
                "balance": float(getattr(supplier, "balance", 0) or 0),
                "credit_limit": (
                    float(supplier.credit_limit)
                    if getattr(supplier, "credit_limit", None) is not None
                    else None
                ),
                "entries": [PartyLedgerService.serialize_entry(row) for row in rows],
            },
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def list_supplier_outstanding(*, page=1, per_page=50):
        require_permission(PERM_SUPPLIERS_READ)
        ctx = require_request_context()
        rows, total = PartyLedgerRepository.list_outstanding_suppliers(
            ctx.tenant_id,
            page=page,
            per_page=per_page,
        )
        from app.services.supplier_service import SupplierService

        return (
            [SupplierService.serialize(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def empty_aging_buckets() -> dict:
        return {
            "0_30": 0.0,
            "31_60": 0.0,
            "61_90": 0.0,
            "90_plus": 0.0,
        }

    @staticmethod
    def _bucket_key(age_days: int) -> str:
        if age_days <= 30:
            return "0_30"
        if age_days <= 60:
            return "31_60"
        if age_days <= 90:
            return "61_90"
        return "90_plus"

    @staticmethod
    def age_open_charges(
        entries: list,
        *,
        as_of,
    ) -> dict:
        """
        FIFO-age remaining charge amounts after applying payments/cancels.
        Charge entries: CREDIT_SALE / CREDIT_PURCHASE (positive amounts).
        Reductions: PAYMENT / BILL_CANCEL (negative amounts).
        """
        from datetime import datetime as dt

        opens: list[list] = []  # [created_at, remaining]
        for entry in entries:
            amount = money(Decimal(entry.amount or 0))
            if amount > 0:
                opens.append([entry.created_at, amount])
            elif amount < 0:
                pay = -amount
                for open_row in opens:
                    if pay <= 0:
                        break
                    take = min(open_row[1], pay)
                    open_row[1] = money(open_row[1] - take)
                    pay = money(pay - take)

        buckets = PartyLedgerService.empty_aging_buckets()
        total = Decimal("0.00")
        as_of_date = as_of.date() if isinstance(as_of, dt) else as_of
        for created_at, remaining in opens:
            if remaining <= 0:
                continue
            created_date = created_at.date() if hasattr(created_at, "date") else created_at
            age_days = max((as_of_date - created_date).days, 0)
            key = PartyLedgerService._bucket_key(age_days)
            buckets[key] = float(money(Decimal(str(buckets[key])) + remaining))
            total += remaining
        buckets["total"] = float(money(total))
        return buckets

    @staticmethod
    def aged_outstanding_report(*, as_of=None, party_type: str | None = None) -> dict:
        """Customer + supplier outstanding with aging buckets (BIZ-54)."""
        from datetime import datetime, timezone

        from app.services.customer_service import CustomerService
        from app.services.supplier_service import SupplierService

        ctx = require_request_context()
        as_of_dt = as_of or datetime.now(timezone.utc).replace(tzinfo=None)
        if isinstance(as_of_dt, str):
            try:
                as_of_dt = datetime.fromisoformat(as_of_dt.replace("Z", ""))
            except ValueError as exc:
                raise ValidationError("as_of must be an ISO date or datetime") from exc

        include_customers = party_type in (None, "", "all", "customer", "customers")
        include_suppliers = party_type in (None, "", "all", "supplier", "suppliers")
        if party_type and party_type not in (
            "all",
            "customer",
            "customers",
            "supplier",
            "suppliers",
        ):
            raise ValidationError("party_type must be customer, supplier, or all")

        def _sum_buckets(rows: list[dict]) -> dict:
            summary = PartyLedgerService.empty_aging_buckets()
            summary["total"] = 0.0
            summary["party_count"] = 0
            for row in rows:
                aging = row["aging"]
                for key in ("0_30", "31_60", "61_90", "90_plus", "total"):
                    summary[key] = float(
                        money(Decimal(str(summary[key])) + Decimal(str(aging.get(key, 0))))
                    )
                summary["party_count"] += 1
            return summary

        customers_out = []
        if include_customers:
            parties = PartyLedgerRepository.list_all_outstanding_customers(ctx.tenant_id)
            for party in parties:
                entries = PartyLedgerRepository.list_all_for_party(
                    ctx.tenant_id, party_type=PARTY_CUSTOMER, party_id=party.id
                )
                aging = PartyLedgerService.age_open_charges(entries, as_of=as_of_dt)
                customers_out.append(
                    {
                        **CustomerService.serialize(party),
                        "aging": aging,
                    }
                )

        suppliers_out = []
        if include_suppliers:
            parties = PartyLedgerRepository.list_all_outstanding_suppliers(ctx.tenant_id)
            for party in parties:
                entries = PartyLedgerRepository.list_all_for_party(
                    ctx.tenant_id, party_type=PARTY_SUPPLIER, party_id=party.id
                )
                aging = PartyLedgerService.age_open_charges(entries, as_of=as_of_dt)
                suppliers_out.append(
                    {
                        **SupplierService.serialize(party),
                        "aging": aging,
                    }
                )

        return {
            "as_of": as_of_dt.date().isoformat()
            if hasattr(as_of_dt, "date")
            else str(as_of_dt),
            "buckets": ["0_30", "31_60", "61_90", "90_plus"],
            "bucket_labels": {
                "0_30": "0–30 days",
                "31_60": "31–60 days",
                "61_90": "61–90 days",
                "90_plus": "90+ days",
            },
            "customers": {
                "summary": _sum_buckets(customers_out),
                "parties": customers_out,
            },
            "suppliers": {
                "summary": _sum_buckets(suppliers_out),
                "parties": suppliers_out,
            },
        }

