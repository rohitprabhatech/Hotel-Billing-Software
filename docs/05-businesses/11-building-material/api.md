# Hardware / Building Material — API

Namespace: `/api/v1/building-material/...`

Do **not** re-document common `/bills`, `/customers`, `/items` here — use those.

| Method | Endpoint | Purpose | Auth | Permission | Tenant |
|--------|----------|---------|------|------------|--------|
| GET/POST | `/api/v1/building-material/warehouses` | Warehouses | JWT | industry + role | Yes |
| POST | `/api/v1/building-material/transfers` | Stock transfer | JWT | industry + role | Yes |
| GET/POST | `/api/v1/building-material/quotations` | Quotes | JWT | industry + role | Yes |
| GET/POST | `/api/v1/building-material/challans` | Challans | JWT | industry + role | Yes |

## Contract notes

- **Authentication:** Bearer JWT (business user).
- **Tenant scope:** from JWT only.
- **Validation:** 400 on bad payload; 409 on unique conflicts (e.g. IMEI).
- **Errors:** 401 / 403 / 404 / 402 (subscription).

### Example response envelope

```json
{ "success": true, "data": {}, "meta": {}, "error": null }
```
