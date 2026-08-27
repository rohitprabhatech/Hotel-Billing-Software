"""Cafe coupons + bill coupon columns (Sprint 5).

Revision ID: 20260827_cafe_coupons
Revises: 20260827_stock_movement_sources
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260827_cafe_coupons"
down_revision = "20260827_stock_movement_sources"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def _has_column(table: str, column: str) -> bool:
    cols = [row["name"] for row in inspect(op.get_bind()).get_columns(table)]
    return column in cols


def upgrade() -> None:
    if not _has_table("coupons"):
        op.create_table(
            "coupons",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("code", sa.String(40), nullable=False),
            sa.Column("name", sa.String(120), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("discount_type", sa.String(16), nullable=False, server_default="amount"),
            sa.Column("discount_value", sa.Numeric(12, 2), nullable=False),
            sa.Column("min_order_amount", sa.Numeric(12, 2), nullable=True),
            sa.Column("max_discount_amount", sa.Numeric(12, 2), nullable=True),
            sa.Column("starts_on", sa.Date(), nullable=True),
            sa.Column("ends_on", sa.Date(), nullable=True),
            sa.Column("usage_limit", sa.Integer(), nullable=True),
            sa.Column("usage_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column(
                "created_by",
                sa.String(36),
                sa.ForeignKey("users.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint("tenant_id", "code", name="uq_coupons_tenant_code"),
        )
        op.create_index("ix_coupons_tenant_id", "coupons", ["tenant_id"])

    if not _has_table("coupon_redemptions"):
        op.create_table(
            "coupon_redemptions",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column(
                "coupon_id",
                sa.String(36),
                sa.ForeignKey("coupons.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column(
                "bill_id",
                sa.String(36),
                sa.ForeignKey("bills.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column(
                "order_id",
                sa.String(36),
                sa.ForeignKey("orders.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("discount_applied", sa.Numeric(12, 2), nullable=False),
            sa.Column(
                "redeemed_by",
                sa.String(36),
                sa.ForeignKey("users.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_coupon_redemptions_tenant_id", "coupon_redemptions", ["tenant_id"])
        op.create_index("ix_coupon_redemptions_coupon_id", "coupon_redemptions", ["coupon_id"])
        op.create_index("ix_coupon_redemptions_bill_id", "coupon_redemptions", ["bill_id"])
        op.create_index("ix_coupon_redemptions_order_id", "coupon_redemptions", ["order_id"])

    if not _has_column("bills", "coupon_id"):
        op.add_column(
            "bills",
            sa.Column(
                "coupon_id",
                sa.String(36),
                sa.ForeignKey("coupons.id", ondelete="SET NULL"),
                nullable=True,
            ),
        )
        op.create_index("ix_bills_coupon_id", "bills", ["coupon_id"])
    if not _has_column("bills", "coupon_code"):
        op.add_column("bills", sa.Column("coupon_code", sa.String(40), nullable=True))
    if not _has_column("bills", "coupon_discount"):
        op.add_column(
            "bills",
            sa.Column(
                "coupon_discount",
                sa.Numeric(12, 2),
                nullable=False,
                server_default="0",
            ),
        )


def downgrade() -> None:
    if _has_column("bills", "coupon_discount"):
        op.drop_column("bills", "coupon_discount")
    if _has_column("bills", "coupon_code"):
        op.drop_column("bills", "coupon_code")
    if _has_column("bills", "coupon_id"):
        op.drop_index("ix_bills_coupon_id", table_name="bills")
        op.drop_column("bills", "coupon_id")
    if _has_table("coupon_redemptions"):
        op.drop_table("coupon_redemptions")
    if _has_table("coupons"):
        op.drop_table("coupons")
