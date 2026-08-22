# API Architecture — Prabha Billing SaaS V2

**Style:** REST · JSON envelope · Bearer JWT · `/api/v1`  
**Phase:** Conceptual — do not implement new industry APIs until approved sprints.

---

## 1. Pipeline

```
Frontend → API → AuthN → AuthZ → Tenant resolution → Service → SQLAlchemy → MySQL
→ Response → UI
```

Never authorize using client-supplied `tenant_id`.

---

## 2. Existing common prefixes (keep)

| Prefix | Area |
|--------|------|
| `/auth` | Login, register-business, password, verify |
| `/public` | Plans |
| `/master` | Platform ops |
| `/profile` `/users` `/tenants` | Account / tenant |
| `/categories` `/items` | Catalog (items → products later) |
| `/bills` | Billing |
| `/stock-movements` | Inventory ledger |
| `/reports` `/audit-logs` `/notifications` `/ai` | Ops |
| `/webhooks/whatsapp` | Meta |

---

## 3. Target common APIs (additive)

| Prefix | Purpose |
|--------|---------|
| `/customers` | Customer CRM |
| `/suppliers` | Suppliers |
| `/products` `/services` | Catalog split (or evolve `/items`) |
| `/payments` | Payment allocations |
| `/purchases` | Purchase orders |
| `/expenses` | Expenses |
| `/inventory` | Balances, batches, serials, warehouses |
| `/quotations` | Quotes |
| `/modules/me` | Enabled modules/features for session |

Exact paths finalized per sprint; prefer evolving `/items` over a breaking rename without migration plan.

---

## 4. Industry API namespaces (conceptual)

```
/api/v1/restaurant/...
/api/v1/cafe/...
/api/v1/grocery/...
/api/v1/clothing/...
/api/v1/mobile/...
/api/v1/hardware/...
/api/v1/bakery/...
/api/v1/stationery/...
/api/v1/electronics/...
/api/v1/furniture/...
/api/v1/building-material/...
/api/v1/books/...
/api/v1/wholesale/...
/api/v1/travel/...
```

Only register blueprints when the industry pack sprint starts. Guard with module entitlement.

---

## 5. Envelope

```json
{ "success": true, "data": {}, "meta": { "page": 1, "per_page": 25, "total": 0 }, "error": null }
```

Errors: `VALIDATION_ERROR`, `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`, `SUBSCRIPTION_INACTIVE` (402), etc.

---

## 6. Integration verification (per sprint)

For each critical resource: Create/Read/Update/Delete (or soft status) and confirm UI ↔ API ↔ DB consistency. Cross-tenant IDs → 403/404.
