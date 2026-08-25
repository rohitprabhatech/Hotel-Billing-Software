"""Audit hardening: inventory CHECKs + composite indexes (non-destructive).

Revision ID: 20260825_audit_db_hardening
Revises: 20260825_biz29_serial_units
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import inspect, text

revision = "20260825_audit_db_hardening"
down_revision = "20260825_biz29_serial_units"
branch_labels = None
depends_on = None


def _has_index(table: str, name: str) -> bool:
    bind = op.get_bind()
    indexes = inspect(bind).get_indexes(table)
    return any(idx.get("name") == name for idx in indexes)


def _has_check(name: str) -> bool:
    bind = op.get_bind()
    try:
        rows = bind.execute(
            text(
                "SELECT CONSTRAINT_NAME FROM information_schema.CHECK_CONSTRAINTS "
                "WHERE CONSTRAINT_SCHEMA = DATABASE() AND CONSTRAINT_NAME = :n"
            ),
            {"n": name},
        ).fetchall()
        return bool(rows)
    except Exception:
        return False


def _add_check(table: str, name: str, clause: str) -> None:
    if _has_check(name):
        return
    op.execute(text(f"ALTER TABLE `{table}` ADD CONSTRAINT `{name}` CHECK ({clause})"))


def _create_index(name: str, table: str, columns: list[str]) -> None:
    if _has_index(table, name):
        return
    op.create_index(name, table, columns)


def upgrade() -> None:
    # DB-level stock floors (app already rejects oversell; CHECK is a safety net).
    _add_check("item_variants", "chk_item_variants_stock", "stock_quantity >= 0")
    _add_check("item_batches", "chk_item_batches_qty", "quantity >= 0")
    _add_check(
        "serial_units",
        "chk_serial_units_status",
        "status IN ('IN_STOCK', 'SOLD')",
    )

    _create_index(
        "ix_serial_units_tenant_item_status",
        "serial_units",
        ["tenant_id", "item_id", "status"],
    )
    _create_index(
        "ix_item_variants_tenant_item_active",
        "item_variants",
        ["tenant_id", "item_id", "is_active"],
    )
    _create_index(
        "ix_item_batches_tenant_expiry_active",
        "item_batches",
        ["tenant_id", "expiry_date", "is_active"],
    )
    _create_index(
        "ix_party_ledger_tenant_party_created",
        "party_ledger_entries",
        ["tenant_id", "party_type", "party_id", "created_at"],
    )


def downgrade() -> None:
    for name, table in (
        ("ix_party_ledger_tenant_party_created", "party_ledger_entries"),
        ("ix_item_batches_tenant_expiry_active", "item_batches"),
        ("ix_item_variants_tenant_item_active", "item_variants"),
        ("ix_serial_units_tenant_item_status", "serial_units"),
    ):
        if _has_index(table, name):
            op.drop_index(name, table_name=table)

    for table, name in (
        ("serial_units", "chk_serial_units_status"),
        ("item_batches", "chk_item_batches_qty"),
        ("item_variants", "chk_item_variants_stock"),
    ):
        if not _has_check(name):
            continue
        for stmt in (
            f"ALTER TABLE `{table}` DROP CONSTRAINT `{name}`",
            f"ALTER TABLE `{table}` DROP CHECK `{name}`",
        ):
            try:
                op.execute(text(stmt))
                break
            except Exception:
                continue
