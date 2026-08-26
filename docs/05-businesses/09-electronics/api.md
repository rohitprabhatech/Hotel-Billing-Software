# Electronics Shops — API

Namespace: `/api/v1/...` (shared serial/repair + pack-specific installation).

| Method | Endpoint | Purpose | Auth | Permission | Tenant |
|--------|----------|---------|------|------------|--------|
| GET | `/api/v1/serial-units` | Serial inventory (shared) | JWT | `serial_imei` | Yes |
| GET/POST | `/api/v1/repairs` | Repair tickets (shared) | JWT | `repair_service` | Yes |
| GET/POST | `/api/v1/installations` | Installation jobs | JWT | `installation` | Yes |
| PATCH | `/api/v1/installations/{id}/status` | Status transitions | JWT Owner/Manager | `installation` | Yes |
| GET | `/api/v1/mobile/sales` | Brand/model sales (shared with mobile) | JWT | `serial_imei` | Yes |

Create installation body: `serial_unit_id`, `scheduled_at` (required); optional address, customer, technician, notes, charge. Status flow: `SCHEDULED` → `IN_PROGRESS` → `COMPLETED` (or `CANCELLED`).

## Contract notes

- **Authentication:** Bearer JWT (business user).
- **Tenant scope:** from JWT only.
- **Module:** `installation` enabled for `electronics` (and furniture later).
