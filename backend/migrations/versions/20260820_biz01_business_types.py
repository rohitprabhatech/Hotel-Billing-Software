"""Map legacy business_type codes to the 14-type BIZ-01 catalog.

Revision ID: 20260820_biz01_business_types
Revises: 20260818_phase8_saas

Data-only migration. No DROP.
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import inspect, text

revision = "20260820_biz01_business_types"
down_revision = "20260818_phase8_saas"
branch_labels = None
depends_on = None

LEGACY_MAP = {
    "restaurant": "hotel_restaurant",
    "hotel": "hotel_restaurant",
    "clothing_store": "clothing",
    "footwear_store": "clothing",
    "kirana_store": "grocery_kirana",
    "grocery_store": "grocery_kirana",
    "electronics_store": "electronics",
    "retail_shop": "stationery",
    "other": "grocery_kirana",
    "bakery_sweets": "bakery_sweet",
    "bookstore": "book_store",
}

REVERSE_MAP = {
    "hotel_restaurant": "hotel",
    "clothing": "clothing_store",
    "grocery_kirana": "grocery_store",
    "electronics": "electronics_store",
    "stationery": "retail_shop",
    "bakery_sweet": "bakery_sweets",
    "book_store": "bookstore",
}


def _has_business_type(table: str) -> bool:
    bind = op.get_bind()
    inspector = inspect(bind)
    if table not in inspector.get_table_names():
        return False
    return any(c["name"] == "business_type" for c in inspector.get_columns(table))


def _remap(table: str, mapping: dict[str, str]) -> None:
    if not _has_business_type(table):
        return
    for source, target in mapping.items():
        op.execute(
            text(
                f"UPDATE {table} SET business_type = :target "
                "WHERE LOWER(TRIM(business_type)) = :source"
            ).bindparams(target=target, source=source)
        )


def upgrade() -> None:
    for table in ("tenants", "registration_requests"):
        _remap(table, LEGACY_MAP)


def downgrade() -> None:
    for table in ("tenants", "registration_requests"):
        _remap(table, REVERSE_MAP)
