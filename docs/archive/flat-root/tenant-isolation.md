# Tenant Isolation — Prabha Billing SaaS V2

## Rule

`tenant_id` is resolved from the authenticated session/JWT context.  
**Never trust `tenant_id` from request body or query for authorization.**

## Scope

Every tenant-owned resource must be filtered:

Users, customers, products, categories, bills, bill items, payments, purchases, inventory, stock, expenses, reports, notifications, audit logs, settings, subscription **views**.

## Cross-tenant tests

Create Tenant A and Tenant B. Attempt A’s token on B’s IDs.

| Expected | Not acceptable |
|----------|----------------|
| 403 Forbidden or 404 Not Found | Any of B’s data in response |

## Master Admin

Master may list tenants by design; still must not expose password hashes or secrets. Platform audit is separate from tenant `audit_logs`.

## Current implementation

Repositories/services already scope by context for existing tables. New V2 tables must follow the same pattern from day one of each sprint.
