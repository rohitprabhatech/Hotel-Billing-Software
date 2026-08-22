# Backend Architecture — Prabha Billing SaaS V2

**Stack:** Python · Flask · SQLAlchemy · MySQL/MariaDB · JWT  
**Rule:** No business logic in route handlers.

---

## 1. Current structure (retain)

```
backend/app/
  config/ controllers/ routes/ services/ repositories/
  models/ schemas/ middleware/ utils/ templates/ constants/
```

This matches clean layering already used in production.

---

## 2. Target extension (conceptual)

```
backend/app/
  ...existing...
  core/                    # shared kernels (billing, inventory, tax)
  modules/
    billing/
    inventory/
    customers/
    suppliers/
    purchases/
    expenses/
    reports/
    notifications/
    subscriptions/
    restaurant/
    cafe/
    grocery/
    clothing/
    mobile/
    hardware/
    bakery/
    stationery/
    electronics/
    furniture/
    building_material/
    books/
    wholesale/
    travel/
```

Industry folders hold **industry services + routes** that call **core** engines. Do not duplicate bill posting logic per industry.

---

## 3. Request pipeline

```
HTTP → Blueprint → Middleware (auth / master / roles)
  → Controller (thin) → Service → Repository → DB
  → Envelope response { success, data, meta, error }
```

Tenant resolution: from JWT / request context only.

---

## 4. Core engines (services)

| Engine | Responsibility |
|--------|----------------|
| BillingEngine | Create/finalize/cancel invoices; tax; payments |
| InventoryEngine | Stock modes; movements; concurrency |
| TaxEngine | CGST/SGST/IGST rules |
| EntitlementService | Subscription access (exists) |
| AuditService / PlatformAudit | Append-only logs (exist) |
| NotificationService | Rule-driven alerts (extend) |
| ModuleRegistry | Resolve enabled modules for tenant |

---

## 5. Safety

- Migrations only after approved sprints + backup.  
- Idempotent helpers preferred for hosted MariaDB.  
- Never `DROP DATABASE` / production `DELETE` without explicit approval.

---

## 6. Testing

Pytest with `FLASK_ENV=testing` and project venv (existing suite). New modules add focused tests per sprint.
