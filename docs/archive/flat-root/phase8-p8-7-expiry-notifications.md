# Sprint P8-7 Completion Report — Notifications, email, scheduled expiry checks

**Date:** 2026-08-18  
**Status:** **COMPLETED**  
**Phase:** 8  
**Product:** Business Billing

---

## SPRINT STATUS

**Completed.** Subscription warnings and expiry alerts now work without waiting for a tenant to open the app. The system records one notice per subscription period, sends Owner email alerts, creates tenant in-app notifications, and shows the same events to Master Admin through a separate notification bell.

## Database changes

| Change | Notes |
|--------|--------|
| `subscription_notices` | Idempotency log keyed by `subscription_id + notice_type + period_key` |
| `platform_notifications` | Master Admin in-app alerts with no `tenant_id` |
| `scripts/apply_expiry_notifications.py` | Idempotent schema helper for existing MySQL databases |
| `scripts/check_subscription_expiry.py` | CLI entrypoint for Task Scheduler / cron |

`02_schema.sql` includes both new tables for fresh installs. `apply_pending_schema.py` now runs the P8-7 helper after P8-6.

## API changes

| Method | Path | Auth |
|--------|------|------|
| GET | `/api/v1/master/notifications` | Master Admin only |
| GET | `/api/v1/master/notifications/unread-count` | Master Admin only |
| PATCH | `/api/v1/master/notifications/:id/read` | Master Admin only |
| PATCH | `/api/v1/master/notifications/read-all` | Master Admin only |
| POST | `/api/v1/master/jobs/expiry-check` | Master Admin only; manual job trigger |
| PUT | `/api/v1/master/settings/trial` | Accepts `expiry_warning_days` in addition to trial settings |

Tenant `/notifications` now includes:

- `SUBSCRIPTION_EXPIRING`
- `SUBSCRIPTION_EXPIRED`

Owner clicking a subscription notice opens Owner Settings at `#subscription`.  
Master clicking a platform notice opens `/master/businesses`.

## Backend changes

| Area | Change |
|------|--------|
| `ExpiryJobService` | Refreshes subscription statuses, deduplicates by period, creates notices, sends emails |
| `EmailService` | Added expiring and expired subscription email methods |
| `PlatformSettingsService` | `expiry_warning_days` is now editable and validated (1–30) |
| `UserRepository` | Added active-owner lookup for email recipients |
| `NotificationService` | Added subscription notification types |

The production path is **CLI + scheduler**, not an in-process always-on job:

- Windows Task Scheduler → `backend\.venv\Scripts\python.exe scripts\check_subscription_expiry.py`
- Cron → same script on Linux

This avoids duplicate runs across multiple app workers.

## Frontend changes

| Path / component | Change |
|------------------|--------|
| `MasterLayout` | Master notification bell |
| `MasterTrialSettingsPage` | Editable expiry warning days |
| `NotificationBell` | Subscription notices route Owners to the subscription section |

## Tests

- `backend/tests/test_p8_7_expiry_notifications.py`
- `frontend` production build passes
- Full backend regression was started after the targeted P8-7 tests passed

## Known issues / residuals

- Public landing pricing is still hardcoded until P8-8.
- No payment gateway checkout; renewal remains operator-recorded.

---

**Stopped.** Should I start the next sprint? (P8-8 Dynamic landing page pricing)
