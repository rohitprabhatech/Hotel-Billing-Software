"""Travel booking itinerary and document metadata (BIZ-58)."""

from datetime import date, datetime

from app.constants.permissions import PERM_BILLING
from app.extensions import db
from app.models.role import ROLE_BILLING_USER
from app.models.travel_booking_detail import (
    ALLOWED_DOCUMENT_TYPES,
    ALLOWED_ITINERARY_TYPES,
    TravelBookingDocument,
    TravelItineraryItem,
)
from app.repositories.tenant_repository import TenantRepository
from app.repositories.travel_booking_detail_repository import TravelBookingDetailRepository
from app.repositories.travel_booking_repository import TravelBookingRepository
from app.services.audit_service import AuditService
from app.services.module_service import ModuleService
from app.utils.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context

MODULE = "travel_bookings"


class TravelBookingDetailService:
    @staticmethod
    def _require(*, write: bool = False):
        require_permission(PERM_BILLING)
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, MODULE)
        if write and ctx.role == ROLE_BILLING_USER:
            raise ForbiddenError("Only the owner or manager can edit booking details")
        return ctx, tenant

    @staticmethod
    def _booking(tenant_id: str, booking_id: str):
        row = TravelBookingRepository.get_by_id(tenant_id, booking_id)
        if row is None:
            raise NotFoundError("Travel booking not found")
        return row

    @staticmethod
    def _parse_dt(value, *, field: str):
        if value is None or value == "":
            return None
        if isinstance(value, datetime):
            return value.replace(tzinfo=None) if value.tzinfo else value
        try:
            return datetime.fromisoformat(str(value).replace("Z", "")).replace(tzinfo=None)
        except ValueError as exc:
            raise ValidationError(f"{field} must be an ISO datetime") from exc

    @staticmethod
    def _parse_date(value, *, field: str):
        if value is None or value == "":
            return None
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        try:
            return date.fromisoformat(str(value)[:10])
        except ValueError as exc:
            raise ValidationError(f"{field} must be an ISO date (YYYY-MM-DD)") from exc

    @staticmethod
    def serialize_itinerary(row: TravelItineraryItem) -> dict:
        return {
            "id": row.id,
            "booking_id": row.booking_id,
            "item_type": row.item_type,
            "day_number": row.day_number,
            "title": row.title,
            "description": row.description,
            "location": row.location,
            "vendor_name": row.vendor_name,
            "confirmation_ref": row.confirmation_ref,
            "start_at": row.start_at.isoformat() if row.start_at else None,
            "end_at": row.end_at.isoformat() if row.end_at else None,
            "sort_order": int(row.sort_order or 0),
            "notes": row.notes,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }

    @staticmethod
    def serialize_document(row: TravelBookingDocument) -> dict:
        return {
            "id": row.id,
            "booking_id": row.booking_id,
            "document_type": row.document_type,
            "holder_name": row.holder_name,
            "document_number": row.document_number,
            "issued_country": row.issued_country,
            "expiry_date": row.expiry_date.isoformat() if row.expiry_date else None,
            "file_name": row.file_name,
            "notes": row.notes,
            "created_by": row.created_by,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }

    @staticmethod
    def list_itinerary(booking_id: str):
        ctx, _ = TravelBookingDetailService._require(write=False)
        TravelBookingDetailService._booking(ctx.tenant_id, booking_id)
        rows = TravelBookingDetailRepository.list_itinerary(ctx.tenant_id, booking_id)
        return [TravelBookingDetailService.serialize_itinerary(row) for row in rows]

    @staticmethod
    def create_itinerary(booking_id: str, **fields):
        ctx, _ = TravelBookingDetailService._require(write=True)
        TravelBookingDetailService._booking(ctx.tenant_id, booking_id)
        item_type = (fields.get("item_type") or "ACTIVITY").strip().upper()
        if item_type not in ALLOWED_ITINERARY_TYPES:
            raise ValidationError("Invalid item_type")
        title = (fields.get("title") or "").strip()
        if not title:
            raise ValidationError("title is required")
        row = TravelItineraryItem(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            booking_id=booking_id,
            item_type=item_type,
            day_number=fields.get("day_number"),
            title=title,
            description=(fields.get("description") or "").strip() or None,
            location=(fields.get("location") or "").strip() or None,
            vendor_name=(fields.get("vendor_name") or "").strip() or None,
            confirmation_ref=(fields.get("confirmation_ref") or "").strip() or None,
            start_at=TravelBookingDetailService._parse_dt(
                fields.get("start_at"), field="start_at"
            ),
            end_at=TravelBookingDetailService._parse_dt(fields.get("end_at"), field="end_at"),
            sort_order=int(fields.get("sort_order") or 0),
            notes=(fields.get("notes") or "").strip() or None,
        )
        TravelBookingDetailRepository.add_itinerary(row)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_TRAVEL_ITINERARY_ITEM",
            entity_type="TRAVEL_ITINERARY_ITEM",
            entity_id=row.id,
            new_data={"booking_id": booking_id, "item_type": item_type, "title": title},
        )
        db.session.commit()
        return TravelBookingDetailService.serialize_itinerary(row)

    @staticmethod
    def update_itinerary(booking_id: str, item_id: str, **fields):
        ctx, _ = TravelBookingDetailService._require(write=True)
        TravelBookingDetailService._booking(ctx.tenant_id, booking_id)
        row = TravelBookingDetailRepository.get_itinerary_item(
            ctx.tenant_id, booking_id, item_id
        )
        if row is None:
            raise NotFoundError("Itinerary item not found")
        if "item_type" in fields and fields["item_type"] is not None:
            item_type = str(fields["item_type"]).strip().upper()
            if item_type not in ALLOWED_ITINERARY_TYPES:
                raise ValidationError("Invalid item_type")
            row.item_type = item_type
        if "title" in fields and fields["title"] is not None:
            title = str(fields["title"]).strip()
            if not title:
                raise ValidationError("title is required")
            row.title = title
        if "day_number" in fields:
            row.day_number = fields["day_number"]
        if "description" in fields:
            row.description = (fields["description"] or "").strip() or None
        if "location" in fields:
            row.location = (fields["location"] or "").strip() or None
        if "vendor_name" in fields:
            row.vendor_name = (fields["vendor_name"] or "").strip() or None
        if "confirmation_ref" in fields:
            row.confirmation_ref = (fields["confirmation_ref"] or "").strip() or None
        if "start_at" in fields:
            row.start_at = TravelBookingDetailService._parse_dt(
                fields.get("start_at"), field="start_at"
            )
        if "end_at" in fields:
            row.end_at = TravelBookingDetailService._parse_dt(
                fields.get("end_at"), field="end_at"
            )
        if "sort_order" in fields and fields["sort_order"] is not None:
            row.sort_order = int(fields["sort_order"])
        if "notes" in fields:
            row.notes = (fields["notes"] or "").strip() or None
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_TRAVEL_ITINERARY_ITEM",
            entity_type="TRAVEL_ITINERARY_ITEM",
            entity_id=row.id,
            new_data=TravelBookingDetailService.serialize_itinerary(row),
        )
        db.session.commit()
        return TravelBookingDetailService.serialize_itinerary(row)

    @staticmethod
    def delete_itinerary(booking_id: str, item_id: str):
        ctx, _ = TravelBookingDetailService._require(write=True)
        TravelBookingDetailService._booking(ctx.tenant_id, booking_id)
        row = TravelBookingDetailRepository.get_itinerary_item(
            ctx.tenant_id, booking_id, item_id
        )
        if row is None:
            raise NotFoundError("Itinerary item not found")
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="DELETE_TRAVEL_ITINERARY_ITEM",
            entity_type="TRAVEL_ITINERARY_ITEM",
            entity_id=row.id,
            old_data={"booking_id": booking_id, "title": row.title},
        )
        TravelBookingDetailRepository.delete_itinerary(row)
        db.session.commit()
        return {"deleted": True, "id": item_id}

    @staticmethod
    def list_documents(booking_id: str):
        ctx, _ = TravelBookingDetailService._require(write=False)
        TravelBookingDetailService._booking(ctx.tenant_id, booking_id)
        rows = TravelBookingDetailRepository.list_documents(ctx.tenant_id, booking_id)
        return [TravelBookingDetailService.serialize_document(row) for row in rows]

    @staticmethod
    def create_document(booking_id: str, **fields):
        ctx, _ = TravelBookingDetailService._require(write=True)
        TravelBookingDetailService._booking(ctx.tenant_id, booking_id)
        doc_type = (fields.get("document_type") or "OTHER").strip().upper()
        if doc_type not in ALLOWED_DOCUMENT_TYPES:
            raise ValidationError("Invalid document_type")
        row = TravelBookingDocument(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            booking_id=booking_id,
            document_type=doc_type,
            holder_name=(fields.get("holder_name") or "").strip() or None,
            document_number=(fields.get("document_number") or "").strip() or None,
            issued_country=(fields.get("issued_country") or "").strip() or None,
            expiry_date=TravelBookingDetailService._parse_date(
                fields.get("expiry_date"), field="expiry_date"
            ),
            file_name=(fields.get("file_name") or "").strip() or None,
            notes=(fields.get("notes") or "").strip() or None,
            created_by=ctx.user_id,
        )
        TravelBookingDetailRepository.add_document(row)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_TRAVEL_BOOKING_DOCUMENT",
            entity_type="TRAVEL_BOOKING_DOCUMENT",
            entity_id=row.id,
            new_data={
                "booking_id": booking_id,
                "document_type": doc_type,
                "document_number": row.document_number,
            },
        )
        db.session.commit()
        return TravelBookingDetailService.serialize_document(row)

    @staticmethod
    def delete_document(booking_id: str, document_id: str):
        ctx, _ = TravelBookingDetailService._require(write=True)
        TravelBookingDetailService._booking(ctx.tenant_id, booking_id)
        row = TravelBookingDetailRepository.get_document(
            ctx.tenant_id, booking_id, document_id
        )
        if row is None:
            raise NotFoundError("Document not found")
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="DELETE_TRAVEL_BOOKING_DOCUMENT",
            entity_type="TRAVEL_BOOKING_DOCUMENT",
            entity_id=row.id,
            old_data={
                "booking_id": booking_id,
                "document_type": row.document_type,
                "document_number": row.document_number,
            },
        )
        TravelBookingDetailRepository.delete_document(row)
        db.session.commit()
        return {"deleted": True, "id": document_id}
