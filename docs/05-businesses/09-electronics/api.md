# Electronics Shops — API

Namespace: `/api/v1/electronics/...`

Do **not** re-document common `/bills`, `/customers`, `/items` here — use those.

| Method | Endpoint | Purpose | Auth | Permission | Tenant |
|--------|----------|---------|------|------------|--------|
| GET/POST | `/api/v1/electronics/serials` | Serial inventory | JWT | industry + role | Yes |
| GET/POST | `/api/v1/electronics/warranties` | Warranties | JWT | industry + role | Yes |
| GET/POST | `/api/v1/electronics/repairs` | Repairs | JWT | industry + role | Yes |
| GET/POST | `/api/v1/electronics/installations` | Install jobs | JWT | industry + role | Yes |

## Contract notes

- **Authentication:** Bearer JWT (business user).
- **Tenant scope:** from JWT only.
- **Validation:** 400 on bad payload; 409 on unique conflicts (e.g. IMEI).
- **Errors:** 401 / 403 / 404 / 402 (subscription).

### Example response envelope

```json
{ "success": true, "data": {}, "meta": {}, "error": null }
```
