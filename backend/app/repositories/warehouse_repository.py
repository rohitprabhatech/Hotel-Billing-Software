"""Warehouse and stock-transfer persistence (BIZ-38)."""

from decimal import Decimal

from sqlalchemy import func

from app.extensions import db
from app.models.warehouse import (
    StockTransfer,
    StockTransferNumberCounter,
    Warehouse,
    WarehouseStock,
)


class WarehouseRepository:
    @staticmethod
    def get_by_id(tenant_id: str, warehouse_id: str) -> Warehouse | None:
        return Warehouse.query.filter_by(tenant_id=tenant_id, id=warehouse_id).first()

    @staticmethod
    def get_default(tenant_id: str) -> Warehouse | None:
        return Warehouse.query.filter_by(
            tenant_id=tenant_id, is_default=True, is_active=True
        ).first()

    @staticmethod
    def get_by_code(tenant_id: str, code: str) -> Warehouse | None:
        return Warehouse.query.filter_by(tenant_id=tenant_id, code=code.strip().upper()).first()

    @staticmethod
    def list_for_tenant(
        tenant_id: str, *, active_only: bool = True
    ) -> list[Warehouse]:
        query = Warehouse.query.filter_by(tenant_id=tenant_id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(Warehouse.is_default.desc(), Warehouse.name.asc()).all()

    @staticmethod
    def add(row: Warehouse) -> Warehouse:
        db.session.add(row)
        return row

    @staticmethod
    def clear_default(tenant_id: str) -> None:
        Warehouse.query.filter_by(tenant_id=tenant_id, is_default=True).update(
            {"is_default": False}
        )

    @staticmethod
    def lock_stock(tenant_id: str, warehouse_id: str, item_id: str) -> WarehouseStock | None:
        return (
            db.session.query(WarehouseStock)
            .filter(
                WarehouseStock.tenant_id == tenant_id,
                WarehouseStock.warehouse_id == warehouse_id,
                WarehouseStock.item_id == item_id,
            )
            .with_for_update()
            .first()
        )

    @staticmethod
    def get_stock(tenant_id: str, warehouse_id: str, item_id: str) -> WarehouseStock | None:
        return WarehouseStock.query.filter_by(
            tenant_id=tenant_id, warehouse_id=warehouse_id, item_id=item_id
        ).first()

    @staticmethod
    def list_stocks(
        tenant_id: str,
        *,
        warehouse_id: str | None = None,
        item_id: str | None = None,
        page: int = 1,
        per_page: int = 100,
    ) -> tuple[list[WarehouseStock], int]:
        query = WarehouseStock.query.filter_by(tenant_id=tenant_id)
        if warehouse_id:
            query = query.filter_by(warehouse_id=warehouse_id)
        if item_id:
            query = query.filter_by(item_id=item_id)
        total = query.with_entities(func.count(WarehouseStock.id)).scalar() or 0
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 100), 1), 200)
        rows = (
            query.order_by(WarehouseStock.updated_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, int(total)

    @staticmethod
    def sum_item_quantity(tenant_id: str, item_id: str) -> Decimal:
        value = (
            db.session.query(func.coalesce(func.sum(WarehouseStock.quantity), 0))
            .filter(
                WarehouseStock.tenant_id == tenant_id,
                WarehouseStock.item_id == item_id,
            )
            .scalar()
        )
        return Decimal(str(value or 0))

    @staticmethod
    def add_stock(row: WarehouseStock) -> WarehouseStock:
        db.session.add(row)
        return row


class StockTransferRepository:
    @staticmethod
    def get_by_id(tenant_id: str, transfer_id: str) -> StockTransfer | None:
        return StockTransfer.query.filter_by(tenant_id=tenant_id, id=transfer_id).first()

    @staticmethod
    def list_for_tenant(
        tenant_id: str, *, page: int = 1, per_page: int = 50
    ) -> tuple[list[StockTransfer], int]:
        query = StockTransfer.query.filter_by(tenant_id=tenant_id)
        total = query.with_entities(func.count(StockTransfer.id)).scalar() or 0
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 50), 1), 100)
        rows = (
            query.order_by(StockTransfer.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, int(total)

    @staticmethod
    def allocate_number(tenant_id: str) -> tuple[int, str]:
        counter = (
            db.session.query(StockTransferNumberCounter)
            .filter(StockTransferNumberCounter.tenant_id == tenant_id)
            .with_for_update()
            .first()
        )
        if counter is None:
            counter = StockTransferNumberCounter(tenant_id=tenant_id, next_value=1)
            db.session.add(counter)
            db.session.flush()
        sequence = int(counter.next_value)
        counter.next_value = sequence + 1
        db.session.flush()
        return sequence, f"ST-{sequence:05d}"

    @staticmethod
    def add(row: StockTransfer) -> StockTransfer:
        db.session.add(row)
        return row
