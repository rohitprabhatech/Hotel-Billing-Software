"""Tenant data access."""

from app.extensions import db
from app.models.tenant import Tenant


class TenantRepository:
    @staticmethod
    def get_by_id(tenant_id: str) -> Tenant | None:
        return db.session.get(Tenant, tenant_id)

    @staticmethod
    def add(tenant: Tenant) -> Tenant:
        db.session.add(tenant)
        return tenant

    @staticmethod
    def commit():
        db.session.commit()