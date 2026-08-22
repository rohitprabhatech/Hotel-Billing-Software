# Sprint P6-1 Completion Report — Stock movement ledger + owner low-stock ops

**Date:** 2026-08-16  
**Status:** **COMPLETED**  
**Phase:** 6 — Inventory operations

---

## Implementation

- Schema: `stock_movements` (delta, quantity_after, source `BILL|CANCEL|ADJUST|ITEM_UPDATE`, reason, bill reference, actor)
- Apply helper: `scripts/apply_stock_movements.py` (included in `apply_pending_schema.py`); also in `sql/02_schema.sql`
- Dual-write from bill deduct, cancel restore, adjust-stock, and item stock update
- Owner API: `GET /api/v1/stock-movements` (item / source filters, pagination)
- Items list: `stock_status=low|out|tracked`
- FE: Owner **Stock Movements** page + Items stock filter + per-item link

## Ops

```text
python scripts/apply_pending_schema.py
```

## Testing

```text
.\.venv\Scripts\python -m pytest tests\test_p6_1_stock_movements.py -q
→ 3 passed

npm run build → OK
```

## Documentation

- Plan: `docs/sprint-p6-1-stock-movements-plan.md`
- This report; roadmap Phase 6 IN PROGRESS with P6-1 completed

## Non-goals (deferred)

- SMS, suppliers/PO, warehouses, SaaS checkout

---

**Stopped.** Should I start the next sprint (P6-2)?
