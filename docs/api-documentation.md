# API Documentation — Business Billing

Base URL: **`/api/v1`**  
Auth: Bearer JWT (`Authorization: Authorization: Bearer <token>`).  
Envelope: `{ "success": true|false, "data": ..., "meta": ..., "error": ... }`.

Extended historical notes: [09-api-documentation.md](./09-api-documentation.md). Prefer this file for current product naming.

## Public

| Method | Path | Notes |
|--------|------|-------|
| GET | `/health` | Liveness |
| GET | `/health/ready` | DB readiness |
| GET | `/public/plans` | Active public subscription plans for landing pricing; ordered by `display_order` |
| GET | `/tenants/business-types` | Selectable business types |
| POST | `/auth/register-business` | Submit **PENDING** request (`register-hotel` = legacy alias). Does **not** create a tenant or JWT. Requires `terms_accepted: true`. |
| POST | `/auth/login` | Email + password (business user **or** Master Admin) |

## Master Admin (`MASTER_ADMIN` only)

JWT has `role=MASTER_ADMIN` and **no** `tenant_id`. Business Owner/Billing User tokens receive **403**.

| Method | Path | Notes |
|--------|------|-------|
| GET | `/master/dashboard/summary` | Live tenant counts + `pending_requests` + `trial_businesses` |
| GET | `/master/registration-requests` | List (`status`, `q`, `page`, `per_page`) |
| GET | `/master/registration-requests/:id` | Detail (never returns `password_hash`) |
| POST | `/master/registration-requests/:id/approve` | Creates ACTIVE tenant + verified OWNER; starts trial if enabled |
| POST | `/master/registration-requests/:id/reject` | Body `{ "reason": "..." }` (min 8 chars) |
| GET | `/master/settings/trial` | `trial_enabled`, `trial_days`, `expiry_warning_days` |
| PUT | `/master/settings/trial` | `{ "trial_enabled": true, "trial_days": 15, "expiry_warning_days": 5 }` |
| GET | `/master/trials` | Active (not-ended) TRIAL subscriptions |
| GET | `/master/plans` | Plan catalog (`include_inactive` default true); ordered by `display_order` |
| POST | `/master/plans` | Create plan (price ≥ 0, INR, MONTHLY\|YEARLY) |
| GET | `/master/plans/:id` | Plan detail + `subscriber_count` |
| PUT | `/master/plans/:id` | Partial update; does **not** rewrite `subscriptions.price_at_purchase` |
| PATCH | `/master/plans/:id/status` | `{ "is_active": true\|false }` — existing subscriptions stay |
| GET | `/master/businesses` | Tenants + current subscription (`status`, `q`, `page`) |
| GET | `/master/businesses/expiring` | Within `expiry_warning_days` |
| GET | `/master/businesses/:tenant_id` | Business + subscription |
| POST | `/master/businesses/:id/assign-plan` | `{ "plan_id", "days"? }` |
| POST | `/master/businesses/:id/extend-trial` | `{ "days" }` |
| POST | `/master/businesses/:id/renew` | Manual paid period; snapshots `price_at_purchase` |
| POST | `/master/businesses/:id/cancel-subscription` | Cancel entitlement (login still allowed) |
| GET | `/master/notifications` | Master Admin in-app alerts for expiring / expired businesses |
| GET | `/master/notifications/unread-count` | Unread Master alert count |
| PATCH | `/master/notifications/:id/read` | Mark one Master alert read |
| PATCH | `/master/notifications/read-all` | Mark all Master alerts read |
| POST | `/master/jobs/expiry-check` | Manual trigger for the idempotent expiry notice job |
| POST | `/auth/forgot-password` | Reset email |
| POST | `/auth/reset-password` | Token + new password |
| POST | `/auth/verify-email` | Email verification token |
| POST | `/auth/resend-verification` | Resend verification |

## Authenticated (business user or Master Admin)

| Method | Path | Notes |
|--------|------|-------|
| GET | `/auth/me` | Current user (`tenant` is `null` for Master Admin) |
| POST | `/auth/logout` | Bumps `token_version` |
| POST | `/auth/change-password` | Bumps `token_version` |
| GET/PUT | `/profile` | Profile |
| POST | `/profile/request-email-change` | Pending email + verify |

## Catalog & billing (OWNER + BILLING_USER)

| Area | Paths |
|------|--------|
| Categories | `GET/POST /categories`, `GET/PUT /categories/:id`, `PATCH /categories/:id/status` (write mostly OWNER) |
| Items | `GET/POST /items`, `GET/PUT /items/:id`, `PATCH /items/:id/status` (DELETE → 405; soft deactivate only) |
| Bills | `POST/GET /bills`, `GET /bills/today-summary`, `GET /bills/:id`, `GET /bills/:id/pdf`, `POST /bills/:id/cancel`, `POST /bills/:id/print`, `POST /bills/:id/send-whatsapp` |
| Items | `GET/POST /items`, `GET/PUT /items/:id`, `PATCH /items/:id/status`, `POST /items/:id/adjust-stock`, `POST /items/:id/receive-stock` |
| Stock movements | `GET /stock-movements` (owner) |
| Tenant WhatsApp | `GET /tenants/me/whatsapp` (status, no token), `PUT /tenants/me/whatsapp` (OWNER), `POST .../test`, `POST .../disconnect` |
| WhatsApp webhook (public) | `GET/POST /webhooks/whatsapp` — Meta verify + signed status callbacks (`DELIVERED`/`READ`/`FAILED`) |

Bill payload uses **`reference`** (legacy alias `table_number`). Payment: **`cash`** \| **`online`**.

## Owner-only

| Area | Paths |
|------|--------|
| Tenant | `GET/PUT /tenants/me` |
| Users | `GET/POST /users`, `GET/PUT /users/:id`, `PATCH /users/:id/password` |
| Reports | `/reports/summary`, `/daily-sales`, `/weekly-sales`, `/monthly-sales`, `/custom-sales`, `/export` |

## Notification behavior

- Tenant `/notifications` now includes `SUBSCRIPTION_EXPIRING` and `SUBSCRIPTION_EXPIRED`.
- Owner clicking a subscription notice opens Owner Settings at `#subscription`.
- Master notification bell opens `/master/businesses`.
| AI | `GET /ai/analysis`, `GET /ai/decisions` |
| Audit | `GET /audit-logs`, `/audit-logs/alerts`, `/audit-logs/:id` |

## Multi-tenant rule

Authorization uses the **JWT tenant**, never a client-supplied `tenant_id` for scoping.

## Registration body (conceptual)

```json
{
  "business_name": "Sunrise Retail",
  "business_type": "retail_shop",
  "owner_name": "Asha",
  "owner_email": "asha@example.com",
  "password": "SecurePass1",
  "confirm_password": "SecurePass1",
  "mobile": "98xxxxxxxx",
  "gst_number": "",
  "fssai_number": "",
  "terms_accepted": true
}
```

Register submits a **PENDING** `registration_requests` row. Tenant + OWNER are created only after Master Admin **approve**. Existing seed/live tenants stay ACTIVE (grandfathered). Email verification is for profile email-change, not signup.
