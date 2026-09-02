"""Travel bookings with advances and status pipeline (BIZ-57)."""

from datetime import datetime, timezone
from decimal import Decimal

from app.constants.payments import DEFAULT_PAYMENT_METHOD, normalize_payment_method
from app.constants.permissions import PERM_BILLING
from app.extensions import db
from app.models.role import ROLE_BILLING_USER
from app.models.travel_booking import (
    STATUS_BOOKED,
    STATUS_CANCELLED,
    STATUS_COMPLETED,
    STATUS_CONFIRMED,
    STATUS_TRANSITIONS,
    TravelBooking,
    TravelBookingPayment,
)
from app.repositories.customer_repository import CustomerRepository
from app.repositories.tenant_repository import TenantRepository
from app.repositories.tour_package_repository import TourPackageRepository
from app.repositories.travel_booking_repository import TravelBookingRepository
from app.services.audit_service import AuditService
from app.services.module_service import ModuleService
from app.services.notification_service import NotificationService
from app.utils.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import money
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context

MODULE = "travel_bookings"
ZERO = Decimal("0.00")


class TravelBookingService:
    @staticmethod
    def _require(*, write: bool = False, manage: bool = False):
        require_permission(PERM_BILLING)
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, MODULE)
        if (write or manage) and ctx.role == ROLE_BILLING_USER and manage:
            raise ForbiddenError("Only the owner or manager can change booking status")
        return ctx, tenant

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
    def serialize(row: TravelBooking) -> dict:
        total = money(row.total_amount)
        advance = money(row.advance_paid)
        remaining = money(total - advance)
        return {
            "id": row.id,
            "booking_number": row.booking_number,
            "package_id": row.package_id,
            "package_name": row.package_name,
            "customer_id": row.customer_id,
            "customer_name": row.customer_name,
            "customer_phone": row.customer_phone,
            "pax_count": int(row.pax_count or 1),
            "travel_start_at": row.travel_start_at.isoformat() if row.travel_start_at else None,
            "travel_end_at": row.travel_end_at.isoformat() if row.travel_end_at else None,
            "total_amount": float(total),
            "advance_paid": float(advance),
            "remaining_amount": float(remaining),
            "status": row.status,
            "notes": row.notes,
            "bill_id": row.bill_id,
            "agent_id": row.agent_id,
            "agent_name": row.agent.name if row.agent else None,
            "agent_code": row.agent.code if row.agent else None,
            "commission": (
                {
                    "id": row.commission_entry.id,
                    "commission_percent": float(row.commission_entry.commission_percent),
                    "commission_amount": float(row.commission_entry.commission_amount),
                    "status": row.commission_entry.status,
                }
                if row.commission_entry
                else None
            ),
            "completed_at": row.completed_at.isoformat() if row.completed_at else None,
            "created_by": row.created_by,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
            "payments": [
                {
                    "id": pay.id,
                    "amount": float(pay.amount),
                    "payment_method": pay.payment_method,
                    "notes": pay.notes,
                    "created_at": pay.created_at.isoformat() if pay.created_at else None,
                }
                for pay in (row.payments or [])
            ],
            "itinerary_count": len(row.itinerary_items or []),
            "document_count": len(row.documents or []),
        }

    @staticmethod
    def _add_payment(order: TravelBooking, *, amount: Decimal, payment_method: str, notes=None):
        method = normalize_payment_method(payment_method or DEFAULT_PAYMENT_METHOD)
        pay = TravelBookingPayment(
            id=new_uuid(),
            tenant_id=order.tenant_id,
            booking_id=order.id,
            amount=amount,
            payment_method=method,
            notes=(notes or "").strip() or None,
            created_by=require_request_context().user_id,
        )
        TravelBookingRepository.add_payment(pay)
        order.advance_paid = money(order.advance_paid) + amount
        return pay

    @staticmethod
    def list_bookings(*, status=None, page=1, per_page=50):
        ctx, _ = TravelBookingService._require()
        rows, total = TravelBookingRepository.list_for_tenant(
            ctx.tenant_id, status=status, page=page, per_page=per_page
        )
        return (
            [TravelBookingService.serialize(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def get_booking(booking_id: str):
        ctx, _ = TravelBookingService._require()
        row = TravelBookingRepository.get_by_id(ctx.tenant_id, booking_id)
        if row is None:
            raise NotFoundError("Travel booking not found")
        return TravelBookingService.serialize(row)

    @staticmethod
    def create(
        *,
        package_id: str,
        customer_id=None,
        customer_name=None,
        customer_phone=None,
        pax_count=1,
        total_amount=None,
        advance_amount=0,
        payment_method=DEFAULT_PAYMENT_METHOD,
        travel_start_at=None,
        travel_end_at=None,
        notes=None,
        agent_id=None,
        commission_percent=None,
    ):
        ctx, _ = TravelBookingService._require(write=True)
        package = TourPackageRepository.get_by_id(ctx.tenant_id, package_id)
        if package is None or not package.is_active:
            raise ValidationError("Tour package not found or inactive")

        pax = int(pax_count or 1)
        if pax < 1:
            raise ValidationError("pax_count must be at least 1")

        if total_amount is None or str(total_amount).strip() == "":
            total = money(package.base_price) * pax
        else:
            total = money(total_amount)
        if total <= ZERO:
            raise ValidationError("total_amount must be greater than zero")

        advance = money(advance_amount or 0)
        if advance < ZERO:
            raise ValidationError("advance_amount cannot be negative")
        if advance > total:
            raise ValidationError("Advance cannot exceed total amount")

        cust_id = (customer_id or "").strip() or None
        name = (customer_name or "").strip() or None
        phone = (customer_phone or "").strip() or None
        if cust_id:
            customer = CustomerRepository.get_by_id_and_tenant(cust_id, ctx.tenant_id)
            if customer is None:
                raise ValidationError("Customer not found")
            name = name or customer.name
            phone = phone or getattr(customer, "phone_e164", None) or getattr(
                customer, "phone_national", None
            )

        start = TravelBookingService._parse_dt(travel_start_at, field="travel_start_at")
        end = TravelBookingService._parse_dt(travel_end_at, field="travel_end_at")
        if start and end and end < start:
            raise ValidationError("travel_end_at must be on or after travel_start_at")

        resolved_agent = (agent_id or "").strip() or None
        if resolved_agent:
            from app.repositories.travel_agent_repository import TravelAgentRepository

            agent = TravelAgentRepository.get_by_id(ctx.tenant_id, resolved_agent)
            if agent is None or not agent.is_active:
                raise ValidationError("Travel agent not found or inactive")

        sequence, number = TravelBookingRepository.allocate_number(ctx.tenant_id)
        booking = TravelBooking(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            booking_number=number,
            booking_sequence=sequence,
            package_id=package.id,
            package_name=package.name,
            customer_id=cust_id,
            customer_name=name,
            customer_phone=phone,
            pax_count=pax,
            travel_start_at=start,
            travel_end_at=end,
            total_amount=total,
            advance_paid=ZERO,
            status=STATUS_BOOKED,
            notes=(notes or "").strip() or None,
            agent_id=resolved_agent,
            created_by=ctx.user_id,
        )
        TravelBookingRepository.add(booking)
        db.session.flush()

        if advance > ZERO:
            TravelBookingService._add_payment(
                booking,
                amount=advance,
                payment_method=payment_method,
                notes="Initial advance",
            )

        if resolved_agent:
            from app.services.travel_agent_service import TravelAgentService

            TravelAgentService.ensure_commission_for_booking(
                tenant_id=ctx.tenant_id,
                booking=booking,
                agent_id=resolved_agent,
                commission_percent=commission_percent,
                user_id=ctx.user_id,
                commit=False,
            )

        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_TRAVEL_BOOKING",
            entity_type="TRAVEL_BOOKING",
            entity_id=booking.id,
            new_data={
                "booking_number": number,
                "package_id": package.id,
                "total_amount": float(total),
                "advance_paid": float(booking.advance_paid),
                "agent_id": resolved_agent,
            },
        )
        remaining = money(booking.total_amount) - money(booking.advance_paid)
        if remaining > ZERO:
            NotificationService.notify_travel_payment_due(
                tenant_id=ctx.tenant_id,
                booking_number=number,
                customer_name=name or "Customer",
                remaining=remaining,
            )
        db.session.commit()
        return TravelBookingService.serialize(
            TravelBookingRepository.get_by_id(ctx.tenant_id, booking.id)
        )

    @staticmethod
    def record_payment(*, booking_id: str, amount, payment_method="cash", notes=None):
        ctx, _ = TravelBookingService._require(write=True)
        booking = TravelBookingRepository.get_by_id(ctx.tenant_id, booking_id)
        if booking is None:
            raise NotFoundError("Travel booking not found")
        if booking.status in (STATUS_CANCELLED, STATUS_COMPLETED):
            raise ValidationError("Cannot record payment on a cancelled or completed booking")

        pay_amount = money(amount)
        if pay_amount <= ZERO:
            raise ValidationError("amount must be greater than zero")
        remaining = money(booking.total_amount) - money(booking.advance_paid)
        if pay_amount > remaining:
            raise ValidationError(
                f"Payment exceeds remaining balance. Remaining: {float(remaining):.2f}."
            )

        TravelBookingService._add_payment(
            booking,
            amount=pay_amount,
            payment_method=payment_method,
            notes=notes,
        )
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="TRAVEL_BOOKING_PAYMENT",
            entity_type="TRAVEL_BOOKING",
            entity_id=booking.id,
            new_data={
                "amount": float(pay_amount),
                "advance_paid": float(booking.advance_paid),
                "remaining": float(money(booking.total_amount) - money(booking.advance_paid)),
            },
        )
        db.session.commit()
        return TravelBookingService.serialize(
            TravelBookingRepository.get_by_id(ctx.tenant_id, booking.id)
        )

    @staticmethod
    def update_status(booking_id: str, *, status: str):
        ctx, _ = TravelBookingService._require(manage=True)
        booking = TravelBookingRepository.get_by_id(ctx.tenant_id, booking_id)
        if booking is None:
            raise NotFoundError("Travel booking not found")
        new_status = (status or "").strip().upper()
        allowed = STATUS_TRANSITIONS.get(booking.status, set())
        if new_status not in allowed:
            raise ValidationError(
                f"Cannot move booking from {booking.status} to {new_status}"
            )

        booking.status = new_status
        if new_status == STATUS_COMPLETED:
            remaining = money(booking.total_amount) - money(booking.advance_paid)
            if remaining > ZERO:
                raise ValidationError(
                    f"Cannot complete booking with outstanding balance of {float(remaining):.2f}."
                )
            booking.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)

        if new_status == STATUS_CONFIRMED:
            NotificationService.notify_travel_booking_confirmed(
                tenant_id=ctx.tenant_id,
                booking_number=booking.booking_number,
                package_name=booking.package_name,
                customer_name=booking.customer_name or "Customer",
            )
            remaining = money(booking.total_amount) - money(booking.advance_paid)
            if remaining > ZERO:
                NotificationService.notify_travel_payment_due(
                    tenant_id=ctx.tenant_id,
                    booking_number=booking.booking_number,
                    customer_name=booking.customer_name or "Customer",
                    remaining=remaining,
                )

        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_TRAVEL_BOOKING_STATUS",
            entity_type="TRAVEL_BOOKING",
            entity_id=booking.id,
            new_data={"status": new_status, "booking_number": booking.booking_number},
        )
        db.session.commit()
        return TravelBookingService.serialize(booking)

    @staticmethod
    def update_booking(booking_id: str, **fields):
        from app.utils.owner_access import require_owner

        require_owner()
        ctx, _ = TravelBookingService._require(write=True)
        booking = TravelBookingRepository.get_by_id(ctx.tenant_id, booking_id)
        if booking is None:
            raise NotFoundError("Travel booking not found")
        if booking.status in (STATUS_COMPLETED, STATUS_CANCELLED):
            raise ValidationError("Cannot edit a completed or cancelled booking")

        if "customer_name" in fields:
            booking.customer_name = (fields.get("customer_name") or "").strip() or None
        if "customer_phone" in fields:
            booking.customer_phone = (fields.get("customer_phone") or "").strip() or None
        if "pax_count" in fields and fields.get("pax_count") is not None:
            pax = int(fields["pax_count"])
            if pax < 1:
                raise ValidationError("pax_count must be at least 1")
            package = TourPackageRepository.get_by_id(ctx.tenant_id, booking.package_id)
            if package is None:
                raise ValidationError("Linked package not found")
            booking.pax_count = pax
            new_total = money(package.base_price) * pax
            if new_total < money(booking.advance_paid):
                raise ValidationError("New total cannot be less than advance already paid")
            booking.total_amount = new_total
        if "notes" in fields:
            booking.notes = (fields.get("notes") or "").strip() or None
        if "travel_start_at" in fields:
            booking.travel_start_at = TravelBookingService._parse_dt(
                fields.get("travel_start_at"), field="travel_start_at"
            )
        if "travel_end_at" in fields:
            booking.travel_end_at = TravelBookingService._parse_dt(
                fields.get("travel_end_at"), field="travel_end_at"
            )
        if booking.travel_start_at and booking.travel_end_at and booking.travel_end_at < booking.travel_start_at:
            raise ValidationError("travel_end_at must be on or after travel_start_at")
        if "agent_id" in fields:
            agent_id = (fields.get("agent_id") or "").strip() or None
            booking.agent_id = agent_id
            if agent_id:
                from app.services.travel_agent_service import TravelAgentService

                TravelAgentService.ensure_commission_for_booking(
                    tenant_id=ctx.tenant_id,
                    booking=booking,
                    agent_id=agent_id,
                    user_id=ctx.user_id,
                    commit=False,
                )

        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_TRAVEL_BOOKING",
            entity_type="TRAVEL_BOOKING",
            entity_id=booking.id,
            new_data={"booking_number": booking.booking_number},
        )
        db.session.commit()
        return TravelBookingService.serialize(booking)

    @staticmethod
    def delete_booking(booking_id: str):
        from app.utils.owner_access import require_owner

        require_owner()
        return TravelBookingService.update_status(booking_id, status=STATUS_CANCELLED)
