"""Bill delivery data access — tenant scoped."""

from app.extensions import db
from app.models.bill_delivery import BillDelivery


class BillDeliveryRepository:
    @staticmethod
    def add(row: BillDelivery) -> BillDelivery:
        db.session.add(row)
        return row

    @staticmethod
    def get_by_id_and_tenant(delivery_id: str, tenant_id: str) -> BillDelivery | None:
        return (
            db.session.query(BillDelivery)
            .filter(
                BillDelivery.id == delivery_id,
                BillDelivery.tenant_id == tenant_id,
            )
            .first()
        )

    @staticmethod
    def get_by_provider_message_id(provider_message_id: str) -> BillDelivery | None:
        if not provider_message_id:
            return None
        return (
            db.session.query(BillDelivery)
            .filter(BillDelivery.provider_message_id == provider_message_id)
            .order_by(BillDelivery.created_at.desc())
            .first()
        )

    @staticmethod
    def list_for_bill(tenant_id: str, bill_id: str) -> list[BillDelivery]:
        return (
            db.session.query(BillDelivery)
            .filter(
                BillDelivery.tenant_id == tenant_id,
                BillDelivery.bill_id == bill_id,
            )
            .order_by(BillDelivery.created_at.desc())
            .all()
        )

    @staticmethod
    def latest_whatsapp_status_map(tenant_id: str, bill_ids: list[str]) -> dict[str, str]:
        if not bill_ids:
            return {}
        rows = (
            db.session.query(BillDelivery)
            .filter(
                BillDelivery.tenant_id == tenant_id,
                BillDelivery.bill_id.in_(bill_ids),
                BillDelivery.delivery_method == "WHATSAPP",
            )
            .order_by(BillDelivery.created_at.desc())
            .all()
        )
        out: dict[str, str] = {}
        for row in rows:
            if row.bill_id not in out:
                out[row.bill_id] = row.status
        return out
