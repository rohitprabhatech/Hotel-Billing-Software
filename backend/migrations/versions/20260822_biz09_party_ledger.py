"""Party ledger + customer balance cache (BIZ-09).

Revision ID: 20260822_biz09_party_ledger
Revises: 20260822_biz08_barcode_uom
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260822_biz09_party_ledger"
down_revision = "20260822_biz08_barcode_uom"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def _has_column(table: str, column: str) -> bool:
    return column in {col["name"] for col in inspect(op.get_bind()).get_columns(table)}


def upgrade() -> None:
    if not _has_column("customers", "balance"):
        op.add_column(
            "customers",
            sa.Column("balance", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        )
        op.alter_column("customers", "balance", server_default=None)

    if not _has_table("party_ledger_entries"):
        op.create_table(
            "party_ledger_entries",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id"), nullable=False),
            sa.Column("party_type", sa.String(20), nullable=False),
            sa.Column("party_id", sa.String(36), nullable=False),
            sa.Column("entry_type", sa.String(20), nullable=False),
            sa.Column("amount", sa.Numeric(12, 2), nullable=False),
            sa.Column("balance_after", sa.Numeric(12, 2), nullable=False),
            sa.Column("reference_type", sa.String(20), nullable=True),
            sa.Column("reference_id", sa.String(36), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.UniqueConstraint(
                "tenant_id",
                "reference_type",
                "reference_id",
                "entry_type",
                name="uq_party_ledger_ref_entry",
            ),
        )
        op.create_index("ix_party_ledger_entries_tenant_id", "party_ledger_entries", ["tenant_id"])
        op.create_index("ix_party_ledger_entries_party_type", "party_ledger_entries", ["party_type"])
        op.create_index("ix_party_ledger_entries_party_id", "party_ledger_entries", ["party_id"])


def downgrade() -> None:
    if _has_table("party_ledger_entries"):
        op.drop_index("ix_party_ledger_entries_party_id", table_name="party_ledger_entries")
        op.drop_index("ix_party_ledger_entries_party_type", table_name="party_ledger_entries")
        op.drop_index("ix_party_ledger_entries_tenant_id", table_name="party_ledger_entries")
        op.drop_table("party_ledger_entries")
    if _has_column("customers", "balance"):
        op.drop_column("customers", "balance")
