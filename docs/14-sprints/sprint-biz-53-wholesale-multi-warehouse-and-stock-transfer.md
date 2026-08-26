# Sprint BIZ-53 – Wholesale Multi-Warehouse and Stock Transfer

## Objective

Enable warehouse module fully for wholesale.

## Business Type

Wholesale Shops

## Status

**COMPLETED** (2026-08-26)

## What shipped

### Backend

- Wholesale already has `warehouse` in module matrix (BIZ-38 reuse)
- Transfer pre-validates all source balances before any mutation
- Per-warehouse LOW_STOCK / OUT_OF_STOCK notifications (`entity_type=WAREHOUSE_STOCK`)
- Aliases: `/wholesale/warehouses`, `/wholesale/warehouses/stocks`, `/wholesale/stock-transfers`
- Bills continue to accept `warehouse_id` when module on

### Frontend

- Sell-from warehouse picker on Grocery/Barcode POS and New Bill
- Warehouses page: balances filter by location; transfer lines show qty available at **from** warehouse

### Tests

- `backend/tests/test_biz53_wholesale_warehouse.py` (5 passed)

## Acceptance Criteria

- [x] Sell from selected warehouse
- [x] Wholesale warehouse E2E (transfer + bill + low-stock notify)

## Dependencies

BIZ-38, BIZ-52

## Next

BIZ-54 — wholesale outstanding, challan, and GST invoice
