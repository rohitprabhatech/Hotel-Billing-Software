"""Coupon repository (Sprint 5)."""

from app.extensions import db
from app.models.coupon import Coupon, CouponRedemption


class CouponRepository:
    @staticmethod
    def list_by_tenant(tenant_id: str, *, active_only=False) -> list[Coupon]:
        query = db.session.query(Coupon).filter(Coupon.tenant_id == tenant_id)
        if active_only:
            query = query.filter(Coupon.is_active.is_(True))
        return query.order_by(Coupon.code.asc()).all()

    @staticmethod
    def get_by_id(tenant_id: str, coupon_id: str) -> Coupon | None:
        return (
            db.session.query(Coupon)
            .filter(Coupon.tenant_id == tenant_id, Coupon.id == coupon_id)
            .first()
        )

    @staticmethod
    def get_by_code(tenant_id: str, code: str) -> Coupon | None:
        return (
            db.session.query(Coupon)
            .filter(Coupon.tenant_id == tenant_id, Coupon.code == code)
            .first()
        )

    @staticmethod
    def add(coupon: Coupon) -> Coupon:
        db.session.add(coupon)
        return coupon

    @staticmethod
    def add_redemption(row: CouponRedemption) -> CouponRedemption:
        db.session.add(row)
        return row
