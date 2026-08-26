# Sprint BIZ-49 – Furniture Delivery and Installation Tracking

## Objective

Delivery management + installation tracking for furniture orders.

## Business Type

Furniture Shops

## Status

**COMPLETED** (2026-08-26)

## What shipped

### Backend

- `delivery_jobs` + `delivery_number_counters` (DL-#####)
- `/api/v1/deliveries` CRUD + PATCH status (`delivery_tracking` module)
- `/api/v1/furniture/deliveries` aliases
- Furniture orders cannot be marked DELIVERED directly when `delivery_tracking` is on — use delivery board
- `installation_orders.custom_order_id` — schedule install from ready furniture custom order
- `/api/v1/furniture/installations` alias
- Notifications: `DELIVERY_OUT_FOR_DELIVERY`, `DELIVERY_COMPLETED`

### Frontend

- Owner **Deliveries** board at `/owner/deliveries` (Scheduled → Out for delivery → Delivered)
- Furniture Orders: no direct “Mark delivered” when delivery module on
- Installations: furniture mode picks ready custom orders instead of serial units

### Database

- Alembic: `20260826_biz49_furniture_delivery_tracking`

### Tests

- `backend/tests/test_biz49_furniture_delivery_installation.py` (5 passed)

## Acceptance Criteria

- [x] Delivery statuses on dedicated jobs
- [x] Delivery board live (API + UI)
- [x] Out for delivery / delivered notifications
- [x] Reuse installation for furniture custom orders

## Dependencies

BIZ-48, BIZ-33

## Next

BIZ-50 — furniture quotations + Phase 09 testing gate
