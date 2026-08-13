"""Health and readiness checks."""

from sqlalchemy import text

from app.extensions import db
from app.utils.responses import error_response, success_response


def get_health():
    return success_response(
        data={
            "status": "ok",
            "service": "hotel-billing-api",
            "version": "v1",
        }
    )


def get_readiness():
    try:
        db.session.execute(text("SELECT 1"))
        return success_response(
            data={
                "status": "ready",
                "database": "ok",
            }
        )
    except Exception:
        return error_response(
            message="Database is not ready",
            code="SERVICE_UNAVAILABLE",
            status_code=503,
            details={"database": "unavailable"},
        )