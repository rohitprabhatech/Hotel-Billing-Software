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
    def latest_delivery_status_maps(
        tenant_id: str, bill_ids: list[str]
    ) -> tuple[dict[str, str], dict[str, str]]:
        """Latest WhatsApp and email status per bill in one query."""
        if not bill_ids:
            return {}, {}
        rows = (
            db.session.query(BillDelivery)
            .filter(
                BillDelivery.tenant_id == tenant_id,
                BillDelivery.bill_id.in_(bill_ids),
                BillDelivery.delivery_method.in_(("WHATSAPP", "EMAIL")),
            )
            .order_by(BillDelivery.created_at.desc())
            .all()
        )
        wa: dict[str, str] = {}
        email: dict[str, str] = {}
        for row in rows:
            if row.delivery_method == "WHATSAPP":
                if row.bill_id not in wa:
                    wa[row.bill_id] = row.status
            elif row.delivery_method == "EMAIL":
                if row.bill_id not in email:
                    email[row.bill_id] = row.status
        return wa, email

    @staticmethod
    def latest_whatsapp_status_map(tenant_id: str, bill_ids: list[str]) -> dict[str, str]:
        wa, _ = BillDeliveryRepository.latest_delivery_status_maps(tenant_id, bill_ids)
        return wa

    @staticmethod
    def latest_email_status_map(tenant_id: str, bill_ids: list[str]) -> dict[str, str]:
        _, email = BillDeliveryRepository.latest_delivery_status_maps(tenant_id, bill_ids)
        return email

    @staticmethod
    def delivery_status_counts(
        tenant_id: str, *, delivery_method: str, date_from, date_to
    ) -> dict[str, int | float | None]:
        """
        Count latest delivery status per bill for deliveries of the given method
        created in [date_from, date_to).
        """
        from sqlalchemy import and_, func

        latest = (
            db.session.query(
                BillDelivery.bill_id.label("bill_id"),
                func.max(BillDelivery.created_at).label("max_created"),
            )
            .filter(
                BillDelivery.tenant_id == tenant_id,
                BillDelivery.delivery_method == delivery_method,
                BillDelivery.created_at >= date_from,
                BillDelivery.created_at < date_to,
            )
            .group_by(BillDelivery.bill_id)
            .subquery()
        )
        rows = (
            db.session.query(BillDelivery.status, func.count())
            .join(
                latest,
                and_(
                    BillDelivery.bill_id == latest.c.bill_id,
                    BillDelivery.created_at == latest.c.max_created,
                    BillDelivery.tenant_id == tenant_id,
                    BillDelivery.delivery_method == delivery_method,
                ),
            )
            .group_by(BillDelivery.status)
            .all()
        )
        counts = {
            "pending": 0,
            "sent": 0,
            "delivered": 0,
            "read": 0,
            "failed": 0,
        }
        key_map = {
            "PENDING": "pending",
            "SENT": "sent",
            "DELIVERED": "delivered",
            "READ": "read",
            "FAILED": "failed",
        }
        for status, n in rows:
            k = key_map.get(status)
            if k:
                counts[k] = int(n or 0)
        total = sum(counts.values())
        if delivery_method == "EMAIL":
            reached = counts["sent"]
        else:
            reached = counts["delivered"] + counts["read"]
        success_rate = round((reached / total) * 100, 1) if total else None
        return {
            **counts,
            "total": total,
            "success_rate": success_rate,
        }

    @staticmethod
    def whatsapp_status_counts(tenant_id: str, *, date_from, date_to):
        return BillDeliveryRepository.delivery_status_counts(
            tenant_id,
            delivery_method="WHATSAPP",
            date_from=date_from,
            date_to=date_to,
        )

    @staticmethod
    def email_status_counts(tenant_id: str, *, date_from, date_to):
        return BillDeliveryRepository.delivery_status_counts(
            tenant_id,
            delivery_method="EMAIL",
            date_from=date_from,
            date_to=date_to,
        )