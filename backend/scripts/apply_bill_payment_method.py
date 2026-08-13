"""Add bills.payment_method if missing."""

from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import inspect, text

from app import create_app
from app.extensions import db


def main():
    app = create_app()
    with app.app_context():
        cols = {c["name"] for c in inspect(db.engine).get_columns("bills")}
        if "payment_method" in cols:
            print("bills.payment_method already present")
            return
        print("Adding bills.payment_method...")
        dialect = db.engine.dialect.name
        if dialect == "sqlite":
            db.session.execute(
                text(
                    "ALTER TABLE bills "
                    "ADD COLUMN payment_method VARCHAR(20) NOT NULL DEFAULT 'cash'"
                )
            )
        else:
            db.session.execute(
                text(
                    "ALTER TABLE bills "
                    "ADD COLUMN payment_method VARCHAR(20) NOT NULL DEFAULT 'cash' "
                    "AFTER status, "
                    "ADD INDEX ix_bills_tenant_payment_method (tenant_id, payment_method)"
                )
            )
        db.session.commit()
        print("Done.")


if __name__ == "__main__":
    main()
