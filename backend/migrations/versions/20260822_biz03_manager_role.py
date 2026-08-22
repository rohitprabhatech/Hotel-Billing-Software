"""Seed MANAGER role (BIZ-03).

Revision ID: 20260822_biz03_manager_role
Revises: 20260820_biz01_business_types
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import inspect, text

revision = "20260822_biz03_manager_role"
down_revision = "20260820_biz01_business_types"
branch_labels = None
depends_on = None

MANAGER_ID = "33333333-3333-3333-3333-333333333333"


def _manager_role_exists(bind) -> bool:
    row = bind.execute(text("SELECT 1 FROM roles WHERE name = 'MANAGER' LIMIT 1")).fetchone()
    return row is not None


def _roles_check_allows_manager(bind) -> bool:
    row = bind.execute(
        text(
            "SELECT CHECK_CLAUSE FROM information_schema.CHECK_CONSTRAINTS "
            "WHERE CONSTRAINT_SCHEMA = DATABASE() "
            "AND TABLE_NAME = 'roles' AND CONSTRAINT_NAME = 'chk_roles_name'"
        )
    ).fetchone()
    return row is not None and "MANAGER" in str(row[0]).upper()


def _expand_roles_name_check(bind) -> None:
    """02_schema.sql only allowed OWNER/BILLING_USER — widen before seeding MANAGER."""
    if bind.dialect.name != "mysql":
        return
    if _manager_role_exists(bind) or _roles_check_allows_manager(bind):
        return
    # MariaDB uses DROP CONSTRAINT; MySQL 8.0.19+ accepts DROP CHECK — try both.
    dropped = False
    for drop_sql in (
        "ALTER TABLE roles DROP CONSTRAINT chk_roles_name",
        "ALTER TABLE roles DROP CHECK chk_roles_name",
    ):
        try:
            bind.execute(text(drop_sql))
            dropped = True
            break
        except Exception:
            continue
    if not dropped and not _roles_check_allows_manager(bind):
        raise RuntimeError(
            "Could not drop chk_roles_name before seeding MANAGER role"
        )
    bind.execute(
        text(
            "ALTER TABLE roles ADD CONSTRAINT chk_roles_name "
            "CHECK (name IN ('OWNER', 'BILLING_USER', 'MANAGER'))"
        )
    )


def _has_roles_table() -> bool:
    return "roles" in inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if not _has_roles_table():
        return
    bind = op.get_bind()
    _expand_roles_name_check(bind)
    op.execute(
        text(
            "INSERT INTO roles (id, name, description, created_at, updated_at) "
            "SELECT :id, :name, :description, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP "
            "FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = :name)"
        ).bindparams(
            id=MANAGER_ID,
            name="MANAGER",
            description="Operations manager - billing, reports, stock (no admin settings)",
        )
    )


def downgrade() -> None:
    if not _has_roles_table():
        return
    op.execute(text("DELETE FROM roles WHERE name = 'MANAGER'"))
