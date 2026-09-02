"""Travel agents and commission calculation (BIZ-59)."""

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from app.constants.permissions import PERM_BILLING
from app.extensions import db
from app.models.role import ROLE_BILLING_USER, ROLE_OWNER
from app.models.travel_agent import (
    COMMISSION_CANCELLED,
    COMMISSION_PAID,
    COMMISSION_PENDING,
    TravelAgent,
    TravelCommissionEntry,
)
from app.repositories.tenant_repository import TenantRepository
from app.repositories.travel_agent_repository import (
    TravelAgentRepository,
    TravelCommissionRepository,
)
from app.repositories.travel_booking_repository import TravelBookingRepository
from app.services.audit_service import AuditService
from app.services.module_service import ModuleService
from app.utils.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.money import money
from app.utils.permission_access import require_permission
from app.utils.request_context import require_request_context

MODULE = "travel_commission"
ZERO = Decimal("0.00")
HUNDRED = Decimal("100")


class TravelAgentService:
    @staticmethod
    def _require(*, write: bool = False):
        require_permission(PERM_BILLING)
        ctx = require_request_context()
        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found")
        ModuleService.require_enabled(tenant, MODULE)
        if write and ctx.role != ROLE_OWNER:
            raise ForbiddenError("Only the owner can manage travel agents")
        return ctx, tenant

    @staticmethod
    def _require_write():
        return TravelAgentService._require(write=True)

    @staticmethod
    def _parse_percent(value) -> Decimal:
        try:
            pct = money(Decimal(str(value if value is not None else 0)))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValidationError("commission_percent must be a valid number") from exc
        if pct < ZERO or pct > HUNDRED:
            raise ValidationError("commission_percent must be between 0 and 100")
        return pct

    @staticmethod
    def calc_commission(booking_total, commission_percent) -> Decimal:
        total = money(booking_total)
        pct = money(commission_percent)
        return money(total * pct / HUNDRED)

    @staticmethod
    def serialize_agent(row: TravelAgent) -> dict:
        return {
            "id": row.id,
            "code": row.code,
            "name": row.name,
            "phone": row.phone,
            "email": row.email,
            "commission_percent": float(row.commission_percent),
            "is_active": bool(row.is_active),
            "notes": row.notes,
            "created_by": row.created_by,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }

    @staticmethod
    def serialize_entry(row: TravelCommissionEntry) -> dict:
        agent = row.agent
        return {
            "id": row.id,
            "agent_id": row.agent_id,
            "agent_code": agent.code if agent else None,
            "agent_name": agent.name if agent else None,
            "booking_id": row.booking_id,
            "booking_number": row.booking_number,
            "booking_total": float(row.booking_total),
            "commission_percent": float(row.commission_percent),
            "commission_amount": float(row.commission_amount),
            "status": row.status,
            "notes": row.notes,
            "created_by": row.created_by,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
            "paid_at": row.paid_at.isoformat() if row.paid_at else None,
        }

    @staticmethod
    def list_agents(*, active_only: bool = False, page=1, per_page=50):
        ctx, _ = TravelAgentService._require()
        rows, total = TravelAgentRepository.list_for_tenant(
            ctx.tenant_id, active_only=active_only, page=page, per_page=per_page
        )
        return (
            [TravelAgentService.serialize_agent(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def get_agent(agent_id: str):
        ctx, _ = TravelAgentService._require()
        row = TravelAgentRepository.get_by_id(ctx.tenant_id, agent_id)
        if row is None:
            raise NotFoundError("Travel agent not found")
        return TravelAgentService.serialize_agent(row)

    @staticmethod
    def create_agent(**fields):
        ctx, _ = TravelAgentService._require_write()
        code = (fields.get("code") or "").strip().upper()
        name = (fields.get("name") or "").strip()
        if not code or not name:
            raise ValidationError("code and name are required")
        if TravelAgentRepository.get_by_code(ctx.tenant_id, code):
            raise ValidationError("An agent with this code already exists")
        pct = TravelAgentService._parse_percent(fields.get("commission_percent"))
        row = TravelAgent(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            code=code,
            name=name,
            phone=(fields.get("phone") or "").strip() or None,
            email=(fields.get("email") or "").strip() or None,
            commission_percent=pct,
            is_active=bool(fields.get("is_active", True)),
            notes=(fields.get("notes") or "").strip() or None,
            created_by=ctx.user_id,
        )
        TravelAgentRepository.add(row)
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="CREATE_TRAVEL_AGENT",
            entity_type="TRAVEL_AGENT",
            entity_id=row.id,
            new_data={"code": code, "name": name, "commission_percent": float(pct)},
        )
        db.session.commit()
        return TravelAgentService.serialize_agent(row)

    @staticmethod
    def update_agent(agent_id: str, **fields):
        ctx, _ = TravelAgentService._require_write()
        raw_keys = set(fields.keys())
        row = TravelAgentRepository.get_by_id(ctx.tenant_id, agent_id)
        if row is None:
            raise NotFoundError("Travel agent not found")
        old = TravelAgentService.serialize_agent(row)
        if "code" in raw_keys and fields.get("code") is not None:
            code = str(fields["code"]).strip().upper()
            if not code:
                raise ValidationError("code is required")
            existing = TravelAgentRepository.get_by_code(ctx.tenant_id, code)
            if existing and existing.id != row.id:
                raise ValidationError("An agent with this code already exists")
            row.code = code
        if "name" in raw_keys and fields.get("name") is not None:
            name = str(fields["name"]).strip()
            if not name:
                raise ValidationError("name is required")
            row.name = name
        if "phone" in raw_keys:
            row.phone = (fields.get("phone") or "").strip() or None
        if "email" in raw_keys:
            row.email = (fields.get("email") or "").strip() or None
        if "commission_percent" in raw_keys and fields.get("commission_percent") is not None:
            row.commission_percent = TravelAgentService._parse_percent(
                fields.get("commission_percent")
            )
        if "notes" in raw_keys:
            row.notes = (fields.get("notes") or "").strip() or None
        if "is_active" in raw_keys and fields.get("is_active") is not None:
            row.is_active = bool(fields["is_active"])
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_TRAVEL_AGENT",
            entity_type="TRAVEL_AGENT",
            entity_id=row.id,
            old_data=old,
            new_data=TravelAgentService.serialize_agent(row),
        )
        db.session.commit()
        return TravelAgentService.serialize_agent(row)

    @staticmethod
    def delete_agent(agent_id: str):
        from app.utils.owner_access import require_owner

        require_owner()
        ctx, _ = TravelAgentService._require(write=True)
        row = TravelAgentRepository.get_by_id(ctx.tenant_id, agent_id)
        if row is None:
            raise NotFoundError("Travel agent not found")
        old = TravelAgentService.serialize_agent(row)
        row.is_active = False
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="DELETE_TRAVEL_AGENT",
            entity_type="TRAVEL_AGENT",
            entity_id=row.id,
            old_data=old,
            new_data=TravelAgentService.serialize_agent(row),
        )
        db.session.commit()
        return TravelAgentService.serialize_agent(row)

    @staticmethod
    def ensure_commission_for_booking(
        *,
        tenant_id: str,
        booking,
        agent_id: str | None,
        commission_percent=None,
        notes=None,
        user_id: str,
        commit: bool = False,
    ) -> TravelCommissionEntry | None:
        """Create or refresh a commission entry for a booking. Caller may own the txn."""
        if not agent_id:
            return None
        agent = TravelAgentRepository.get_by_id(tenant_id, agent_id)
        if agent is None or not agent.is_active:
            raise ValidationError("Travel agent not found or inactive")
        pct = (
            TravelAgentService._parse_percent(commission_percent)
            if commission_percent is not None
            else money(agent.commission_percent)
        )
        total = money(booking.total_amount)
        amount = TravelAgentService.calc_commission(total, pct)
        existing = TravelCommissionRepository.get_by_booking(tenant_id, booking.id)
        if existing is not None:
            if existing.status == COMMISSION_PAID:
                raise ValidationError("Cannot change commission after it has been paid")
            existing.agent_id = agent.id
            existing.booking_number = booking.booking_number
            existing.booking_total = total
            existing.commission_percent = pct
            existing.commission_amount = amount
            existing.status = COMMISSION_PENDING
            if notes is not None:
                existing.notes = (notes or "").strip() or None
            entry = existing
            action = "UPDATE_TRAVEL_COMMISSION"
        else:
            entry = TravelCommissionEntry(
                id=new_uuid(),
                tenant_id=tenant_id,
                agent_id=agent.id,
                booking_id=booking.id,
                booking_number=booking.booking_number,
                booking_total=total,
                commission_percent=pct,
                commission_amount=amount,
                status=COMMISSION_PENDING,
                notes=(notes or "").strip() or None,
                created_by=user_id,
            )
            TravelCommissionRepository.add(entry)
            action = "CREATE_TRAVEL_COMMISSION"
        booking.agent_id = agent.id
        AuditService.log(
            tenant_id=tenant_id,
            action=action,
            entity_type="TRAVEL_COMMISSION_ENTRY",
            entity_id=entry.id,
            new_data={
                "booking_id": booking.id,
                "agent_id": agent.id,
                "commission_percent": float(pct),
                "commission_amount": float(amount),
            },
        )
        if commit:
            db.session.commit()
        return entry

    @staticmethod
    def create_commission(*, booking_id: str, agent_id=None, commission_percent=None, notes=None):
        ctx, _ = TravelAgentService._require_write()
        booking = TravelBookingRepository.get_by_id(ctx.tenant_id, booking_id)
        if booking is None:
            raise NotFoundError("Travel booking not found")
        resolved_agent = (agent_id or booking.agent_id or "").strip() or None
        if not resolved_agent:
            raise ValidationError("agent_id is required when the booking has no agent")
        entry = TravelAgentService.ensure_commission_for_booking(
            tenant_id=ctx.tenant_id,
            booking=booking,
            agent_id=resolved_agent,
            commission_percent=commission_percent,
            notes=notes,
            user_id=ctx.user_id,
            commit=True,
        )
        return TravelAgentService.serialize_entry(
            TravelCommissionRepository.get_by_id(ctx.tenant_id, entry.id)
        )

    @staticmethod
    def list_commissions(*, agent_id=None, status=None, page=1, per_page=50):
        ctx, _ = TravelAgentService._require()
        rows, total = TravelCommissionRepository.list_for_tenant(
            ctx.tenant_id, agent_id=agent_id, status=status, page=page, per_page=per_page
        )
        return (
            [TravelAgentService.serialize_entry(row) for row in rows],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def commission_report():
        ctx, _ = TravelAgentService._require()
        rows = TravelCommissionRepository.report_by_agent(ctx.tenant_id)
        return [
            {
                "agent_id": row["agent_id"],
                "agent_code": row["agent_code"],
                "agent_name": row["agent_name"],
                "entry_count": row["entry_count"],
                "booking_total": float(money(row["booking_total"])),
                "commission_total": float(money(row["commission_total"])),
                "pending_total": float(money(row["pending_total"])),
                "paid_total": float(money(row["paid_total"])),
            }
            for row in rows
        ]

    @staticmethod
    def update_commission_status(entry_id: str, *, status: str, notes=None):
        ctx, _ = TravelAgentService._require_write()
        row = TravelCommissionRepository.get_by_id(ctx.tenant_id, entry_id)
        if row is None:
            raise NotFoundError("Commission entry not found")
        new_status = (status or "").strip().upper()
        if new_status not in (COMMISSION_PENDING, COMMISSION_PAID, COMMISSION_CANCELLED):
            raise ValidationError("Invalid commission status")
        if row.status == COMMISSION_CANCELLED and new_status != COMMISSION_CANCELLED:
            raise ValidationError("Cancelled commission cannot be reopened")
        old_status = row.status
        row.status = new_status
        if notes is not None:
            row.notes = (notes or "").strip() or None
        if new_status == COMMISSION_PAID:
            row.paid_at = datetime.now(timezone.utc).replace(tzinfo=None)
        elif new_status == COMMISSION_PENDING:
            row.paid_at = None
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="UPDATE_TRAVEL_COMMISSION_STATUS",
            entity_type="TRAVEL_COMMISSION_ENTRY",
            entity_id=row.id,
            old_data={"status": old_status},
            new_data={"status": new_status, "commission_amount": float(row.commission_amount)},
        )
        db.session.commit()
        return TravelAgentService.serialize_entry(row)
