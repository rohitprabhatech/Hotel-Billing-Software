"""Travel agent + commission data access (BIZ-59)."""

from sqlalchemy import case, func

from app.extensions import db
from app.models.travel_agent import TravelAgent, TravelCommissionEntry


class TravelAgentRepository:
    @staticmethod
    def get_by_id(tenant_id: str, agent_id: str) -> TravelAgent | None:
        return TravelAgent.query.filter_by(tenant_id=tenant_id, id=agent_id).first()

    @staticmethod
    def get_by_code(tenant_id: str, code: str) -> TravelAgent | None:
        return TravelAgent.query.filter_by(tenant_id=tenant_id, code=code).first()

    @staticmethod
    def list_for_tenant(
        tenant_id: str, *, active_only: bool = False, page: int = 1, per_page: int = 50
    ) -> tuple[list[TravelAgent], int]:
        q = TravelAgent.query.filter_by(tenant_id=tenant_id)
        if active_only:
            q = q.filter_by(is_active=True)
        total = q.count()
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 50), 1), 100)
        rows = (
            q.order_by(TravelAgent.name.asc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, total

    @staticmethod
    def add(row: TravelAgent) -> TravelAgent:
        db.session.add(row)
        return row


class TravelCommissionRepository:
    @staticmethod
    def get_by_id(tenant_id: str, entry_id: str) -> TravelCommissionEntry | None:
        return TravelCommissionEntry.query.filter_by(
            tenant_id=tenant_id, id=entry_id
        ).first()

    @staticmethod
    def get_by_booking(tenant_id: str, booking_id: str) -> TravelCommissionEntry | None:
        return TravelCommissionEntry.query.filter_by(
            tenant_id=tenant_id, booking_id=booking_id
        ).first()

    @staticmethod
    def list_for_tenant(
        tenant_id: str,
        *,
        agent_id: str | None = None,
        status: str | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[TravelCommissionEntry], int]:
        q = TravelCommissionEntry.query.filter_by(tenant_id=tenant_id)
        if agent_id:
            q = q.filter_by(agent_id=agent_id)
        if status:
            q = q.filter_by(status=status)
        total = q.count()
        page = max(int(page or 1), 1)
        per_page = min(max(int(per_page or 50), 1), 100)
        rows = (
            q.order_by(TravelCommissionEntry.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return rows, total

    @staticmethod
    def report_by_agent(tenant_id: str) -> list[dict]:
        rows = (
            db.session.query(
                TravelCommissionEntry.agent_id,
                TravelAgent.code,
                TravelAgent.name,
                func.count(TravelCommissionEntry.id).label("entry_count"),
                func.coalesce(func.sum(TravelCommissionEntry.booking_total), 0).label(
                    "booking_total"
                ),
                func.coalesce(func.sum(TravelCommissionEntry.commission_amount), 0).label(
                    "commission_total"
                ),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                TravelCommissionEntry.status == "PENDING",
                                TravelCommissionEntry.commission_amount,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label("pending_total"),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                TravelCommissionEntry.status == "PAID",
                                TravelCommissionEntry.commission_amount,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label("paid_total"),
            )
            .join(TravelAgent, TravelAgent.id == TravelCommissionEntry.agent_id)
            .filter(TravelCommissionEntry.tenant_id == tenant_id)
            .filter(TravelCommissionEntry.status != "CANCELLED")
            .group_by(TravelCommissionEntry.agent_id, TravelAgent.code, TravelAgent.name)
            .order_by(TravelAgent.name.asc())
            .all()
        )
        return [
            {
                "agent_id": row.agent_id,
                "agent_code": row.code,
                "agent_name": row.name,
                "entry_count": int(row.entry_count or 0),
                "booking_total": row.booking_total,
                "commission_total": row.commission_total,
                "pending_total": row.pending_total,
                "paid_total": row.paid_total,
            }
            for row in rows
        ]

    @staticmethod
    def add(row: TravelCommissionEntry) -> TravelCommissionEntry:
        db.session.add(row)
        return row
