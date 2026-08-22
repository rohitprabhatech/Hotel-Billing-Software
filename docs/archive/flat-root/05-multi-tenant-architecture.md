# 05 — Multi-Tenant Architecture

## Model

**Shared database, shared schema, row-level isolation by `tenant_id`.**

```text
Tenant 1 (Hotel A) ─┐
Tenant 2 (Hotel B) ─┼──► Same MySQL schema, different tenant_id values
Tenant 3 (Hotel C) ─┘
```

## Tenant Identity

- Primary key: UUID (`tenants.id`)
- Used as foreign key / column on all tenant-scoped entities
- Resolved **only** from authenticated user record / JWT claims

## What Is Tenant-Scoped

| Entity | Scoped? |
|--------|---------|
| tenants | N/A (root) |
| roles | Global seed (`OWNER`, `BILLING_USER`) |
| users | Yes |
| categories | Yes |
| items | Yes |
| bills | Yes |
| bill_items | Yes |
| audit_logs | Yes |
| tenant settings / GST defaults (if added) | Yes |

## Isolation Rules

1. **Never trust client `tenant_id`** — ignore if sent; use JWT-derived value.
2. **Every repository method** that reads/writes tenant data accepts or reads `tenant_id` from auth context.
3. **Joins** must not leak rows across tenants (always include tenant predicate).
4. **Exports** filter by tenant before file generation.
5. **Bill numbers** unique per tenant, not globally.
6. **IDs in URLs** (e.g., `/bills/{id}`) are looked up with `(id, tenant_id)`.

## JWT Claim Strategy

Recommended claims:

```json
{
  "sub": "<user_uuid>",
  "tenant_id": "<tenant_uuid>",
  "role": "OWNER",
  "exp": 1234567890
}
```

On each request:

```text
JWT → user_id + tenant_id + role
     → optional DB re-check: user.active && user.tenant_id matches claim
     → bind to request context
```

If claim `tenant_id` disagrees with DB user record → reject token.

## Query Pattern (Mandatory)

```text
SELECT * FROM bills
WHERE id = :bill_id
  AND tenant_id = :current_tenant_id
```

Never:

```text
SELECT * FROM bills WHERE id = :bill_id   -- missing tenant filter
```

## Cross-Tenant Attack Scenarios (Must Fail)

| Attack | Expected Result |
|--------|-----------------|
| User A requests bill ID belonging to Tenant B | 404 or 403 (no data leak) |
| Client sends `tenant_id` of another hotel in body | Ignored; own tenant used |
| Export with forged tenant filter | Own tenant only |
| Audit log ID from another tenant | 404/403 |

## Tenant Lifecycle (v1)

| Operation | Support |
|-----------|---------|
| Provision tenant + owner user | Seed/admin script or controlled onboarding API (internal) |
| Suspend tenant (`status`) | Owner/platform; blocks login when inactive |
| Delete tenant | Out of scope for app users; ops-only if ever needed |

Public self-signup of new hotels may be deferred; v1 can use controlled provisioning.

## Indexes Supporting Isolation

Composite indexes always leading with `tenant_id`:

- `(tenant_id, bill_number)` UNIQUE
- `(tenant_id, created_at)`
- `(tenant_id, status)`
- `(tenant_id, category_id)` on items
- `(tenant_id, user_id, created_at)` on audit_logs

## Testing Mandate

Automated tests must prove:

1. Tenant A cannot list Tenant B items/bills/users/audit
2. Tenant A cannot cancel Tenant B bill by ID
3. Login JWT from A cannot access B even with B's resource UUIDs

See [18-testing-strategy.md](./18-testing-strategy.md).
