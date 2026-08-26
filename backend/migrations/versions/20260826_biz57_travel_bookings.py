"""BIZ-57: travel bookings and payments.

Revision ID: 20260826_biz57_travel_bookings
Revises: 20260826_biz56_tour_packages
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260826_biz57_travel_bookings"
down_revision = "20260826_biz56_tour_packages"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if not _has_table("travel_booking_number_counters"):
        op.create_table(
            "travel_booking_number_counters",
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="CASCADE"),
                primary_key=True,
            ),
            sa.Column("next_value", sa.Integer(), nullable=False, server_default="1"),
        )

    if not _has_table("travel_bookings"):
        op.create_table(
            "travel_bookings",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("booking_number", sa.String(30), nullable=False),
            sa.Column("booking_sequence", sa.Integer(), nullable=False),
            sa.Column(
                "package_id",
                sa.String(36),
                sa.ForeignKey("tour_packages.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("package_name", sa.String(200), nullable=False),
            sa.Column(
                "customer_id",
                sa.String(36),
                sa.ForeignKey("customers.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("customer_name", sa.String(120), nullable=True),
            sa.Column("customer_phone", sa.String(30), nullable=True),
            sa.Column("pax_count", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("travel_start_at", sa.DateTime(), nullable=True),
            sa.Column("travel_end_at", sa.DateTime(), nullable=True),
            sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
            sa.Column("advance_paid", sa.Numeric(12, 2), nullable=False, server_default="0"),
            sa.Column("status", sa.String(20), nullable=False, server_default="BOOKED"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column(
                "bill_id",
                sa.String(36),
                sa.ForeignKey("bills.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("completed_at", sa.DateTime(), nullable=True),
            sa.Column(
                "created_by",
                sa.String(36),
                sa.ForeignKey("users.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.UniqueConstraint(
                "tenant_id", "booking_number", name="uq_travel_bookings_tenant_number"
            ),
        )
        op.create_index("ix_travel_bookings_tenant_id", "travel_bookings", ["tenant_id"])
        op.create_index("ix_travel_bookings_package_id", "travel_bookings", ["package_id"])
        op.create_index("ix_travel_bookings_customer_id", "travel_bookings", ["customer_id"])
        op.create_index("ix_travel_bookings_bill_id", "travel_bookings", ["bill_id"])
        op.create_index(
            "ix_travel_bookings_travel_start_at", "travel_bookings", ["travel_start_at"]
        )

    if not _has_table("travel_booking_payments"):
        op.create_table(
            "travel_booking_payments",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column(
                "booking_id",
                sa.String(36),
                sa.ForeignKey("travel_bookings.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("amount", sa.Numeric(12, 2), nullable=False),
            sa.Column("payment_method", sa.String(30), nullable=False, server_default="cash"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column(
                "created_by",
                sa.String(36),
                sa.ForeignKey("users.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index(
            "ix_travel_booking_payments_tenant_id", "travel_booking_payments", ["tenant_id"]
        )
        op.create_index(
            "ix_travel_booking_payments_booking_id", "travel_booking_payments", ["booking_id"]
        )


def downgrade() -> None:
    if _has_table("travel_booking_payments"):
        op.drop_table("travel_booking_payments")
    if _has_table("travel_bookings"):
        op.drop_table("travel_bookings")
    if _has_table("travel_booking_number_counters"):
        op.drop_table("travel_booking_number_counters")
