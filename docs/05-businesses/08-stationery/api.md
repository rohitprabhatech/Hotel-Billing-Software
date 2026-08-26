# Stationery Shops — API

Namespace: `/api/v1/stationery/...` (BIZ-44 thin aliases over grocery barcode POS).

Do **not** re-document common `/bills`, `/customers`, `/items` here — use those.

| Method | Endpoint | Purpose | Auth | Permission | Tenant |
|--------|----------|---------|------|------------|--------|
| GET | `/api/v1/stationery/pos-catalog` | Catalog (+ optional `?q=`) | JWT | `items:read` + `barcode_pos` | Yes |
| GET | `/api/v1/stationery/products/search` | Search-first alias of catalog | JWT | `items:read` + `barcode_pos` | Yes |
| GET | `/api/v1/stationery/products/by-barcode/{code}` | Exact barcode lookup | JWT | `items:read` + `barcode_pos` | Yes |

Billing / credit / bulk pricing reuse common endpoints (`/bills`, `/customers/outstanding`, item bulk tiers).

## Contract notes

- **Authentication:** Bearer JWT (Owner / Manager / Billing).
- **Tenant scope:** from JWT only.
- **Module gate:** `barcode_pos` (enabled for `business_type=stationery`).
- **Errors:** 401 / 403 (wrong business or missing module) / 404.

### Example response envelope

```json
{ "success": true, "data": {}, "meta": {}, "error": null }
```
