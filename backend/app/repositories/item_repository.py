"""Item data access — tenant scoped."""

from sqlalchemy import or_, func
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.item import Item


class ItemRepository:
    @staticmethod
    def get_by_id_and_tenant(item_id: str, tenant_id: str) -> Item | None:
        return (
            db.session.query(Item)
            .options(joinedload(Item.category), joinedload(Item.creator))
            .filter(Item.id == item_id, Item.tenant_id == tenant_id)
            .first()
        )

    @staticmethod
    def lock_by_id_and_tenant(item_id: str, tenant_id: str) -> Item | None:
        """Row-lock item for concurrent stock updates (MySQL FOR UPDATE; SQLite no-op)."""
        return (
            db.session.query(Item)
            .filter(Item.id == item_id, Item.tenant_id == tenant_id)
            .with_for_update()
            .first()
        )

    @staticmethod
    def find_by_tenant_and_name(tenant_id: str, name: str) -> Item | None:
        return (
            db.session.query(Item)
            .filter(
                Item.tenant_id == tenant_id,
                func.lower(Item.name) == name.lower().strip(),
            )
            .first()
        )

    @staticmethod
    def find_by_tenant_and_sku(tenant_id: str, sku: str) -> Item | None:
        cleaned = (sku or "").strip()
        if not cleaned:
            return None
        return (
            db.session.query(Item)
            .filter(
                Item.tenant_id == tenant_id,
                func.lower(Item.sku) == cleaned.lower(),
            )
            .first()
        )

    @staticmethod
    def find_by_tenant_and_barcode(tenant_id: str, barcode: str) -> Item | None:
        cleaned = (barcode or "").strip()
        if not cleaned:
            return None
        return (
            db.session.query(Item)
            .options(joinedload(Item.category), joinedload(Item.creator))
            .filter(
                Item.tenant_id == tenant_id,
                func.lower(Item.barcode) == cleaned.lower(),
            )
            .first()
        )

    @staticmethod
    def find_by_tenant_and_isbn(tenant_id: str, isbn: str) -> Item | None:
        cleaned = (isbn or "").strip().replace("-", "").replace(" ", "")
        if not cleaned:
            return None
        return (
            db.session.query(Item)
            .options(joinedload(Item.category), joinedload(Item.creator))
            .filter(
                Item.tenant_id == tenant_id,
                func.lower(Item.isbn) == cleaned.lower(),
            )
            .first()
        )

    @staticmethod
    def list_by_tenant(
        tenant_id: str,
        *,
        q: str | None = None,
        barcode: str | None = None,
        isbn: str | None = None,
        category_id: str | None = None,
        is_active: bool | None = None,
        stock_status: str | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[Item], int]:
        query = db.session.query(Item).filter(Item.tenant_id == tenant_id)
        if barcode:
            cleaned = barcode.strip()
            query = query.filter(func.lower(Item.barcode) == cleaned.lower())
        elif isbn:
            cleaned = isbn.strip().replace("-", "").replace(" ", "")
            query = query.filter(func.lower(Item.isbn) == cleaned.lower())
        elif q:
            raw_q = q.strip()
            like = f"%{raw_q}%"
            isbn_compact = raw_q.replace("-", "").replace(" ", "")
            clauses = [
                Item.name.ilike(like),
                Item.sku.ilike(like),
                Item.barcode.ilike(like),
                Item.isbn.ilike(like),
                Item.author.ilike(like),
                Item.publisher.ilike(like),
                Item.material.ilike(like),
                Item.color.ilike(like),
            ]
            if isbn_compact and isbn_compact != raw_q:
                clauses.append(Item.isbn.ilike(f"%{isbn_compact}%"))
            query = query.filter(or_(*clauses))
        if category_id:
            query = query.filter(Item.category_id == category_id)
        if is_active is not None:
            query = query.filter(Item.is_active.is_(is_active))
        if stock_status == "tracked":
            query = query.filter(Item.stock_quantity.is_not(None))
        elif stock_status == "out":
            query = query.filter(
                Item.stock_quantity.is_not(None),
                Item.stock_quantity <= 0,
            )
        elif stock_status == "low":
            query = query.filter(
                Item.stock_quantity.is_not(None),
                Item.minimum_stock_level.is_not(None),
                Item.stock_quantity > 0,
                Item.stock_quantity <= Item.minimum_stock_level,
            )

        total = query.count()
        page = max(page, 1)
        per_page = min(max(per_page, 1), 100)
        items = (
            query.options(joinedload(Item.category), joinedload(Item.creator))
            .order_by(Item.name.asc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return items, total

    @staticmethod
    def list_menu_items_by_tenant(tenant_id: str, *, is_veg: bool | None = None) -> list[Item]:
        query = (
            db.session.query(Item)
            .options(joinedload(Item.category), joinedload(Item.creator))
            .filter(
                Item.tenant_id == tenant_id,
                Item.is_menu.is_(True),
                Item.is_active.is_(True),
            )
        )
        if is_veg is not None:
            query = query.filter(Item.is_veg.is_(is_veg))
        from app.constants.perf import MENU_CATALOG_MAX

        return query.order_by(Item.name.asc()).limit(MENU_CATALOG_MAX).all()

    @staticmethod
    def inventory_health_counts(tenant_id: str) -> dict:
        """Point-in-time stock health for a tenant (active + inactive catalog)."""
        base = db.session.query(Item).filter(Item.tenant_id == tenant_id)
        total = base.count()
        tracked = base.filter(Item.stock_quantity.is_not(None)).count()
        untracked = total - tracked
        out = base.filter(
            Item.stock_quantity.is_not(None),
            Item.stock_quantity <= 0,
        ).count()
        low = base.filter(
            Item.stock_quantity.is_not(None),
            Item.minimum_stock_level.is_not(None),
            Item.stock_quantity > 0,
            Item.stock_quantity <= Item.minimum_stock_level,
        ).count()
        return {
            "total_items": total,
            "tracked": tracked,
            "untracked": untracked,
            "low": low,
            "out": out,
        }

    @staticmethod
    def add(item: Item) -> Item:
        db.session.add(item)
        return item
