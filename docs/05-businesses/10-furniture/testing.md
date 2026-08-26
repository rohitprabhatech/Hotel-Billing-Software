# Furniture Shops — Testing

## Automated (BIZ-47)

Suite: `backend/tests/test_biz47_furniture_product_attributes.py` (5 passed, 2026-08-26)

## Automated (BIZ-48)

Suite: `backend/tests/test_biz48_furniture_custom_orders.py` (5 passed, 2026-08-26)

| Test | Covers |
|------|--------|
| `test_restaurant_custom_orders_forbidden` | 403 without module |
| `test_create_furniture_order_advance_less_than_total` | alias create, remaining, bakery filter |
| `test_furniture_status_pipeline_and_billing_cannot_manage` | status + permissions |
| `test_furniture_record_additional_advance` | advance caps |
| `test_furniture_order_cross_tenant_isolation` | 404 |

## Automated (BIZ-49)

Suite: `backend/tests/test_biz49_furniture_delivery_installation.py` (5 passed, 2026-08-26)

| Test | Covers |
|------|--------|
| `test_delivery_module_forbidden_for_restaurant` | module gate |
| `test_furniture_cannot_mark_delivered_directly` | 400 guard |
| `test_delivery_lifecycle_and_notifications` | DL-##### pipeline + order DELIVERED + notifications |
| `test_installation_from_furniture_custom_order` | custom_order_id install path |
| `test_delivery_cross_tenant_isolation` | 404 |

## Automated (BIZ-50)

Suite: `backend/tests/test_biz50_furniture_quotations.py` (3 passed, 2026-08-26)

## Automated (Phase 09 gate — BIZ-50)

Combined gate in `test_biz50_furniture_testing_gate.py`. Full Phase 09 — **28 passed** (2026-08-26). See [biz-50-furniture-gate-report.md](../../14-sprints/biz-50-furniture-gate-report.md).

## Manual smoke

| Test ID | Purpose | Expected | Priority |
|---------|---------|----------|----------|
| TEST-FURN-001 | Create item with dims/material/color | Saved and shown | P0 |
| TEST-FURN-010 | Book furniture order with advance | CO-#####; remaining due | P0 |
| TEST-FURN-011 | Status board pipeline | Owner/Manager only | P0 |
| TEST-FURN-012 | Record extra advance | Remaining updates | P0 |
| TEST-FURN-020 | Schedule delivery from ready order | DL-##### on board | P0 |
| TEST-FURN-021 | Out for delivery → delivered | Order DELIVERED; notifications | P0 |
| TEST-FURN-022 | Schedule installation from ready order | INS-##### linked to order | P1 |
| TEST-FURN-030 | Create quotation; convert to bill | QT-#####; stock decreases | P0 |

Do not run destructive tests on production data.
