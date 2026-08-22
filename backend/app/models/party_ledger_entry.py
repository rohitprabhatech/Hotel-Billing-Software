"""Shared party ledger entries (customer credit / udhari — BIZ-09)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import utcnow

PARTY_CUSTOMER = "CUSTOMER"
PARTY_SUPPLIER = "SUPPLIER"

ENTRY_CREDIT_SALE = "CREDIT_SALE"
ENTRY_PAYMENT = "PAYMENT"
ENTRY_BILL_CANCEL = "BILL_CANCEL"

REF_BILL = "BILL"
REF_PAYMENT = "PAYMENT"


class PartyLedgerEntry(db.Model):
    __tablename__ = "party_ledger_entries"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "reference_type",
            "reference_id",
            "entry_type",
            name="uq_party_ledger_ref_entry",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    party_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    party_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    entry_type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    balance_after: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    reference_type: Mapped[str | None] = mapped_column(String(20))
    reference_id: Mapped[str | None] = mapped_column(String(36))
    notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utcnow
    )

    creator = relationship("User", foreign_keys=[created_by])
