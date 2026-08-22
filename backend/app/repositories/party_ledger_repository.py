"""Party ledger data access."""

from decimal import Decimal

from sqlalchemy import func

from app.extensions import db
from app.models.customer import Customer
from app.models.party_ledger_entry import (
    ENTRY_BILL_CANCEL,
    ENTRY_CREDIT_SALE,
    ENTRY_PAYMENT,
    PARTY_CUSTOMER,
    PartyLedgerEntry,
)


class PartyLedgerRepository:
    @staticmethod
    def get_by_reference(
        tenant_id: str,
        *,
        reference_type: str,
        reference_id: str,
        entry_type: str,
    ) -> PartyLedgerEntry | None:
        return (
            db.session.query(PartyLedgerEntry)
            .filter(
                PartyLedgerEntry.tenant_id == tenant_id,
                PartyLedgerEntry.reference_type == reference_type,
                PartyLedgerEntry.reference_id == reference_id,
                PartyLedgerEntry.entry_type == entry_type,
            )
            .first()
        )

    @staticmethod
    def lock_customer(customer_id: str, tenant_id: str) -> Customer | None:
        return (
            db.session.query(Customer)
            .filter(Customer.id == customer_id, Customer.tenant_id == tenant_id)
            .with_for_update()
            .first()
        )

    @staticmethod
    def add(entry: PartyLedgerEntry) -> PartyLedgerEntry:
        db.session.add(entry)
        return entry

    @staticmethod
    def list_for_party(
        tenant_id: str,
        *,
        party_type: str,
        party_id: str,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[PartyLedgerEntry], int]:
        query = db.session.query(PartyLedgerEntry).filter(
            PartyLedgerEntry.tenant_id == tenant_id,
            PartyLedgerEntry.party_type == party_type,
            PartyLedgerEntry.party_id == party_id,
        )
        total = query.with_entities(func.count(PartyLedgerEntry.id)).scalar() or 0
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 50), 1), 100)
        rows = (
            query.order_by(PartyLedgerEntry.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, int(total)

    @staticmethod
    def list_outstanding_customers(
        tenant_id: str,
        *,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[Customer], int]:
        query = db.session.query(Customer).filter(
            Customer.tenant_id == tenant_id,
            Customer.is_active.is_(True),
            Customer.balance > Decimal("0.00"),
        )
        total = query.with_entities(func.count(Customer.id)).scalar() or 0
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 50), 1), 100)
        rows = (
            query.order_by(Customer.balance.desc(), Customer.name.asc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, int(total)
