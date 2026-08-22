# Common Module — Suppliers

Tenant-scoped supplier master (BIZ-05). Prepares purchase and receive-stock flows in BIZ-06.

## Data Model

| Field | Notes |
|-------|-------|
| `id` | UUID |
| `tenant_id` | From JWT — never from client |
| `name` | Required |
| `phone_country_code`, `phone_national`, `phone_e164` | Optional; unique per tenant when E.164 set |
| `gstin` | Optional; normalized uppercase; unique per tenant when set |
| `email`, `address`, `notes` | Optional |
| `is_active` | Soft deactivate via DELETE or status patch |

## API (`/api/v1/suppliers`)

| Method | Path | Roles | Permission |
|--------|------|-------|------------|
| GET | `/suppliers` | Owner, Manager, Billing User | `suppliers.read` |
| POST | `/suppliers` | Owner, Manager | `suppliers.write` |
| GET | `/suppliers/:id` | Owner, Manager, Billing User | `suppliers.read` |
| PATCH | `/suppliers/:id` | Owner, Manager | `suppliers.write` |
| DELETE | `/suppliers/:id` | Owner, Manager | `suppliers.write` (soft deactivate) |
| PATCH | `/suppliers/:id/status` | Owner, Manager | `suppliers.write` |

List supports `q`, `is_active`, `page`, `per_page`.

## Roles

- **Owner / Manager:** full CRUD
- **Billing User:** read-only (list/get)

## Frontend

- Owner: `/owner/suppliers`
- Manager: `/billing/suppliers` (full CRUD)
- Billing User: `/billing/suppliers` (read-only UI)

## Audit

`CREATE_SUPPLIER`, `UPDATE_SUPPLIER`, `DEACTIVATE_SUPPLIER` with old/new snapshots.

## Migration

Run `flask db upgrade` — revision `20260822_biz05_suppliers`.

## Next

BIZ-06 Purchases will link stock receipts to `supplier_id`.
