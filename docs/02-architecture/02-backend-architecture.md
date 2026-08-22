# Backend Architecture

**Stack:** Flask · SQLAlchemy · MySQL/MariaDB · JWT

Retain: `controllers/ services/ repositories/ models/ routes/ middleware/`

Target extension: `app/core/` (billing/inventory/tax) + `app/modules/{industry}/`

No business logic in routes. Migrations only after approved sprints + backup.
