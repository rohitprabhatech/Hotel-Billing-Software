# Travel Agencies — Testing

## Automated (BIZ-56)

Suite: `backend/tests/test_biz56_tour_packages.py` (5 passed, 2026-08-26)

| Test | Covers |
|------|--------|
| `test_restaurant_tour_packages_forbidden` | 403 without module |
| `test_travel_module_has_tour_packages` | module matrix |
| `test_create_package_and_bill_without_stock` | untracked item + bill; stock stays null |
| `test_billing_cannot_create_package_can_bill` | permissions |
| `test_package_cross_tenant_isolation` | 404 |

## Automated (BIZ-57)

Suite: `backend/tests/test_biz57_travel_bookings.py` (4 passed, 2026-08-26)

| Test | Covers |
|------|--------|
| `test_restaurant_bookings_forbidden` | 403 |
| `test_booking_advance_remaining_and_complete` | TB-#####, payments, status, notifications |
| `test_cannot_complete_with_outstanding_balance` | status rule |
| `test_booking_cross_tenant_isolation` | 404 |

## Automated (BIZ-58)

Suite: `backend/tests/test_biz58_travel_itinerary_documents.py` (3 passed, 2026-08-26)

| Test | Covers |
|------|--------|
| `test_itinerary_and_documents_crud` | hotel/vehicle/ticket CRUD + docs + counts + billing write denied |
| `test_detail_cross_tenant_isolation` | nested 404 |
| `test_restaurant_travel_details_forbidden` | module gate |

## Automated (BIZ-59)

Suite: `backend/tests/test_biz59_travel_agent_commission.py` (4 passed, 2026-08-26)

| Test | Covers |
|------|--------|
| `test_commission_math_helper` | percent × total rounding |
| `test_agent_booking_commission_and_report` | CRUD, auto-accrue, report, mark paid, override % |
| `test_commission_cross_tenant_isolation` | 404 / empty report |
| `test_restaurant_commission_forbidden` | module gate |

## Automated (BIZ-60 gate)

Suite: Phase 11 matrix BIZ-56…60 — **23 passed** (2026-08-26)

Gate file: `backend/tests/test_biz60_travel_agency_testing_gate.py` (7)

Docs: [`../../14-sprints/biz-60-travel-agency-gate-report.md`](../../14-sprints/biz-60-travel-agency-gate-report.md),
[`../../14-sprints/biz-60-manual-frontend-checklist.md`](../../14-sprints/biz-60-manual-frontend-checklist.md)

## Manual smoke

| Test ID | Purpose | Expected | Priority |
|---------|---------|----------|----------|
| TEST-TRVL-001 | Create package | Saved; appears on cards | P0 |
| TEST-TRVL-002 | Booking + advance | Balance due | P0 |
| TEST-TRVL-003 | Complete booking | Status COMPLETED after full pay | P0 |
| TEST-TRVL-005 | Service invoice / Create bill | Bill created; no stock move | P0 |
| TEST-TRVL-006 | Booking Details itinerary | Hotel/vehicle/ticket lines save | P0 |
| TEST-TRVL-007 | Document metadata | Passport/visa/ID rows; delete audited | P0 |
| TEST-TRVL-008 | Agent + commission | Report totals match booking × % | P0 |
| TEST-TRVL-009 | Cross-tenant document | Other tenant 404 on docs | P0 |

Do not run destructive tests on production data.
