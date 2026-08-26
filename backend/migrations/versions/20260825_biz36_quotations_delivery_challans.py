"""BIZ-36: quotations and delivery challans.

Revision ID: 20260825_biz36_quotations_delivery_challans
Revises: 20260825_biz35_sale_uom_measurement
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260825_biz36_quotations_delivery_challans"
down_revision = "20260825_biz35_sale_uom_measurement"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if not _has_table("quotation_number_counters"):
        op.create_table(
            "quotation_number_counters",
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                primary_key=True,
            ),
            sa.Column("next_value", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )

    if not _has_table("quotations"):
        op.create_table(
            "quotations",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("quotation_number", sa.String(50), nullable=False),
            sa.Column("quotation_sequence", sa.Integer(), nullable=False),
            sa.Column(
                "customer_id",
                sa.String(36),
                sa.ForeignKey("customers.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("customer_name", sa.String(120), nullable=True),
            sa.Column("customer_phone", sa.String(30), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("valid_until", sa.Date(), nullable=True),
            sa.Column("status", sa.String(20), nullable=False, server_default="DRAFT"),
            sa.Column("discount", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("subtotal", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("taxable_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("cgst_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("sgst_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("gst_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("grand_total", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column(
                "bill_id",
                sa.String(36),
                sa.ForeignKey("bills.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column(
                "created_by",
                sa.String(36),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint("tenant_id", "quotation_number", name="uq_quotations_tenant_number"),
        )
        op.create_index("ix_quotations_tenant_id", "quotations", ["tenant_id"])
        op.create_index("ix_quotations_customer_id", "quotations", ["customer_id"])
        op.create_index("ix_quotations_bill_id", "quotations", ["bill_id"])

    if not _has_table("quotation_items"):
        op.create_table(
            "quotation_items",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column(
                "quotation_id",
                sa.String(36),
                sa.ForeignKey("quotations.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "item_id",
                sa.String(36),
                sa.ForeignKey("items.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("item_name", sa.String(200), nullable=False),
            sa.Column("quantity", sa.Numeric(10, 3), nullable=False),
            sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
            sa.Column("gst_percentage", sa.Numeric(5, 2), nullable=False, server_default="0"),
            sa.Column("discount", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("taxable_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("cgst_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("sgst_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("total", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("uom", sa.String(16), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_quotation_items_tenant_id", "quotation_items", ["tenant_id"])
        op.create_index("ix_quotation_items_quotation_id", "quotation_items", ["quotation_id"])

    if not _has_table("delivery_challan_number_counters"):
        op.create_table(
            "delivery_challan_number_counters",
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                primary_key=True,
            ),
            sa.Column("next_value", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )

    if not _has_table("delivery_challans"):
        op.create_table(
            "delivery_challans",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("challan_number", sa.String(50), nullable=False),
            sa.Column("challan_sequence", sa.Integer(), nullable=False),
            sa.Column(
                "customer_id",
                sa.String(36),
                sa.ForeignKey("customers.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("customer_name", sa.String(120), nullable=True),
            sa.Column("customer_phone", sa.String(30), nullable=True),
            sa.Column("delivery_address", sa.Text(), nullable=True),
            sa.Column("vehicle_number", sa.String(40), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("status", sa.String(20), nullable=False, server_default="DRAFT"),
            sa.Column(
                "quotation_id",
                sa.String(36),
                sa.ForeignKey("quotations.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column(
                "bill_id",
                sa.String(36),
                sa.ForeignKey("bills.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("printed_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column(
                "created_by",
                sa.String(36),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint(
                "tenant_id", "challan_number", name="uq_delivery_challans_tenant_number"
            ),
        )
        op.create_index("ix_delivery_challans_tenant_id", "delivery_challans", ["tenant_id"])
        op.create_index("ix_delivery_challans_customer_id", "delivery_challans", ["customer_id"])
        op.create_index("ix_delivery_challans_quotation_id", "delivery_challans", ["quotation_id"])
        op.create_index("ix_delivery_challans_bill_id", "delivery_challans", ["bill_id"])

    if not _has_table("delivery_challan_items"):
        op.create_table(
            "delivery_challan_items",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column(
                "challan_id",
                sa.String(36),
                sa.ForeignKey("delivery_challans.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "item_id",
                sa.String(36),
                sa.ForeignKey("items.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("item_name", sa.String(200), nullable=False),
            sa.Column("quantity", sa.Numeric(10, 3), nullable=False),
            sa.Column("unit_price", sa.Numeric(12, 2), nullable=True),
            sa.Column("uom", sa.String(16), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index(
            "ix_delivery_challan_items_tenant_id", "delivery_challan_items", ["tenant_id"]
        )
        op.create_index(
            "ix_delivery_challan_items_challan_id", "delivery_challan_items", ["challan_id"]
        )


def downgrade() -> None:
    for table, indexes in (
        ("delivery_challan_items", ("ix_delivery_challan_items_challan_id", "ix_delivery_challan_items_tenant_id")),
        ("delivery_challans", ("ix_delivery_challans_bill_id", "ix_delivery_challans_quotation_id", "ix_delivery_challans_customer_id", "ix_delivery_challans_tenant_id")),
        ("quotation_items", ("ix_quotation_items_quotation_id", "ix_quotation_items_tenant_id")),
        ("quotations", ("ix_quotations_bill_id", "ix_quotations_customer_id", "ix_quotations_tenant_id")),
    ):
        if _has_table(table):
            for index in indexes:
                try:
                    op.drop_index(index, table_name=table)
                except Exception:
                    pass
            op.drop_table(table)
    if _has_table("delivery_challan_number_counters"):
        op.drop_table("delivery_challan_number_counters")
    if _has_table("quotation_number_counters"):
        op.drop_table("quotation_number_counters")
