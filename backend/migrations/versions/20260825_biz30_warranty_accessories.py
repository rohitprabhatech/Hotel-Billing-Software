"""Warranty fields and item accessory links (BIZ-30).

Revision ID: 20260825_biz30_warranty_accessories
Revises: 20260825_audit_db_hardening
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260825_biz30_warranty_accessories"
down_revision = "20260825_audit_db_hardening"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def _has_column(table: str, column: str) -> bool:
    cols = [row["name"] for row in inspect(op.get_bind()).get_columns(table)]
    return column in cols


def upgrade() -> None:
    if not _has_column("items", "warranty_months"):
        op.add_column("items", sa.Column("warranty_months", sa.Integer(), nullable=True))
    if not _has_column("serial_units", "warranty_months"):
        op.add_column("serial_units", sa.Column("warranty_months", sa.Integer(), nullable=True))
    if not _has_column("bill_items", "warranty_until"):
        op.add_column("bill_items", sa.Column("warranty_until", sa.Date(), nullable=True))

    if not _has_table("item_accessories"):
        op.create_table(
            "item_accessories",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column(
                "item_id",
                sa.String(36),
                sa.ForeignKey("items.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "accessory_item_id",
                sa.String(36),
                sa.ForeignKey("items.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint(
                "tenant_id",
                "item_id",
                "accessory_item_id",
                name="uq_item_accessories_tenant_item_accessory",
            ),
        )
        op.create_index("ix_item_accessories_tenant_id", "item_accessories", ["tenant_id"])
        op.create_index("ix_item_accessories_item_id", "item_accessories", ["item_id"])
        op.create_index(
            "ix_item_accessories_accessory_item_id",
            "item_accessories",
            ["accessory_item_id"],
        )


def downgrade() -> None:
    if _has_table("item_accessories"):
        op.drop_table("item_accessories")
    if _has_column("bill_items", "warranty_until"):
        op.drop_column("bill_items", "warranty_until")
    if _has_column("serial_units", "warranty_months"):
        op.drop_column("serial_units", "warranty_months")
    if _has_column("items", "warranty_months"):
        op.drop_column("items", "warranty_months")
