# Audit System — Prabha Billing SaaS V2

## Two ledgers

| Ledger | Scope |
|--------|-------|
| `audit_logs` | Tenant business activity |
| `platform_audit_logs` | Master Admin actions |

Never store passwords, tokens, or raw WhatsApp secrets in snapshots.

## Tenant events (examples)

Login/logout · Item/category CRUD · Bill create/cancel/return · Payment change · Stock adjust · Customer/user/settings/subscription-visible changes

## Record shape

Tenant, user, action, entity type/id, timestamp, old/new JSON, IP/UA when appropriate.

## Item activity

If Billing User adds/edits/deactivates items, Owner must still see full history (existing Item Activity + audit). Soft-deactivate preferred over hard delete.

## Retention

Append-only from application perspective; purge only via approved retention policy.
