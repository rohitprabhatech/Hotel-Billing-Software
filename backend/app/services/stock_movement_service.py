"""Record and list stock movements."""

from datetime import timedelta
from decimal import Decimal

from flask import current_app

from app.constants.permissions import PERM_STOCK_MOVEMENTS
from app.models.stock_movement import StockMovement
from app.repositories.stock_movement_repository import StockMovementRepository
from app.utils.exceptions import ValidationError
from app.utils.permission_access import require_permission
from app.utils.ids import new_uuid
from app.utils.periods import parse_date, to_utc_naive
from app.utils.request_context import require_request_context

_ALLOWED_SOURCES = {
    "BILL",
    "CANCEL",
    "ADJUST",
    "ITEM_UPDATE",
    "RECEIVE",
    "PURCHASE",
    "PURCHASE_CANCEL",
    "RECIPE",
    "WASTAGE",
    "RETURN",
    "EXCHANGE",
}


class StockMovementService:
    @staticmethod
    def _tz():
        return current_app.config.get("REPORT_TIMEZONE", "Asia/Kolkata")

    @staticmethod
    def record(
        *,
        tenant_id: str,
        item_id: str,
        delta: Decimal,
        quantity_after: Decimal,
        source: str,
        reason: str | None = None,
        reference_type: str | None = None,
        reference_id: str | None = None,
        created_by: str | None = None,
    ) -> StockMovement:
        row = StockMovement(
            id=new_uuid(),
            tenant_id=tenant_id,
            item_id=item_id,
            delta=delta,
            quantity_after=quantity_after,
            source=source,
            reason=(reason or None),
            reference_type=reference_type,
            reference_id=reference_id,
            created_by=created_by,
        )
        StockMovementRepository.add(row)
        return row

    @staticmethod
    def list_movements(
        *,
        item_id=None,
        source=None,
        from_date=None,
        to_date=None,
        page=1,
        per_page=50,
    ):
        ctx = require_request_context()
        require_permission(PERM_STOCK_MOVEMENTS)
        source_filter = None
        if source:
            source_filter = str(source).strip().upper()
            if source_filter not in _ALLOWED_SOURCES:
                raise ValidationError("Invalid stock movement source filter")

        date_from = None
        date_to = None
        tz = StockMovementService._tz()
        if from_date:
            date_from = to_utc_naive(parse_date(from_date, tz))
        if to_date:
            end_local = parse_date(to_date, tz) + timedelta(days=1)
            date_to = to_utc_naive(end_local)

        rows, total = StockMovementRepository.list_by_tenant(
            ctx.tenant_id,
            item_id=item_id or None,
            source=source_filter,
            date_from=date_from,
            date_to=date_to,
            page=page,
            per_page=per_page,
        )
        return (
            [StockMovementService.serialize(r) for r in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def serialize(row: StockMovement):
        return {
            "id": row.id,
            "item_id": row.item_id,
            "item_name": row.item.name if row.item else None,
            "delta": float(row.delta),
            "quantity_after": float(row.quantity_after),
            "source": row.source,
            "reason": row.reason,
            "reference_type": row.reference_type,
            "reference_id": row.reference_id,
            "created_by": row.created_by,
            "created_by_name": row.creator.name if row.creator else None,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
