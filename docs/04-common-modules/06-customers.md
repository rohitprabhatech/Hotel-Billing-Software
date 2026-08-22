# Common Module — Customers

Tenant-scoped customer master (BIZ-04). Links optional `customer_id` on bills while preserving ad-hoc name/phone/email for walk-in sales.

## Data Model

| Field | Notes |
|-------|-------|
| `id` | UUID |
| `tenant_id` | From JWT — never from client |
| `name` | Required |
| `phone_country_code`, `phone_national`, `phone_e164` | Optional; unique per tenant when E.164 set |
| `email` | Optional |
| `credit_limit` | Optional decimal — max outstanding allowed |
| `balance` | Cached outstanding (udhari) amount |
| `notes` | Optional free text |
| `is_active` | Soft deactivate via DELETE or status patch |

Bills retain denormalized customer contact fields plus optional `customer_id` FK (`ON DELETE SET NULL`).

## API (`/api/v1/customers`)

| Method | Path | Roles | Permission |
|--------|------|-------|------------|
| GET | `/customers` | Owner, Manager, Billing User | `customers.read` |
| POST | `/customers` | Owner, Manager, Billing User | `customers.write` |
| GET | `/customers/:id` | Owner, Manager, Billing User | `customers.read` |
| PATCH | `/customers/:id` | Owner, Manager, Billing User | `customers.write` |
| DELETE | `/customers/:id` | Owner, Manager, Billing User | `customers.write` (soft deactivate) |
| PATCH | `/customers/:id/status` | Owner, Manager, Billing User | `customers.write` |
| GET | `/customers/:id/bills` | Owner, Manager, Billing User | `customers.read` |

Query params on list: `q`, `is_active`, `page`, `per_page`.

Bill create accepts optional `customer_id`. Explicit `customer_name` / phone / email on the bill override master defaults when both are sent.

## Frontend

- Owner: `/owner/customers` — full CRM list, form, purchase history
- Billing / Manager: `/billing/customers` — same page in billing shell
- New Bill: `CustomerPicker` autocomplete + editable contact fields

## Audit

`CREATE_CUSTOMER`, `UPDATE_CUSTOMER`, `DEACTIVATE_CUSTOMER` with old/new snapshots.

## Migration

Run `flask db upgrade` — revision `20260822_biz04_customers`.
