# Sprint P3-2 Completion Report — Stock/notification polish + crash isolation

**Date:** 2026-08-14  
**Status:** **COMPLETED**

---

## Delivered

### Route ErrorBoundary
- `RouteErrorBoundary` wraps Owner + Billing page outlets (`key=pathname` resets on navigation).
- Page render crash shows recovery UI + Try again; shell/nav remain usable (no full blank app).

### Restock clears open stock alerts
- When stock recovers (`> 0` clears `OUT_OF_STOCK`; `> minimum` or no minimum clears `LOW_STOCK`), unread alerts for that item are marked read.
- Triggered on item stock update and on bill cancel stock restore (via `notify_stock_transition`).

### New Bill catalog refresh
- After a successful bill, catalog reload so displayed stock matches deduction.

### Owner dashboard stock strip
- Unread `LOW_STOCK` / `OUT_OF_STOCK` summary alert with link to Items.

---

## Testing

```text
.\.venv\Scripts\python.exe -m pytest tests/test_p3_2_stock_alert_recovery.py tests/test_p3_1_stock_notifications.py -q
→ 9 passed

npm run build → OK
```

---

## Known limitations
- Concurrent double-submit oversell still depends on DB row locks (MySQL `FOR UPDATE`); SQLite test env does not fully prove races.
- ErrorBoundary covers route subtree only, not AppBar/drawer itself.

---

## Next
Ask before starting the next sprint. Candidate themes: email/SMS notifications, inventory adjustments UI, concurrent stock stress on MySQL, or other Phase 3 priorities you choose.
