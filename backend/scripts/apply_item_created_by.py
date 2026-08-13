"""Add items.created_by if missing."""

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
        cols = {c["name"] for c in inspect(db.engine).get_columns("items")}
        if "created_by" in cols:
            print("items.created_by already present")
            return
        print("Adding items.created_by...")
        db.session.execute(
            text(
                "ALTER TABLE items "
                "ADD COLUMN created_by CHAR(36) NULL AFTER category_id, "
                "ADD INDEX ix_items_created_by (created_by), "
                "ADD CONSTRAINT fk_items_created_by "
                "FOREIGN KEY (created_by) REFERENCES users (id) "
                "ON DELETE SET NULL ON UPDATE CASCADE"
            )
        )
        db.session.commit()
        print("Done.")


if __name__ == "__main__":
    main()
