"""Run subscription expiry notices (CLI / Task Scheduler / cron).

Does not depend on a user opening the app. Safe to run daily; notices are
idempotent per subscription period.

  python scripts/check_subscription_expiry.py

Windows Task Scheduler example (daily 06:00):
  Program:  C:\\...\\backend\\.venv\\Scripts\\python.exe
  Arguments: scripts\\check_subscription_expiry.py
  Start in:  C:\\...\\backend
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

sys.path.insert(0, str(ROOT))

from app import create_app  # noqa: E402
from app.services.expiry_job_service import ExpiryJobService  # noqa: E402


def main() -> int:
    app = create_app()
    with app.app_context():
        result = ExpiryJobService.run()
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
