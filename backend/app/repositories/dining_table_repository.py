"""Dining table data access — tenant scoped."""

from sqlalchemy import case, func

from app.extensions import db
from app.models.dining_table import DiningTable


class DiningTableRepository:
    @staticmethod
    def get_by_id_and_tenant(table_id: str, tenant_id: str) -> DiningTable | None:
        return (
            db.session.query(DiningTable)
            .filter(DiningTable.id == table_id, DiningTable.tenant_id == tenant_id)
            .first()
        )

    @staticmethod
    def find_by_code(tenant_id: str, code: str) -> DiningTable | None:
        cleaned = (code or "").strip()
        if not cleaned:
            return None
        return (
            db.session.query(DiningTable)
            .filter(
                DiningTable.tenant_id == tenant_id,
                func.lower(DiningTable.code) == cleaned.lower(),
            )
            .first()
        )

    @staticmethod
    def list_by_tenant(
        tenant_id: str,
        *,
        section: str | None = None,
        status: str | None = None,
        is_active: bool | None = True,
        include_merged_children: bool = True,
    ) -> list[DiningTable]:
        query = db.session.query(DiningTable).filter(DiningTable.tenant_id == tenant_id)
        if is_active is not None:
            query = query.filter(DiningTable.is_active.is_(is_active))
        if section:
            query = query.filter(func.lower(DiningTable.section) == section.strip().lower())
        if status:
            query = query.filter(DiningTable.status == status)
        if not include_merged_children:
            query = query.filter(DiningTable.merged_into_id.is_(None))
        # MySQL does not support NULLS FIRST/LAST — use CASE instead.
        return query.order_by(
            case((DiningTable.section.is_(None), 0), else_=1),
            DiningTable.section.asc(),
            DiningTable.code.asc(),
        ).all()

    @staticmethod
    def list_merged_children(tenant_id: str, primary_table_id: str) -> list[DiningTable]:
        return (
            db.session.query(DiningTable)
            .filter(
                DiningTable.tenant_id == tenant_id,
                DiningTable.merged_into_id == primary_table_id,
                DiningTable.is_active.is_(True),
            )
            .order_by(DiningTable.code.asc())
            .all()
        )

    @staticmethod
    def add(table: DiningTable) -> DiningTable:
        db.session.add(table)
        return table
