"""BIZ-59: travel agents, booking agent link, commission entries.

Revision ID: 20260826_biz59_travel_agent_commission
Revises: 20260826_biz58_travel_itinerary_documents
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20260826_biz59_travel_agent_commission"
down_revision = "20260826_biz58_travel_itinerary_documents"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def _has_column(table: str, column: str) -> bool:
    cols = {c["name"] for c in inspect(op.get_bind()).get_columns(table)}
    return column in cols


def upgrade() -> None:
    if not _has_table("travel_agents"):
        op.create_table(
            "travel_agents",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("code", sa.String(40), nullable=False),
            sa.Column("name", sa.String(120), nullable=False),
            sa.Column("phone", sa.String(30), nullable=True),
            sa.Column("email", sa.String(160), nullable=True),
            sa.Column(
                "commission_percent",
                sa.Numeric(6, 2),
                nullable=False,
                server_default="0",
            ),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column(
                "created_by",
                sa.String(36),
                sa.ForeignKey("users.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.UniqueConstraint("tenant_id", "code", name="uq_travel_agents_tenant_code"),
        )
        op.create_index("ix_travel_agents_tenant_id", "travel_agents", ["tenant_id"])

    if _has_table("travel_bookings") and not _has_column("travel_bookings", "agent_id"):
        with op.batch_alter_table("travel_bookings") as batch:
            batch.add_column(sa.Column("agent_id", sa.String(36), nullable=True))
            batch.create_foreign_key(
                "fk_travel_bookings_agent_id",
                "travel_agents",
                ["agent_id"],
                ["id"],
                ondelete="SET NULL",
            )
            batch.create_index("ix_travel_bookings_agent_id", ["agent_id"])

    if not _has_table("travel_commission_entries"):
        op.create_table(
            "travel_commission_entries",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column(
                "tenant_id",
                sa.String(36),
                sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column(
                "agent_id",
                sa.String(36),
                sa.ForeignKey("travel_agents.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column(
                "booking_id",
                sa.String(36),
                sa.ForeignKey("travel_bookings.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("booking_number", sa.String(30), nullable=False),
            sa.Column("booking_total", sa.Numeric(12, 2), nullable=False),
            sa.Column("commission_percent", sa.Numeric(6, 2), nullable=False),
            sa.Column("commission_amount", sa.Numeric(12, 2), nullable=False),
            sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column(
                "created_by",
                sa.String(36),
                sa.ForeignKey("users.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.Column("paid_at", sa.DateTime(), nullable=True),
            sa.UniqueConstraint(
                "tenant_id",
                "booking_id",
                name="uq_travel_commission_entries_tenant_booking",
            ),
        )
        op.create_index(
            "ix_travel_commission_entries_tenant_id",
            "travel_commission_entries",
            ["tenant_id"],
        )
        op.create_index(
            "ix_travel_commission_entries_agent_id",
            "travel_commission_entries",
            ["agent_id"],
        )
        op.create_index(
            "ix_travel_commission_entries_booking_id",
            "travel_commission_entries",
            ["booking_id"],
        )


def downgrade() -> None:
    if _has_table("travel_commission_entries"):
        op.drop_table("travel_commission_entries")
    if _has_table("travel_bookings") and _has_column("travel_bookings", "agent_id"):
        with op.batch_alter_table("travel_bookings") as batch:
            batch.drop_constraint("fk_travel_bookings_agent_id", type_="foreignkey")
            batch.drop_index("ix_travel_bookings_agent_id")
            batch.drop_column("agent_id")
    if _has_table("travel_agents"):
        op.drop_table("travel_agents")
