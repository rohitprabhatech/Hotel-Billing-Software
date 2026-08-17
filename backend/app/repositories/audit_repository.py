"""Audit log persistence."""

from app.extensions import db
from app.models.audit_log import AuditLog


class AuditRepository:
    @staticmethod
    def add(log: AuditLog) -> AuditLog:
        db.session.add(log)
        return log

    @staticmethod
    def commit():
        db.session.commit()