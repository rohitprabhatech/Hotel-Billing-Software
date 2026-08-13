# 18 — Testing Strategy

## Goals

Prove correctness of billing math, tenant isolation, authorization, audit, and reports before production.

## Test Pyramid

| Layer | Scope | Tools (suggested) |
|-------|-------|-------------------|
| Unit | Services (GST, discount, bill number format) | pytest |
| Integration | API + DB (transactions, auth) | pytest + Flask test client |
| Isolation | Cross-tenant access matrices | pytest |
| Frontend | Critical flows (optional v1) | React Testing Library |
| Manual | Print layout, UX speed | Checklist |

## Critical Test Cases

### Authentication & Authorization

- Valid login returns JWT + role
- Invalid password → 401
- Inactive user → 401/403
- BILLING_USER cannot access `/reports` or `/audit-logs`
- OWNER can access owner endpoints

### Tenant Isolation

For tenants A and B:

- A cannot GET B's item/bill/user/audit by id
- A cannot list B's resources
- A cannot cancel B's bill
- Forged body `tenant_id` ignored
- Export for A contains only A

### Billing

- Subtotal, discount, CGST, SGST, grand total match Decimal expectations
- Mixed GST rates sum correctly
- Inactive item rejected
- Concurrent bill creation → unique bill numbers
- Finalize atomic: failure rolls back bill, items, audit
- Client totals ignored

### Historical Snapshots

- Change item price after bill → old bill still shows old rate/name

### Cancellation

- Reason required
- Status becomes CANCELLED
- Sales totals exclude cancelled (per policy)
- Audit contains who/when/why/amount
- No hard delete endpoint

### Printing / Audit

- Print/reprint creates audit and increments counter

### Reports & Export

- Today/yesterday/month/custom aggregates correct
- Excel/CSV only tenant data
- EXPORT_REPORT audited

### Items / Categories

- Deactivated item hidden from billing search
- Still present on historical bills

## Test Data Strategy

- Factory fixtures for tenant, owner, billing user, items
- Isolated DB per test run (transaction rollback or recreate)

## Acceptance Gate (per sprint)

```text
Implement → Automated/manual tests → Fix → Verify acceptance criteria → Next sprint
```

## Sprint 9 Focus

Full regression of the lists above plus security and error-envelope checks.
