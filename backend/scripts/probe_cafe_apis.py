"""Probe cafe APIs against configured DATABASE_URL (development).

Usage:
  set CAFE_PROBE_EMAIL=you@example.com
  set CAFE_PROBE_PASSWORD=secret
  python scripts/probe_cafe_apis.py
"""

import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app import create_app
from tests.conftest import login


def main():
    email = os.getenv("CAFE_PROBE_EMAIL", "owner@hotelb.com")
    password = os.getenv("CAFE_PROBE_PASSWORD", "Owner@12345")
    app = create_app("development")
    with app.app_context():
        client = app.test_client()
        headers = login(client, email, password)
        paths = [
            "/api/v1/bills/today-summary",
            "/api/v1/cafe/pos-catalog",
            "/api/v1/cafe/dashboard?period=last_7_days",
            "/api/v1/menu/addons",
            "/api/v1/combos",
            "/api/v1/coupons",
            "/api/v1/reports/summary?period=today",
            "/api/v1/tenants/me/modules",
        ]
        for path in paths:
            response = client.get(path, headers=headers)
            body = response.get_json() or {}
            err = body.get("error") or {}
            print(
                response.status_code,
                path,
                err.get("code") or "OK",
                (err.get("message") or "")[:120],
            )


if __name__ == "__main__":
    main()
