# Sprint BIZ-52 – Sales Orders and Purchase Orders

## Objective

SO/PO documents before billing/purchasing.

## Business Type

Wholesale Shops

## Status

**COMPLETED** (2026-08-26)

## What shipped

### Backend

- Tables: `sales_orders`, `sales_order_items`, `purchase_orders`, `purchase_order_items` (+ number counters)
- Migration: `20260826_biz52_sales_purchase_orders`
- `/api/v1/sales-orders` + convert → bill (`SO-#####`)
- `/api/v1/purchase-orders` + convert → purchase (`PO-#####`)
- Wholesale aliases under `/wholesale/sales-orders` and `/wholesale/purchase-orders`
- Status: DRAFT → CONFIRMED → CONVERTED / CANCELLED (v1 full convert only)

### Frontend

- `/owner/sales-orders` and `/owner/purchase-orders` (wholesale nav)

### Tests

- `backend/tests/test_biz52_sales_purchase_orders.py` (5 passed)

## Acceptance Criteria

- [x] SO→Bill
- [x] PO→Purchase

## Dependencies

BIZ-51, BIZ-06

## Next

BIZ-53 — wholesale multi-warehouse & stock transfer
