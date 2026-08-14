# Sprint P3-1 Completion Report — AI fix + Stock + Notifications

**Date:** 2026-08-14  
**Status:** **COMPLETED**

---

## AI ISSUE

**Root cause:** `AiAssistantPage` rendered `<Card>` / `<CardContent>` without importing them → crash after Analyze → blank page.

**Fix:** Import Card/CardContent; add loading / error+Retry / empty / success states so the page never goes blank.

---

## STOCK ISSUE

**Root cause:** `stock_quantity` was catalog-only; bill create never validated or deducted stock.

**Fix:**
- Backend locks items (`FOR UPDATE`), validates **all** lines, then deducts in the same transaction as bill create.
- Reject with `error.code = INSUFFICIENT_STOCK` and message like `Insufficient stock. Available: 5, requested: 6.`
- NULL stock = untracked (no check/deduct).
- Cancel restores stock for tracked items + `STOCK_RESTORED` audit.
- FE New Bill shows available stock, blocks oversell, disables Generate when invalid.

**Threshold rule:** Low-stock when `stock_quantity <= minimum_stock_level` (both set).

---

## NOTIFICATION FEATURE

Implemented tenant-scoped `notifications` table + APIs + bell UI (Owner + Billing layouts).

Types: `LOW_STOCK`, `OUT_OF_STOCK`, `INSUFFICIENT_STOCK_ATTEMPT`  
Duplicate control: no second unread `LOW_STOCK`/`OUT_OF_STOCK` for the same item while one remains unread.

---

## DATABASE

- `items.minimum_stock_level` (nullable)
- Table `notifications`
- Migration: `20260814_stock_notifications.py`
- Apply script: `scripts/apply_stock_notifications.py` (wired into `apply_pending_schema.py`)
- `sql/02_schema.sql` updated

**Ops:** run `python scripts/apply_pending_schema.py` on existing MySQL DBs.

---

## API

| Endpoint | Notes |
|----------|--------|
| `GET /api/v1/notifications` | List + meta unread_count |
| `GET /api/v1/notifications/unread-count` | Badge |
| `PATCH /api/v1/notifications/:id/read` | Mark one |
| `PATCH /api/v1/notifications/read-all` | Mark all |
| `POST /api/v1/bills` | Stock validate/deduct; may return `INSUFFICIENT_STOCK` |
| Items create/update | `minimum_stock_level` |

---

## FRONTEND

- AI Assistant states fixed
- Notification bell on Owner + Billing shells
- New Bill stock UX
- Items form: minimum stock level

---

## TESTING

```text
pytest tests/test_p3_1_stock_notifications.py tests/test_billing.py tests/test_ai_assistant.py -q
→ 22 passed
npm run build → OK
```

---

## FILES MODIFIED / CREATED

**Created:** notification model/repo/service/routes/controller; apply script; migration; `NotificationBell.jsx`; `notificationService.js`; `test_p3_1_stock_notifications.py`; this report; plan doc (earlier).

**Modified:** `AiAssistantPage.jsx`, `bill_service.py`, `item_*`, `exceptions.py`, layouts, `NewBillPage.jsx`, `ItemsPage.jsx`, `02_schema.sql`, `apply_pending_schema.py`, `models/__init__.py`, `routes/__init__.py`, test guide.

---

## KNOWN ISSUES / NOTES

1. Concurrent oversell is protected via row locks on MySQL; SQLite tests do not fully prove DB-level race (lock is no-op).
2. `INSUFFICIENT_STOCK_ATTEMPT` commits a notification before returning 400 (intentional so the attempt is visible).
3. Untracked items (`stock_quantity` null) still sell freely by design.

---

**Should I start the next sprint?**
