"""Sprint 4 relationship alignment.

- Align bills.status default with app/ORM (FINALIZED)
- Preserve bill history if a catalog item row is removed (bill_items.item_id SET NULL)

Revision ID: 20260814_schema_rel_fixes
Revises: 20260814_tenant_business_type
Create Date: 2026-08-14
"""

from alembic import op
import sqlalchemy as sa


revision = "20260814_schema_rel_fixes"
down_revision = "20260814_tenant_business_type"
branch_labels = None
depends_on = None


def upgrade():
    # MySQL: change default status to FINALIZED (app never creates DRAFT today).
    op.execute(
        "ALTER TABLE bills MODIFY status VARCHAR(20) NOT NULL DEFAULT 'FINALIZED'"
    )

    # Recreate item FK as SET NULL so historical bill lines survive catalog hard-deletes.
    # Soft-deactivate remains the application rule; this protects history if ops deletes a row.
    with op.batch_alter_table("bill_items") as batch:
        batch.drop_constraint("fk_bill_items_item", type_="foreignkey")
        batch.create_foreign_key(
            "fk_bill_items_item",
            "items",
            ["item_id"],
            ["id"],
            ondelete="SET NULL",
            onupdate="CASCADE",
        )


def downgrade():
    with op.batch_alter_table("bill_items") as batch:
        batch.drop_constraint("fk_bill_items_item", type_="foreignkey")
        batch.create_foreign_key(
            "fk_bill_items_item",
            "items",
            ["item_id"],
            ["id"],
            ondelete="RESTRICT",
            onupdate="CASCADE",
        )

    op.execute(
        "ALTER TABLE bills MODIFY status VARCHAR(20) NOT NULL DEFAULT 'DRAFT'"
    )
