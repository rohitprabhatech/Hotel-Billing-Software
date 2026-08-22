# Wholesale Shops — API

Namespace: `/api/v1/wholesale/...`

Do **not** re-document common `/bills`, `/customers`, `/items` here — use those.

| Method | Endpoint | Purpose | Auth | Permission | Tenant |
|--------|----------|---------|------|------------|--------|
| GET/POST | `/api/v1/wholesale/price-lists` | Pricing | JWT | industry + role | Yes |
| GET/POST | `/api/v1/wholesale/sales-orders` | SO | JWT | industry + role | Yes |
| GET/POST | `/api/v1/wholesale/purchase-orders` | PO | JWT | industry + role | Yes |
| GET/POST | `/api/v1/wholesale/warehouses` | Warehouses | JWT | industry + role | Yes |
| POST | `/api/v1/wholesale/transfers` | Transfers | JWT | industry + role | Yes |
| GET | `/api/v1/wholesale/outstanding` | Outstanding | JWT | industry + role | Yes |

## Contract notes

- **Authentication:** Bearer JWT (business user).
- **Tenant scope:** from JWT only.
- **Validation:** 400 on bad payload; 409 on unique conflicts (e.g. IMEI).
- **Errors:** 401 / 403 / 404 / 402 (subscription).

### Example response envelope

```json
{ "success": true, "data": {}, "meta": {}, "error": null }
```
