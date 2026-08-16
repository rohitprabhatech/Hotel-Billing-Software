# Sprint Plan — P6-1 Stock movement ledger + owner low-stock ops

**Date:** 2026-08-16  
**Status:** Completed  
**Phase:** 6 — Inventory operations  
**Product:** Business Billing

---

## Phase 6 goal

Turn existing stock enforcement into owner-ready inventory ops (movement history, low-stock visibility, receive/adjust) without full PO or multi-warehouse.

## P6-1 Scope

1. `stock_movements` table + dual-write from bill deduct, cancel restore, adjust-stock.
2. Owner API: list movements (item / tenant-wide filters).
3. Owner UI: Stock Movements page + Items stock status filter (Low / Out).
4. Tests + Phase 6 roadmap row.

## Non-goals

- SMS, SaaS checkout, suppliers/PO, warehouses.

## Completion

See [`phase6-p6-1-stock-movements.md`](./phase6-p6-1-stock-movements.md).
