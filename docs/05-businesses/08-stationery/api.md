# Stationery Shops — API

Namespace: `/api/v1/stationery/...`

Do **not** re-document common `/bills`, `/customers`, `/items` here — use those.

| Method | Endpoint | Purpose | Auth | Permission | Tenant |
|--------|----------|---------|------|------------|--------|
| GET | `/api/v1/stationery/products/search` | Fast search | JWT | industry + role | Yes |
| GET | `/api/v1/stationery/products/by-barcode/{code}` | Barcode | JWT | industry + role | Yes |
| GET/POST | `/api/v1/stationery/brands` | Brands | JWT | industry + role | Yes |

## Contract notes

- **Authentication:** Bearer JWT (business user).
- **Tenant scope:** from JWT only.
- **Validation:** 400 on bad payload; 409 on unique conflicts (e.g. IMEI).
- **Errors:** 401 / 403 / 404 / 402 (subscription).

### Example response envelope

```json
{ "success": true, "data": {}, "meta": {}, "error": null }
```
