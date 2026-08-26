# Common Module — Notifications

Typed in-app events (low stock, subscription expiry, industry ops). Tenant-scoped. Delivered via NotificationBell.

## Template registry (BIZ-63)

Central keys live in `backend/app/constants/notification_templates.py`. Emitters call
`NotificationService.emit_template(key=..., tenant_id=..., entity_id=..., context=...)`
so title/message stay consistent and spam is rate-limited.

| Key | Type | Module | Industry | Anti-spam |
|-----|------|--------|----------|-----------|
| `low_stock` | LOW_STOCK | core_inventory | no | dedupe open |
| `out_of_stock` | OUT_OF_STOCK | core_inventory | no | dedupe open |
| `kot_ready` | KOT_READY | kot | yes | dedupe + 120s cooldown |
| `repair_ready` | REPAIR_READY | repair_service | yes | dedupe open |
| `batch_expiring` | BATCH_EXPIRING | batch_expiry | yes | dedupe open |
| `batch_expired` | BATCH_EXPIRED | batch_expiry | yes | dedupe open |
| `travel_payment_due` | TRAVEL_PAYMENT_DUE | travel_bookings | yes | 300s cooldown |
| `travel_booking_confirmed` | TRAVEL_BOOKING_CONFIRMED | travel_bookings | yes | dedupe open |
| `credit_due` | CREDIT_DUE | customer_credit | yes | 60s cooldown |
| `custom_order_ready` | CUSTOM_ORDER_READY | custom_orders | yes | dedupe open |
| `installation_scheduled` | INSTALLATION_SCHEDULED | installation | yes | dedupe open |

`dedupe_open`: skip while an unread alert of the same type+entity exists.  
`cooldown_seconds`: skip if any alert (read or unread) was created within the window.

## API

| Method | Path | Notes |
|--------|------|-------|
| GET | `/api/v1/notifications` | List (paginated); `unread_only` |
| GET | `/api/v1/notifications/unread-count` | Badge count |
| GET | `/api/v1/notifications/templates` | Module-filtered catalog; `industry_only=true` |
| PATCH | `/api/v1/notifications/{id}/read` | Mark one |
| PATCH | `/api/v1/notifications/read-all` | Mark all |

Catalog returns only templates whose module is enabled for the tenant (`core_*` always).

## Emitters (examples)

- KOT → ready: `kot_service` → `notify_kot_ready`
- Repair ready / install scheduled / custom order ready / travel confirm & due / credit: existing `notify_*` wrappers → `emit_template`
- Batch expiry scan: `batch_service._notify_expiring` → `batch_expiring` / `batch_expired`
