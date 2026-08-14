"""Add catalog fields sku, cost_price, stock_quantity on items.

Revision ID: 20260814_item_catalog_fields
Revises: 20260814_schema_rel_fixes
Create Date: 2026-08-14
"""

from alembic import op
import sqlalchemy as sa


revision = "20260814_item_catalog_fields"
down_revision = "20260814_schema_rel_fixes"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("items") as batch:
        batch.add_column(sa.Column("sku", sa.String(length=64), nullable=True))
        batch.add_column(sa.Column("cost_price", sa.Numeric(12, 2), nullable=True))
        batch.add_column(sa.Column("stock_quantity", sa.Numeric(12, 3), nullable=True))
        batch.create_index("ix_items_tenant_sku", ["tenant_id", "sku"])
        batch.create_unique_constraint("uq_items_tenant_sku", ["tenant_id", "sku"])


def downgrade():
    with op.batch_alter_table("items") as batch:
        batch.drop_constraint("uq_items_tenant_sku", type_="unique")
        batch.drop_index("ix_items_tenant_sku")
        batch.drop_column("stock_quantity")
        batch.drop_column("cost_price")
        batch.drop_column("sku")
