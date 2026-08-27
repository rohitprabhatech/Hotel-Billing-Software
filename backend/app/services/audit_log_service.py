"""Owner audit log listing, details, and activity alerts."""

from datetime import datetime, timedelta, timezone

from flask import current_app

from app.constants.audit_catalog import entity_types_for_module, list_audit_meta
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.repositories.audit_log_repository import (
    ACTIVITY_CATEGORY_FILTERS,
    AuditLogRepository,
)
from app.repositories.bill_repository import BillRepository
from app.repositories.user_repository import UserRepository
from app.utils.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.utils.periods import day_bounds, local_now, parse_date, to_utc_naive
from app.utils.request_context import require_request_context

# Soft thresholds for activity indicators (not accusations)
CANCEL_TODAY_THRESHOLD = 3
USER_CANCEL_THRESHOLD = 2
REPRINT_TODAY_THRESHOLD = 3
HIGH_DISCOUNT_AMOUNT = 100.0

ROLE_LABELS = {
    ROLE_OWNER: "Owner",
    ROLE_MANAGER: "Manager",
    ROLE_BILLING_USER: "Billing User",
}


class AuditLogService:
    @staticmethod
    def _ensure_owner():
        ctx = require_request_context()
        if ctx.role != ROLE_OWNER:
            raise ForbiddenError("Only business owners can access audit logs")
        return ctx

    @staticmethod
    def _tz():
        return current_app.config.get("REPORT_TIMEZONE", "Asia/Kolkata")

    @staticmethod
    def catalog_meta():
        AuditLogService._ensure_owner()
        return list_audit_meta()

    @staticmethod
    def list_logs(
        *,
        user_id=None,
        action=None,
        entity_type=None,
        entity_id=None,
        bill_number=None,
        q=None,
        from_date=None,
        to_date=None,
        module=None,
        category=None,
        page=1,
        per_page=50,
    ):
        ctx = AuditLogService._ensure_owner()
        date_from = date_to = None
        try:
            if from_date:
                date_from = to_utc_naive(parse_date(from_date, AuditLogService._tz()))
            if to_date:
                end_local = parse_date(to_date, AuditLogService._tz()) + timedelta(days=1)
                date_to = to_utc_naive(end_local)
        except ValueError as exc:
            raise ValidationError("Invalid date format. Use YYYY-MM-DD") from exc

        module_types = None
        if module:
            module_types = entity_types_for_module(module)
            if module_types is None:
                raise ValidationError(f"Unknown audit module: {module}")

        category_actions = None
        category_entity_types = None
        if category:
            key = str(category).strip().lower()
            spec = ACTIVITY_CATEGORY_FILTERS.get(key)
            if spec is None:
                raise ValidationError(f"Unknown activity category: {category}")
            category_actions = spec.get("actions")
            category_entity_types = spec.get("entity_types")

        # Explicit entity_type wins over module/category expansion when sent.
        entity_types = None
        filter_actions = None
        if entity_type:
            entity_type = str(entity_type).strip().upper() or None
        elif category_entity_types and not category_actions:
            entity_types = category_entity_types
        elif module_types:
            entity_types = module_types

        if category_actions and not action:
            filter_actions = category_actions

        rows, total = AuditLogRepository.list_by_tenant(
            ctx.tenant_id,
            user_id=user_id,
            action=action,
            actions=filter_actions,
            entity_type=entity_type,
            entity_types=entity_types,
            entity_id=entity_id,
            bill_number=bill_number,
            q=q,
            date_from=date_from,
            date_to=date_to,
            page=page,
            per_page=per_page,
        )
        role_map = UserRepository.map_roles_by_ids(
            [r.user_id for r in rows if r.user_id],
            ctx.tenant_id,
        )
        return (
            [
                AuditLogService.serialize(r, brief=True, user_role=role_map.get(r.user_id))
                for r in rows
            ],
            {
                "page": max(int(page or 1), 1),
                "per_page": min(max(int(per_page or 50), 1), 100),
                "total": total,
            },
        )

    @staticmethod
    def get_log(log_id: str):
        ctx = AuditLogService._ensure_owner()
        row = AuditLogRepository.get_by_id_and_tenant(log_id, ctx.tenant_id)
        if row is None:
            raise NotFoundError("Audit log not found")
        role_map = UserRepository.map_roles_by_ids(
            [row.user_id] if row.user_id else [],
            ctx.tenant_id,
        )
        return AuditLogService.serialize(
            row,
            brief=False,
            user_role=role_map.get(row.user_id),
        )

    @staticmethod
    def delete_log(log_id: str):
        ctx = AuditLogService._ensure_owner()
        deleted = AuditLogRepository.soft_delete(log_id, ctx.tenant_id)
        if not deleted:
            raise NotFoundError("Audit log not found")
        from app.extensions import db

        db.session.commit()
        return {"message": "Activity record removed"}

    @staticmethod
    def alerts():
        ctx = AuditLogService._ensure_owner()
        today = local_now(AuditLogService._tz()).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        start, end = day_bounds(today)
        alerts = []

        cancel_count = AuditLogRepository.count_actions(
            ctx.tenant_id, "CANCEL_BILL", start, end
        )
        if cancel_count >= CANCEL_TODAY_THRESHOLD:
            alerts.append(
                {
                    "type": "HIGH_CANCELLATIONS",
                    "severity": "medium",
                    "title": "High number of cancelled bills",
                    "message": f"{cancel_count} bill cancellations recorded today.",
                    "count": cancel_count,
                }
            )

        for user_id, user_name, count in AuditLogRepository.cancel_counts_by_user(
            ctx.tenant_id, start, end
        ):
            if count >= USER_CANCEL_THRESHOLD:
                alerts.append(
                    {
                        "type": "USER_CANCELLATIONS",
                        "severity": "medium",
                        "title": "Multiple cancellations by same user",
                        "message": f"{user_name} cancelled {count} bills today.",
                        "count": count,
                        "user_id": user_id,
                        "user_name": user_name,
                    }
                )

        reprint_count = AuditLogRepository.count_actions(
            ctx.tenant_id, "REPRINT_BILL", start, end
        )
        if reprint_count >= REPRINT_TODAY_THRESHOLD:
            alerts.append(
                {
                    "type": "FREQUENT_REPRINTS",
                    "severity": "low",
                    "title": "Frequent bill reprints",
                    "message": f"{reprint_count} reprint events recorded today.",
                    "count": reprint_count,
                }
            )

        price_changes = AuditLogRepository.count_actions(
            ctx.tenant_id, "UPDATE_PRICE", start, end
        )
        if price_changes > 0:
            alerts.append(
                {
                    "type": "PRICE_CHANGES",
                    "severity": "low",
                    "title": "Item price changes",
                    "message": f"{price_changes} price update(s) today.",
                    "count": price_changes,
                }
            )

        deactivated = AuditLogRepository.count_actions(
            ctx.tenant_id, "ITEM_DEACTIVATED", start, end
        )
        if deactivated > 0:
            alerts.append(
                {
                    "type": "DEACTIVATED_ITEMS",
                    "severity": "low",
                    "title": "Items deactivated",
                    "message": f"{deactivated} item(s) deactivated today.",
                    "count": deactivated,
                }
            )

        # Unusual discounts from today's CREATE_BILL audits
        create_logs = AuditLogRepository.recent_actions(
            ctx.tenant_id, ["CREATE_BILL"], start, end, limit=100
        )
        unusual = 0
        for log in create_logs:
            data = log.new_data or {}
            discount = float(data.get("discount") or 0)
            if discount >= HIGH_DISCOUNT_AMOUNT:
                unusual += 1
        if unusual > 0:
            alerts.append(
                {
                    "type": "UNUSUAL_DISCOUNTS",
                    "severity": "medium",
                    "title": "Unusual discount activity",
                    "message": f"{unusual} bill(s) today had discount ≥ ₹{int(HIGH_DISCOUNT_AMOUNT)}.",
                    "count": unusual,
                }
            )

        login_count = AuditLogRepository.count_actions(ctx.tenant_id, "LOGIN", start, end)
        alerts.append(
            {
                "type": "LOGIN_ACTIVITY",
                "severity": "info",
                "title": "Login activity",
                "message": f"{login_count} successful login(s) today.",
                "count": login_count,
            }
        )

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "period": "today",
            "alerts": alerts,
        }

    @staticmethod
    def serialize(row, *, brief: bool = True, user_role: str | None = None):
        bill_number = None
        if isinstance(row.new_data, dict):
            bill_number = row.new_data.get("bill_number")
        if not bill_number and isinstance(row.old_data, dict):
            bill_number = row.old_data.get("bill_number")
        if not bill_number and row.entity_type == "BILL" and row.entity_id:
            bill = BillRepository.get_by_id_and_tenant(row.entity_id, row.tenant_id)
            if bill:
                bill_number = bill.bill_number

        role_label = ROLE_LABELS.get(user_role or "", user_role or None)
        if user_role and not role_label:
            role_label = user_role.replace("_", " ").title()

        data = {
            "id": row.id,
            "user_id": row.user_id,
            "user_name": row.user_name,
            "user_role": user_role,
            "user_role_label": role_label,
            "action": row.action,
            "entity_type": row.entity_type,
            "entity_id": row.entity_id,
            "bill_number": bill_number,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
        if not brief:
            data.update(
                {
                    "old_data": row.old_data,
                    "new_data": row.new_data,
                    "ip_address": row.ip_address,
                    "user_agent": row.user_agent,
                }
            )
        return data
