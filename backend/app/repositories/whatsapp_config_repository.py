"""WhatsApp config data access — tenant scoped."""

from app.extensions import db
from app.models.tenant_whatsapp_config import TenantWhatsappConfig


class WhatsappConfigRepository:
    @staticmethod
    def get_by_tenant(tenant_id: str) -> TenantWhatsappConfig | None:
        return db.session.get(TenantWhatsappConfig, tenant_id)

    @staticmethod
    def upsert(row: TenantWhatsappConfig) -> TenantWhatsappConfig:
        db.session.add(row)
        return row
