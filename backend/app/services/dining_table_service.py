"""Dining table business logic (BIZ-12)."""

from app.constants.permissions import PERM_TABLES_READ, PERM_TABLES_STATUS, PERM_TABLES_WRITE
from app.constants.tables import (
    TABLE_STATUS_AVAILABLE,
    TABLE_STATUS_OCCUPIED,
    assert_valid_table_status,
    can_transition_table_status,
)
from app.extensions import db
from app.models.dining_table import DiningTable
from app.repositories.dining_table_repository import DiningTableRepository
from app.repositories.order_repository import OrderRepository
from app.services.audit_service import AuditService
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context


class DiningTableService:
    @staticmethod
    def list_tables(*, section=None, status=None, include_merged_children=False):
        require_permission(PERM_TABLES_READ)
        ctx = require_request_context()
        rows = DiningTableRepository.list_by_tenant(
            ctx.tenant_id,
            section=section,
            status=status,
            is_active=True,
            include_merged_children=include_merged_children,
        )
        primaries = [row for row in rows if row.merged_into_id is None]
        open_orders = OrderRepository.map_open_orders_by_table_ids(
            ctx.tenant_id, [row.id for row in primaries]
        )
        item_counts = OrderRepository.count_items_by_order_ids(
            ctx.tenant_id, [order.id for order in open_orders.values()]
        )
        return [
            DiningTableService.serialize(
                row,
                open_order=open_orders.get(row.id),
                open_order_item_count=item_counts.get(open_orders[row.id].id, 0)
                if row.id in open_orders
                else 0,
            )
            for row in primaries
        ]

    @staticmethod
    def get_table(table_id: str):
        require_permission(PERM_TABLES_READ)
        ctx = require_request_context()
        table = DiningTableRepository.get_by_id_and_tenant(table_id, ctx.tenant_id)
        if table is None or not table.is_active:
            raise NotFoundError("Table not found")
        open_order = OrderRepository.get_open_by_table(ctx.tenant_id, table.id)
        item_count = 0
        if open_order is not None:
            item_count = OrderRepository.count_items_by_order_ids(
                ctx.tenant_id, [open_order.id]
            ).get(open_order.id, 0)
        return DiningTableService.serialize(
            table, open_order=open_order, open_order_item_count=item_count
        )

    @staticmethod
    def list_table_bills(table_id: str, *, page: int = 1, per_page: int = 20):
        """Completed bills whose reference/table_number matches this table code."""
        require_permission(PERM_TABLES_READ)
        ctx = require_request_context()
        table = DiningTableRepository.get_by_id_and_tenant(table_id, ctx.tenant_id)
        if table is None or not table.is_active:
            raise NotFoundError("Table not found")
        from app.services.bill_service import BillService

        return BillService.list_bills_for_reference(
            reference=table.code, page=page, per_page=per_page
        )

    @staticmethod
    def create_table(*, code, section=None, capacity=None):
        require_permission(PERM_TABLES_WRITE)
        ctx = require_request_context()
        code_value = DiningTableService._normalize_code(code)
        if DiningTableRepository.find_by_code(ctx.tenant_id, code_value):
            raise ConflictError("A table with this code already exists")

        table = DiningTable(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            code=code_value,
            section=DiningTableService._normalize_section(section),
            capacity=DiningTableService._normalize_capacity(capacity),
            status=TABLE_STATUS_AVAILABLE,
            is_active=True,
        )
        DiningTableRepository.add(table)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_DINING_TABLE",
            entity_type="DINING_TABLE",
            entity_id=table.id,
            new_data=DiningTableService.serialize(table),
        )
        db.session.commit()
        return DiningTableService.serialize(table)

    @staticmethod
    def update_table(table_id: str, *, code=None, section=None, capacity=None, code_provided=False, section_provided=False, capacity_provided=False):
        require_permission(PERM_TABLES_WRITE)
        ctx = require_request_context()
        table = DiningTableRepository.get_by_id_and_tenant(table_id, ctx.tenant_id)
        if table is None or not table.is_active:
            raise NotFoundError("Table not found")
        if table.merged_into_id:
            raise ValidationError("Cannot edit a table that is merged into another. Unmerge first.")

        old = DiningTableService.serialize(table)
        if code_provided:
            code_value = DiningTableService._normalize_code(code)
            existing = DiningTableRepository.find_by_code(ctx.tenant_id, code_value)
            if existing and existing.id != table.id:
                raise ConflictError("A table with this code already exists")
            table.code = code_value
        if section_provided:
            table.section = DiningTableService._normalize_section(section)
        if capacity_provided:
            table.capacity = DiningTableService._normalize_capacity(capacity)

        new_data = DiningTableService.serialize(table)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_DINING_TABLE",
            entity_type="DINING_TABLE",
            entity_id=table.id,
            old_data=old,
            new_data=new_data,
        )
        db.session.commit()
        return new_data

    @staticmethod
    def deactivate_table(table_id: str):
        require_permission(PERM_TABLES_WRITE)
        ctx = require_request_context()
        table = DiningTableRepository.get_by_id_and_tenant(table_id, ctx.tenant_id)
        if table is None or not table.is_active:
            raise NotFoundError("Table not found")
        if table.merged_into_id:
            raise ValidationError("Cannot deactivate a merged secondary table. Unmerge first.")
        children = DiningTableRepository.list_merged_children(ctx.tenant_id, table.id)
        if children:
            raise ValidationError("Unmerge tables before deactivating the primary table.")

        old = DiningTableService.serialize(table)
        table.is_active = False
        table.status = TABLE_STATUS_AVAILABLE
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="DEACTIVATE_DINING_TABLE",
            entity_type="DINING_TABLE",
            entity_id=table.id,
            old_data=old,
            new_data={"code": table.code, "is_active": False},
        )
        db.session.commit()
        return DiningTableService.serialize(table)

    @staticmethod
    def set_status(table_id: str, status: str):
        require_permission(PERM_TABLES_STATUS)
        ctx = require_request_context()
        table = DiningTableRepository.get_by_id_and_tenant(table_id, ctx.tenant_id)
        if table is None or not table.is_active:
            raise NotFoundError("Table not found")

        if table.merged_into_id:
            raise ValidationError("Update status on the primary merged table instead.")

        new_status = assert_valid_table_status(status)
        try:
            assert_valid_table_status(table.status)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        if not can_transition_table_status(table.status, new_status):
            raise ValidationError(
                f"Cannot change table status from {table.status} to {new_status}"
            )

        old = DiningTableService.serialize(table)
        table.status = new_status
        children = DiningTableRepository.list_merged_children(ctx.tenant_id, table.id)
        for child in children:
            child.status = new_status

        new_data = DiningTableService.serialize(table)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="DINING_TABLE_STATUS_CHANGED",
            entity_type="DINING_TABLE",
            entity_id=table.id,
            old_data={"code": old["code"], "status": old["status"]},
            new_data={"code": new_data["code"], "status": new_data["status"]},
        )
        db.session.commit()
        return new_data

    @staticmethod
    def merge_tables(*, primary_table_id: str, secondary_table_ids: list[str]):
        require_permission(PERM_TABLES_STATUS)
        ctx = require_request_context()
        primary = DiningTableRepository.get_by_id_and_tenant(primary_table_id, ctx.tenant_id)
        if primary is None or not primary.is_active:
            raise NotFoundError("Primary table not found")
        if primary.merged_into_id:
            raise ValidationError("Primary table cannot itself be merged into another table")

        unique_secondaries = []
        seen = set()
        for table_id in secondary_table_ids:
            if table_id == primary.id:
                raise ValidationError("Primary table cannot be listed as secondary")
            if table_id in seen:
                continue
            seen.add(table_id)
            unique_secondaries.append(table_id)

        secondaries: list[DiningTable] = []
        for table_id in unique_secondaries:
            row = DiningTableRepository.get_by_id_and_tenant(table_id, ctx.tenant_id)
            if row is None or not row.is_active:
                raise NotFoundError("One or more secondary tables were not found")
            if row.merged_into_id:
                raise ValidationError(f"Table {row.code} is already merged")
            if row.status != TABLE_STATUS_AVAILABLE:
                raise ValidationError(f"Table {row.code} must be available to merge")
            secondaries.append(row)

        target_status = TABLE_STATUS_OCCUPIED if primary.status == TABLE_STATUS_AVAILABLE else primary.status
        primary.status = target_status
        for row in secondaries:
            row.merged_into_id = primary.id
            row.status = target_status

        payload = {
            "primary_table_id": primary.id,
            "primary_code": primary.code,
            "secondary_table_ids": [row.id for row in secondaries],
            "secondary_codes": [row.code for row in secondaries],
            "status": target_status,
        }
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="MERGE_DINING_TABLES",
            entity_type="DINING_TABLE",
            entity_id=primary.id,
            new_data=payload,
        )
        db.session.commit()
        return DiningTableService.serialize(primary)

    @staticmethod
    def unmerge_tables(*, primary_table_id: str):
        require_permission(PERM_TABLES_STATUS)
        ctx = require_request_context()
        primary = DiningTableRepository.get_by_id_and_tenant(primary_table_id, ctx.tenant_id)
        if primary is None or not primary.is_active:
            raise NotFoundError("Primary table not found")
        children = DiningTableRepository.list_merged_children(ctx.tenant_id, primary.id)
        if not children:
            raise ValidationError("This table has no merged tables to release")

        released_codes = [child.code for child in children]
        for child in children:
            child.merged_into_id = None
            child.status = TABLE_STATUS_AVAILABLE
        primary.status = TABLE_STATUS_AVAILABLE

        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UNMERGE_DINING_TABLES",
            entity_type="DINING_TABLE",
            entity_id=primary.id,
            new_data={
                "primary_table_id": primary.id,
                "primary_code": primary.code,
                "released_codes": released_codes,
            },
        )
        db.session.commit()
        return DiningTableService.serialize(primary)

    @staticmethod
    def _normalize_code(value) -> str:
        cleaned = (value or "").strip()
        if not cleaned:
            raise ValidationError("Table code is required")
        if len(cleaned) > 32:
            raise ValidationError("Table code must be at most 32 characters")
        return cleaned

    @staticmethod
    def _normalize_section(value) -> str | None:
        if value is None:
            return None
        cleaned = str(value).strip()
        return cleaned or None

    @staticmethod
    def _normalize_capacity(value) -> int | None:
        if value is None or value == "":
            return None
        try:
            capacity = int(value)
        except (TypeError, ValueError) as exc:
            raise ValidationError("Capacity must be a whole number") from exc
        if capacity < 1 or capacity > 999:
            raise ValidationError("Capacity must be between 1 and 999")
        return capacity

    @staticmethod
    def serialize(table: DiningTable, *, open_order=None, open_order_item_count: int = 0):
        children = []
        if table.merged_into_id is None:
            children = DiningTableRepository.list_merged_children(table.tenant_id, table.id)
        payload = {
            "id": table.id,
            "code": table.code,
            "section": table.section,
            "capacity": table.capacity,
            "status": table.status,
            "merged_into_id": table.merged_into_id,
            "merged_tables": [
                {
                    "id": child.id,
                    "code": child.code,
                    "section": child.section,
                    "capacity": child.capacity,
                    "status": child.status,
                }
                for child in children
            ],
            "is_active": table.is_active,
            "created_at": table.created_at.isoformat() if table.created_at else None,
            "updated_at": table.updated_at.isoformat() if table.updated_at else None,
            "open_order_id": None,
            "open_order_number": None,
            "open_order_grand_total": None,
            "open_order_item_count": 0,
        }
        if open_order is not None:
            payload["open_order_id"] = open_order.id
            payload["open_order_number"] = open_order.order_number
            payload["open_order_grand_total"] = float(open_order.grand_total or 0)
            payload["open_order_item_count"] = int(open_order_item_count or 0)
        return payload
