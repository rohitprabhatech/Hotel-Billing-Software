# 09 — API Documentation

## Base URL

```text
/api/v1
```

## Conventions

### Headers

```http
Authorization: Bearer <jwt>
Content-Type: application/json
```

### Success Envelope

```json
{
  "success": true,
  "data": {},
  "meta": { "page": 1, "per_page": 20, "total": 100 },
  "error": null
}
```

### Error Envelope

```json
{
  "success": false,
  "data": null,
  "meta": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human readable message",
    "details": {}
  }
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 400 | Validation / business rule |
| 401 | Unauthenticated |
| 403 | Forbidden (role) |
| 404 | Not found in tenant scope |
| 409 | Conflict (e.g., duplicate) |
| 429 | Rate limited |
| 500 | Unexpected (safe message only) |

**Note:** `tenant_id` is never accepted from clients for authorization. Optional filters never override JWT tenant.

---

## Auth — `/api/v1/auth`

### POST `/auth/login`

Body:

```json
{
  "email": "owner@hotela.com",
  "password": "********"
}
```

Response data:

```json
{
  "access_token": "<jwt>",
  "token_type": "Bearer",
  "expires_in": 86400,
  "user": {
    "id": "...",
    "name": "Owner Name",
    "email": "owner@hotela.com",
    "role": "OWNER",
    "tenant": {
      "id": "...",
      "business_name": "Hotel A"
    }
  }
}
```

Audit: `LOGIN`

### POST `/auth/logout`

Requires JWT. Audit: `LOGOUT`. (Stateless JWT: client discards token; optional blocklist later.)

### GET `/auth/me`

Returns current user + role + tenant summary.

---

## Tenants — `/api/v1/tenants`

### GET `/tenants/me`

OWNER (and optionally BILLING_USER read-only subset for display).

### PUT `/tenants/me`

OWNER only. Update business profile fields used on receipts.

---

## Users — `/api/v1/users`

OWNER only.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/users` | List users in tenant |
| POST | `/users` | Create BILLING_USER |
| GET | `/users/{id}` | Get user |
| PUT | `/users/{id}` | Update name/email/active |
| PATCH | `/users/{id}/password` | Reset password |

Cannot create second OWNER via public API unless explicitly allowed later.

---

## Categories — `/api/v1/categories`

| Method | Path | Roles | Description |
|--------|------|-------|-------------|
| GET | `/categories` | OWNER, BILLING_USER | List (billing: active only) |
| POST | `/categories` | OWNER | Create |
| GET | `/categories/{id}` | OWNER, BILLING_USER | Get |
| PUT | `/categories/{id}` | OWNER | Update |
| PATCH | `/categories/{id}/status` | OWNER | Activate/deactivate |

---

## Items — `/api/v1/items`

| Method | Path | Roles | Description |
|--------|------|-------|-------------|
| GET | `/items` | Both | List/search/filter |
| POST | `/items` | OWNER | Create |
| GET | `/items/{id}` | Both | Get |
| PUT | `/items/{id}` | OWNER | Update (price/GST audited) |
| PATCH | `/items/{id}/status` | OWNER | Activate/deactivate |

Query params: `q`, `category_id`, `is_active`, `page`, `per_page`

Audit: `CREATE_ITEM`, `UPDATE_ITEM`, `UPDATE_PRICE`, `CHANGE_GST`, `DEACTIVATE_ITEM`

---

## Bills — `/api/v1/bills`

| Method | Path | Roles | Description |
|--------|------|-------|-------------|
| POST | `/bills` | Both | Create & finalize bill (or create draft if supported) |
| GET | `/bills` | Both | List (role-scoped filters) |
| GET | `/bills/{id}` | Both | Detail with items + tenant receipt header |
| POST | `/bills/{id}/cancel` | Both | Cancel with reason |
| POST | `/bills/{id}/print` | Both | Record PRINT/REPRINT audit; return print payload |

### POST `/bills` Body

```json
{
  "table_number": "41",
  "discount": 50.00,
  "items": [
    { "item_id": "...", "quantity": 1 },
    { "item_id": "...", "quantity": 2 }
  ]
}
```

Server loads current item prices/GST, recalculates all totals, assigns bill number, writes snapshots, audits `CREATE_BILL`.

Client-sent `subtotal`/`grand_total` ignored or validated and rejected if present and mismatched.

### POST `/bills/{id}/cancel` Body

```json
{
  "reason": "Customer order cancelled"
}
```

Audit: `CANCEL_BILL` with old/new status and amounts.

---

## Reports — `/api/v1/reports` (OWNER only)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/reports/daily-sales` | `?date=YYYY-MM-DD` (default today) |
| GET | `/reports/monthly-sales` | `?year=&month=` |
| GET | `/reports/custom-sales` | `?from=&to=` |
| GET | `/reports/summary` | Dashboard cards + comparisons |
| GET | `/reports/export` | `?type=daily\|monthly\|custom&format=xlsx\|csv\|pdf&...` |

All results tenant-scoped. Export filenames include hotel/business name and period.

---

## Audit Logs — `/api/v1/audit-logs` (OWNER only)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/audit-logs` | Filterable list |
| GET | `/audit-logs/{id}` | Detail |
| GET | `/audit-logs/alerts` | Suspicious activity indicators |

Filters: `user_id`, `action`, `from`, `to`, `entity_type`, `entity_id`, `q` (bill number search via join/metadata)

No DELETE endpoint.

---

## Health

### GET `/health`

Public liveness (no secrets). Optional DB ping on `/health/ready`.
