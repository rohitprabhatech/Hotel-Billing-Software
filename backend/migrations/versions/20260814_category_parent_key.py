"""Category parent_key uniqueness for MySQL NULL-parent quirk.

Revision ID: 20260814_category_parent_key
Revises: 20260814_item_catalog_fields
Create Date: 2026-08-14
"""

from alembic import op
import sqlalchemy as sa


revision = "20260814_category_parent_key"
down_revision = "20260814_item_catalog_fields"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "mysql":
        op.execute(
            sa.text(
                """
                ALTER TABLE categories
                ADD COLUMN parent_key CHAR(36)
                AS (IFNULL(parent_id, '')) VIRTUAL
                AFTER parent_id
                """
            )
        )
        try:
            op.drop_constraint("uq_categories_tenant_parent_name", "categories", type_="unique")
        except Exception:  # noqa: BLE001 — index may already be absent on drifted DBs
            pass
        op.create_unique_constraint(
            "uq_categories_tenant_parent_key_name",
            "categories",
            ["tenant_id", "parent_key", "name"],
        )
        return

    with op.batch_alter_table("categories") as batch:
        batch.add_column(
            sa.Column(
                "parent_key",
                sa.String(36),
                sa.Computed("IFNULL(parent_id, '')", persisted=False),
            )
        )
        try:
            batch.drop_constraint("uq_categories_tenant_parent_name", type_="unique")
        except Exception:  # noqa: BLE001
            pass
        batch.create_unique_constraint(
            "uq_categories_tenant_parent_key_name",
            ["tenant_id", "parent_key", "name"],
        )


def downgrade():
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "mysql":
        try:
            op.drop_constraint(
                "uq_categories_tenant_parent_key_name", "categories", type_="unique"
            )
        except Exception:  # noqa: BLE001
            pass
        op.execute(sa.text("ALTER TABLE categories DROP COLUMN parent_key"))
        op.create_unique_constraint(
            "uq_categories_tenant_parent_name",
            "categories",
            ["tenant_id", "parent_id", "name"],
        )
        return

    with op.batch_alter_table("categories") as batch:
        try:
            batch.drop_constraint("uq_categories_tenant_parent_key_name", type_="unique")
        except Exception:  # noqa: BLE001
            pass
        batch.drop_column("parent_key")
        batch.create_unique_constraint(
            "uq_categories_tenant_parent_name",
            ["tenant_id", "parent_id", "name"],
        )
