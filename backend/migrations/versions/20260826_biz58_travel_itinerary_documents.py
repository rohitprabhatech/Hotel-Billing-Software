"""BIZ-58: travel itinerary items and booking document metadata.

Revision ID: 20260826_biz58_travel_itinerary_documents
Revises: 20260826_biz57_travel_bookings
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260826_biz58_travel_itinerary_documents"
down_revision = "20260826_biz57_travel_bookings"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if not _has_table("travel_itinerary_items"):
        op.create_table(
            "travel_itinerary_items",
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
            sa.Column("item_type", sa.String(20), nullable=False, server_default="ACTIVITY"),
            sa.Column("day_number", sa.Integer(), nullable=True),
            sa.Column("title", sa.String(200), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("location", sa.String(200), nullable=True),
            sa.Column("vendor_name", sa.String(160), nullable=True),
            sa.Column("confirmation_ref", sa.String(120), nullable=True),
            sa.Column("start_at", sa.DateTime(), nullable=True),
            sa.Column("end_at", sa.DateTime(), nullable=True),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )
        op.create_index(
            "ix_travel_itinerary_items_tenant_id",
            "travel_itinerary_items",
            ["tenant_id"],
        )
        op.create_index(
            "ix_travel_itinerary_items_booking_id",
            "travel_itinerary_items",
            ["booking_id"],
        )

    if not _has_table("travel_booking_documents"):
        op.create_table(
            "travel_booking_documents",
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
            sa.Column("document_type", sa.String(30), nullable=False, server_default="OTHER"),
            sa.Column("holder_name", sa.String(120), nullable=True),
            sa.Column("document_number", sa.String(80), nullable=True),
            sa.Column("issued_country", sa.String(80), nullable=True),
            sa.Column("expiry_date", sa.Date(), nullable=True),
            sa.Column("file_name", sa.String(255), nullable=True),
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
            "ix_travel_booking_documents_tenant_id",
            "travel_booking_documents",
            ["tenant_id"],
        )
        op.create_index(
            "ix_travel_booking_documents_booking_id",
            "travel_booking_documents",
            ["booking_id"],
        )


def downgrade() -> None:
    if _has_table("travel_booking_documents"):
        op.drop_table("travel_booking_documents")
    if _has_table("travel_itinerary_items"):
        op.drop_table("travel_itinerary_items")
