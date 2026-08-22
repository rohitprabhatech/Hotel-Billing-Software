# 08 — Database ERD

**Current model:** 23 application tables in `backend/sql/02_schema.sql`.  
Text map + cascades: [database-relationships.md](./database-relationships.md).

## Entity Relationship Diagram

```mermaid
erDiagram
    ROLES ||--o{ USERS : assigns
    TENANTS ||--o{ USERS : has
    TENANTS ||--o{ CATEGORIES : has
    TENANTS ||--o{ ITEMS : has
    TENANTS ||--o| BILL_NUMBER_COUNTERS : has
    TENANTS ||--o{ BILLS : has
    TENANTS ||--o{ BILL_ITEMS : has
    TENANTS ||--o{ BILL_DELIVERIES : has
    TENANTS ||--o| TENANT_WHATSAPP_CONFIGS : has
    TENANTS ||--o{ NOTIFICATIONS : has
    TENANTS ||--o{ AUDIT_LOGS : has
    TENANTS ||--o{ STOCK_MOVEMENTS : has
    TENANTS ||--o{ SUBSCRIPTIONS : has
    TENANTS ||--o{ SUBSCRIPTION_NOTICES : has
    TENANTS ||--o{ REGISTRATION_REQUESTS : "optional after approve"

    CATEGORIES ||--o{ CATEGORIES : parent_of
    CATEGORIES ||--o{ ITEMS : contains
    USERS ||--o{ BILLS : creates
    USERS ||--o{ AUDIT_LOGS : performs
    USERS ||--o{ PASSWORD_RESET_TOKENS : owns
    USERS ||--o{ EMAIL_VERIFICATION_TOKENS : owns
    BILLS ||--|{ BILL_ITEMS : contains
    BILLS ||--o{ BILL_DELIVERIES : attempts
    ITEMS ||--o{ BILL_ITEMS : snapshotted_in
    ITEMS ||--o{ STOCK_MOVEMENTS : ledger

    MASTER_ADMINS ||--o{ REGISTRATION_REQUESTS : reviews
    MASTER_ADMINS ||--o{ PLATFORM_AUDIT_LOGS : acts
    SUBSCRIPTION_PLANS ||--o{ SUBSCRIPTIONS : priced_as
    SUBSCRIPTIONS ||--o{ SUBSCRIPTION_NOTICES : notices

    PLATFORM_SETTINGS
    PLATFORM_NOTIFICATIONS
```

## Cardinality notes

| From | To | Cardinality |
|------|-----|-------------|
| Tenant | Users / categories / items / bills | 1 : N |
| Category | Child categories | 1 : N (self) |
| Bill | Bill items | 1 : N (required lines) |
| Tenant | WhatsApp config / bill counter | 1 : 0..1 |
| Tenant | Subscription (current) | 1 : 0..N historically; app uses current row |
| Master Admin | Registration / platform audit | 1 : N |
| Plan | Subscriptions | 1 : N (`plan_id` nullable SET NULL) |

## Platform vs tenant

- **Tenant-scoped:** everything under a business (billing, catalog, stock, tenant audit).  
- **Platform:** `master_admins`, `platform_settings`, `subscription_plans`, `platform_notifications`, `platform_audit_logs`.  
- **Bridge:** `registration_requests`, `subscriptions`, `subscription_notices`.

## Attribute highlights (not exhaustive)

| Entity | Notable fields |
|--------|----------------|
| TENANTS | `business_type`, `status` ACTIVE\|SUSPENDED |
| USERS | `token_version`, email verify / pending email |
| CATEGORIES | generated `parent_key` for root uniqueness |
| ITEMS | `sku`, `cost_price`, `stock_quantity` |
| BILLS | `payment_method`, `table_number` (= reference) |
| MASTER_ADMINS | no `tenant_id` |
| SUBSCRIPTIONS | `price_at_purchase`, trial/paid ends, status |

Full columns: [07-database-design.md](./07-database-design.md).
