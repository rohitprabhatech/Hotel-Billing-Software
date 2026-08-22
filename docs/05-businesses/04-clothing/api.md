# Clothing Shops — API

Namespace: `/api/v1/clothing/...`

Do **not** re-document common `/bills`, `/customers`, `/items` here — use those.

| Method | Endpoint | Purpose | Auth | Permission | Tenant |
|--------|----------|---------|------|------------|--------|
| GET/POST | `/api/v1/clothing/sizes` | Size master | JWT | industry + role | Yes |
| GET/POST | `/api/v1/clothing/colors` | Color master | JWT | industry + role | Yes |
| GET/POST | `/api/v1/clothing/brands` | Brand master | JWT | industry + role | Yes |
| GET/POST | `/api/v1/clothing/variants` | Variant stock | JWT | industry + role | Yes |
| POST | `/api/v1/clothing/returns` | Exchange/return | JWT | industry + role | Yes |

## Contract notes

- **Authentication:** Bearer JWT (business user).
- **Tenant scope:** from JWT only.
- **Validation:** 400 on bad payload; 409 on unique conflicts (e.g. IMEI).
- **Errors:** 401 / 403 / 404 / 402 (subscription).

### Example response envelope

```json
{ "success": true, "data": {}, "meta": {}, "error": null }
```
