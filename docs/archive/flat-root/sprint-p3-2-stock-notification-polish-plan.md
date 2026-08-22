# Sprint Plan — P3-2 Stock/notification polish + crash isolation

**Date:** 2026-08-14  
**Status:** Completed  
**Product:** Business Billing

---

## Scope

1. **Route ErrorBoundary** on Owner + Billing shells — page crash shows recovery UI, not blank app.
2. **Restock recovery** — when stock rises above thresholds, mark open `LOW_STOCK` / `OUT_OF_STOCK` as read (item update + bill cancel restore).
3. **New Bill** — refresh catalog stock after successful bill.
4. **Owner dashboard** — unread stock alert strip with link to Items.
5. Tests + roadmap Phase 3 note + completion report.

## Non-goals

- Payment gateway, rebuild, new notification types, email/SMS push.
