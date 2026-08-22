# Travel Agencies — API

Namespace: `/api/v1/travel/...`

Do **not** re-document common `/bills`, `/customers`, `/items` here — use those.

| Method | Endpoint | Purpose | Auth | Permission | Tenant |
|--------|----------|---------|------|------------|--------|
| GET/POST | `/api/v1/travel/packages` | Packages | JWT | industry + role | Yes |
| GET/POST | `/api/v1/travel/bookings` | Bookings | JWT | industry + role | Yes |
| POST | `/api/v1/travel/bookings/{id}/payments` | Advance/balance | JWT | industry + role | Yes |
| GET/POST | `/api/v1/travel/agents` | Agents | JWT | industry + role | Yes |
| GET | `/api/v1/travel/commissions` | Commissions | JWT | industry + role | Yes |

## Contract notes

- **Authentication:** Bearer JWT (business user).
- **Tenant scope:** from JWT only.
- **Validation:** 400 on bad payload; 409 on unique conflicts (e.g. IMEI).
- **Errors:** 401 / 403 / 404 / 402 (subscription).

### Example response envelope

```json
{ "success": true, "data": {}, "meta": {}, "error": null }
```
