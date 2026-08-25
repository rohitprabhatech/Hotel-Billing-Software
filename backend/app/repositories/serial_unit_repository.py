"""Serial unit persistence (BIZ-29)."""

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.serial_unit import STATUS_IN_STOCK, SerialUnit


class SerialUnitRepository:
    @staticmethod
    def add(row: SerialUnit) -> SerialUnit:
        db.session.add(row)
        return row

    @staticmethod
    def get_by_id(tenant_id: str, unit_id: str) -> SerialUnit | None:
        return SerialUnit.query.filter_by(tenant_id=tenant_id, id=unit_id).first()

    @staticmethod
    def lock_by_id(tenant_id: str, unit_id: str) -> SerialUnit | None:
        return (
            db.session.query(SerialUnit)
            .filter(SerialUnit.tenant_id == tenant_id, SerialUnit.id == unit_id)
            .with_for_update()
            .first()
        )

    @staticmethod
    def find_by_serial(tenant_id: str, serial: str) -> SerialUnit | None:
        cleaned = (serial or "").strip().upper()
        if not cleaned:
            return None
        return SerialUnit.query.filter_by(tenant_id=tenant_id, serial=cleaned).first()

    @staticmethod
    def lock_by_serial(tenant_id: str, serial: str) -> SerialUnit | None:
        cleaned = (serial or "").strip().upper()
        if not cleaned:
            return None
        return (
            db.session.query(SerialUnit)
            .filter(SerialUnit.tenant_id == tenant_id, SerialUnit.serial == cleaned)
            .with_for_update()
            .first()
        )

    @staticmethod
    def count_in_stock(tenant_id: str, item_id: str) -> int:
        return int(
            db.session.query(func.count(SerialUnit.id))
            .filter(
                SerialUnit.tenant_id == tenant_id,
                SerialUnit.item_id == item_id,
                SerialUnit.status == STATUS_IN_STOCK,
            )
            .scalar()
            or 0
        )

    @staticmethod
    def list_for_tenant(
        tenant_id: str,
        *,
        item_id: str | None = None,
        status: str | None = None,
        q: str | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[SerialUnit], int]:
        query = SerialUnit.query.options(joinedload(SerialUnit.item)).filter_by(tenant_id=tenant_id)
        if item_id:
            query = query.filter_by(item_id=item_id)
        if status:
            query = query.filter_by(status=status.strip().upper())
        if q:
            like = f"%{q.strip()}%"
            query = query.filter(SerialUnit.serial.ilike(like))
        total = query.with_entities(func.count(SerialUnit.id)).scalar() or 0
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 50), 1), 100)
        rows = (
            query.order_by(SerialUnit.received_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, int(total)
