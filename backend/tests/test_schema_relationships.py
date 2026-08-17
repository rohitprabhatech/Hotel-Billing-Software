"""Schema relationship integrity smoke tests (ORM metadata)."""

from sqlalchemy import inspect

from app.models.bill import Bill, BillItem
from app.models.category import Category
from app.models.item import Item
from app.models.tenant import Tenant
from app.models.user import User


def _foreign_keys(model):
    result = {}
    for column in inspect(model).columns:
        for fk in column.foreign_keys:
            result[column.name] = {
                "target": f"{fk.column.table.name}.{fk.column.name}",
                "ondelete": (fk.ondelete or "").upper() or None,
            }
    return result


def test_core_tenant_fks_are_restrict():
    assert _foreign_keys(User)["tenant_id"]["ondelete"] == "RESTRICT"
    assert _foreign_keys(Category)["tenant_id"]["ondelete"] == "RESTRICT"
    assert _foreign_keys(Item)["tenant_id"]["ondelete"] == "RESTRICT"
    assert _foreign_keys(Bill)["tenant_id"]["ondelete"] == "RESTRICT"
    assert _foreign_keys(BillItem)["tenant_id"]["ondelete"] == "RESTRICT"


def test_bill_item_catalog_fk_set_null_for_history():
    fk = _foreign_keys(BillItem)["item_id"]
    assert fk["target"] == "items.id"
    assert fk["ondelete"] == "SET NULL"


def test_item_created_by_set_null():
    assert _foreign_keys(Item)["created_by"]["ondelete"] == "SET NULL"


def test_category_parent_self_fk_restrict():
    assert _foreign_keys(Category)["parent_id"]["ondelete"] == "RESTRICT"


def test_bill_default_status_finalized():
    assert Bill.__table__.c.status.default.arg == "FINALIZED"


def test_tenant_has_business_type_column():
    assert "business_type" in Tenant.__table__.c
    assert Tenant.__table__.c.business_type.nullable is False
