# Sprint BIZ-51 – Wholesale Pricing Matrices

## Objective

Wholesale vs retail vs customer-wise pricing.

## Business Type

Wholesale Shops

## Status

**COMPLETED** (2026-08-26)

## What shipped

### Backend

- Tables: `price_lists`, `price_list_items`, `customer_price_lists`
- Migration: `20260826_biz51_wholesale_price_lists`
- `/api/v1/price-lists` CRUD, item matrix replace, customer assignments
- `/api/v1/wholesale/price-lists` aliases
- **Resolution order:** customer list → default wholesale list → bulk qty tiers → catalog retail
- Bill creation + grocery POS catalog use resolver (`customer_id` query on catalog)

### Frontend

- **Price Lists** admin at `/owner/price-lists` (wholesale tenants)
- Grocery/barcode POS applies list prices when customer selected

### Tests

- `backend/tests/test_biz51_wholesale_price_lists.py` (7 passed)

## Acceptance Criteria

- [x] Customer-specific price applies

## Dependencies

BIZ-10, BIZ-21, BIZ-04

## Next

BIZ-52 — sales orders & purchase orders
