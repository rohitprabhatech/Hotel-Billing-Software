"""Customer credit / party ledger business logic (BIZ-09)."""

from decimal import Decimal, InvalidOperation

from app.constants.permissions import PERM_CUSTOMERS_READ, PERM_CUSTOMERS_WRITE
from app.constants.payments import PAYMENT_CASH, PAYMENT_CREDIT, PAYMENT_ONLINE
from app.extensions import db
from app.models.party_ledger_entry import (
    ENTRY_BILL_CANCEL,
    ENTRY_CREDIT_SALE,
    ENTRY_PAYMENT,
    PARTY_CUSTOMER,
    REF_BILL,
    REF_PAYMENT,
    PartyLedgerEntry,
)
from app.repositories.customer_repository import CustomerRepository
from app.repositories.party_ledger_repository import PartyLedgerRepository
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
