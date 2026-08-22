# Platform Architecture — Prabha Billing SaaS V2

**Phase:** Documentation only · Extend existing Business Billing SaaS

---

## 1. High-level

```
                 PRABHA BILLING SaaS
                        |
                 MASTER PLATFORM
                        |
        ---------------------------------
        |                               |
   COMMON CORE                    INDUSTRY MODULES
        |                               |
 Billing Inventory Customers     Restaurant Cafe Grocery Clothing
 Payments Reports Users          Mobile Hardware Bakery ... Travel
 GST Expenses Suppliers
 Subscriptions Notifications Audit AI WhatsApp
```

---

## 2. Layers

| Layer | Responsibility |
|-------|----------------|
| Public web | Landing, register, pricing, privacy/terms |
| Master console | Approvals, plans, trial, businesses, platform audit |
| Tenant console | Owner / Billing / Manager apps |
| API | Flask REST `/api/v1` |
| Domain services | Business rules (no logic in routes) |
| Persistence | SQLAlchemy → MySQL/MariaDB |
| Integrations | WhatsApp, SMTP, future gateways |

---

## 3. Industry configuration

```
Tenant.business_type_id
  → BusinessType
    → BusinessTypeModule[] → Module
    → BusinessTypeFeature[] → Feature
  → Runtime: nav + dashboard + API allow-list
```

Hard-coding industry logic in shared billing routes is forbidden; use extension hooks / module services.

---

## 4. Tenancy

- Shared database, logical isolation via `tenant_id`.  
- JWT / Master context supplies tenant; **never** client-supplied `tenant_id` for authz.  
- Platform tables (`master_admins`, plans, module catalog) are global.

---

## 5. Subscription gate

```
Request → Auth → Subscription entitlement check
  → ACTIVE/TRIAL (and not blocked) → proceed
  → EXPIRED/CANCELLED/SUSPENDED → 402 on billing APIs
  → Tenant SUSPENDED → login blocked
```

---

## 6. Relationship to current system

| Keep | Add |
|------|-----|
| Flask layering (controllers/services/repos) | `modules/` industry packages |
| Master + registration + plans | Module/feature registry |
| Bills / items / stock movements | Customers, suppliers, purchase, expense |
| Dual Owner/Billing layouts | Type-aware nav + UX fix |

---

## 7. Quality attributes

Security, isolation, auditability, extensibility (new type without full rewrite), operability (backup, inspect, stamp).

Related: [backend-architecture.md](./backend-architecture.md) · [frontend-architecture.md](./frontend-architecture.md) · [database-architecture.md](./database-architecture.md)
