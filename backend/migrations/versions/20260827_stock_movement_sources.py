"""Widen stock_movements.source CHECK for RECIPE and industry sources.

Revision ID: 20260827_stock_movement_sources
Revises: 20260827_hotel_billing_settings_audit_delete
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "20260827_stock_movement_sources"
down_revision = "20260827_hotel_billing_settings_audit_delete"
branch_labels = None
depends_on = None

ALLOWED_SOURCES = (
    "BILL",
    "CANCEL",
    "ADJUST",
    "ITEM_UPDATE",
    "RECEIVE",
    "PURCHASE",
    "PURCHASE_CANCEL",
    "RECIPE",
    "WASTAGE",
    "RETURN",
    "EXCHANGE",
    "TRANSFER_OUT",
    "TRANSFER_IN",
    "PRODUCTION",
)

_SOURCE_LIST = ", ".join(f"'{s}'" for s in ALLOWED_SOURCES)


def _check_clause(name: str) -> str | None:
    bind = op.get_bind()
    row = bind.execute(
        text(
            """
            SELECT CHECK_CLAUSE
            FROM information_schema.CHECK_CONSTRAINTS
            WHERE CONSTRAINT_SCHEMA = DATABASE()
              AND CONSTRAINT_NAME = :name
            """
        ),
        {"name": name},
    ).fetchone()
    return row[0] if row else None


def _drop_check(table: str, name: str) -> None:
    if _check_clause(name) is None:
        return
    for stmt in (
        f"ALTER TABLE `{table}` DROP CONSTRAINT `{name}`",
        f"ALTER TABLE `{table}` DROP CHECK `{name}`",
    ):
        try:
            op.execute(text(stmt))
            return
        except Exception:
            continue


def upgrade() -> None:
    clause = _check_clause("chk_stock_movements_source") or ""
    if all(source in clause.upper() for source in ALLOWED_SOURCES):
        return
    _drop_check("stock_movements", "chk_stock_movements_source")
    op.execute(
        text(
            f"""
            ALTER TABLE stock_movements
            ADD CONSTRAINT chk_stock_movements_source
            CHECK (source IN ({_SOURCE_LIST}))
            """
        )
    )


def downgrade() -> None:
    _drop_check("stock_movements", "chk_stock_movements_source")
    op.execute(
        text(
            """
            ALTER TABLE stock_movements
            ADD CONSTRAINT chk_stock_movements_source
            CHECK (source IN ('BILL', 'CANCEL', 'ADJUST', 'ITEM_UPDATE', 'RECEIVE'))
            """
        )
    )
