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
| GET | `/tenants/business-types` | Selectable business types |
| POST | `/auth/register-business` | Create tenant + OWNER (`register-hotel` = legacy alias) |
| POST | `/auth/login` | Email + password |
| POST | `/auth/forgot-password` | Reset email |
| POST | `/auth/reset-password` | Token + new password |
| POST | `/auth/verify-email` | Email verification token |
| POST | `/auth/resend-verification` | Resend verification |

## Authenticated (any role)

| Method | Path | Notes |
|--------|------|-------|
| GET | `/auth/me` | Current user |
| POST | `/auth/logout` | Client discards token |
| POST | `/auth/change-password` | Bumps `token_version` |
| GET/PUT | `/profile` | Profile |
| POST | `/profile/request-email-change` | Pending email + verify |

## Catalog & billing (OWNER + BILLING_USER)

| Area | Paths |
|------|--------|
| Categories | `GET/POST /categories`, `GET/PUT /categories/:id`, `PATCH /categories/:id/status` (write mostly OWNER) |
| Items | `GET/POST /items`, `GET/PUT /items/:id`, `PATCH /items/:id/status` (DELETE → 405; soft deactivate only) |
| Bills | `POST/GET /bills`, `GET /bills/today-summary`, `GET /bills/:id`, `GET /bills/:id/pdf`, `POST /bills/:id/cancel`, `POST /bills/:id/print`, `POST /bills/:id/send-whatsapp` |
| Items | `GET/POST /items`, `GET/PUT /items/:id`, `PATCH /items/:id/status`, `POST /items/:id/adjust-stock` |
| Tenant WhatsApp | `GET /tenants/me/whatsapp` (status, no token), `PUT /tenants/me/whatsapp` (OWNER), `POST .../test`, `POST .../disconnect` |
| WhatsApp webhook (public) | `GET/POST /webhooks/whatsapp` — Meta verify + signed status callbacks (`DELIVERED`/`READ`/`FAILED`) |

Bill payload uses **`reference`** (legacy alias `table_number`). Payment: **`cash`** \| **`online`**.

## Owner-only

| Area | Paths |
|------|--------|
| Tenant | `GET/PUT /tenants/me` |
| Users | `GET/POST /users`, `GET/PUT /users/:id`, `PATCH /users/:id/password` |
| Reports | `/reports/summary`, `/daily-sales`, `/weekly-sales`, `/monthly-sales`, `/custom-sales`, `/export` |
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
  "fssai_number": ""
}
```

Legacy field `hotel_name` may still be accepted by the API as an alias for business name.
