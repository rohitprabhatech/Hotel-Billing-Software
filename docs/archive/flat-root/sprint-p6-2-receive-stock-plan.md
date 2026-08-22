# Sprint Plan — P6-2 Receive stock + low-stock ops polish

**Date:** 2026-08-16  
**Status:** Completed  
**Phase:** 6 — Inventory operations  
**Product:** Business Billing

---

## Goal

Give owners a clear **Receive stock** path (positive-only, including starting tracking) and polish low/out-of-stock navigation from dashboard and notifications.

## Scope

1. Movement source `RECEIVE` + schema/check update.
2. `POST /api/v1/items/:id/receive-stock` `{ quantity > 0, reason? }` — starts tracking if stock was null; else adds; audit + ledger.
3. FE: Receive Stock dialog on Items (tracked and untracked); Stock Movements filter includes RECEIVE.
4. Deep-links: dashboard stock alert + notification bell → Items with `stock_status=low|out`; Items reads URL param.
5. Tests + roadmap/docs.

## Non-goals

- Suppliers/PO, warehouses, SMS, SaaS checkout, bulk CSV import.

## Completion

See [`phase6-p6-2-receive-stock.md`](./phase6-p6-2-receive-stock.md).
