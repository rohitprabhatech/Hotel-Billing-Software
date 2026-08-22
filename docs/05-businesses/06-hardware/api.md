# Hardware Stores — API

Namespace: `/api/v1/hardware/...`

Do **not** re-document common `/bills`, `/customers`, `/items` here — use those.

| Method | Endpoint | Purpose | Auth | Permission | Tenant |
|--------|----------|---------|------|------------|--------|
| GET/POST | `/api/v1/hardware/units` | UOM master | JWT | industry + role | Yes |
| GET | `/api/v1/hardware/products/{id}/price-history` | Price history | JWT | industry + role | Yes |
| GET/POST | `/api/v1/hardware/credit` | Credit accounts | JWT | industry + role | Yes |

## Contract notes

- **Authentication:** Bearer JWT (business user).
- **Tenant scope:** from JWT only.
- **Validation:** 400 on bad payload; 409 on unique conflicts (e.g. IMEI).
- **Errors:** 401 / 403 / 404 / 402 (subscription).

### Example response envelope

```json
{ "success": true, "data": {}, "meta": {}, "error": null }
```
