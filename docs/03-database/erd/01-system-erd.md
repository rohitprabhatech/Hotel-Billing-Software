# System ERD (high level)

```mermaid
erDiagram
    tenants ||--o{ users : has
    tenants ||--o{ customers : has
    tenants ||--o{ suppliers : has
    tenants ||--o{ categories : has
    tenants ||--o{ items : has
    tenants ||--o{ bills : has
    tenants ||--o{ purchases : has
    tenants ||--o{ stock_movements : has
    tenants ||--o{ audit_logs : has

    roles ||--o{ users : assigns

    categories ||--o{ items : groups
    customers ||--o{ bills : optional
    bills ||--|{ bill_items : contains
    items ||--o{ bill_items : sold_as
    bills ||--o{ stock_movements : triggers

    suppliers ||--o{ purchases : supplies
    purchases ||--|{ purchase_items : contains
    items ||--o{ purchase_items : received
```

## Platform (no tenant ownership)

```mermaid
erDiagram
    master_admins ||--o{ platform_audit_logs : acts
    subscription_plans ||--o{ subscriptions : defines
    tenants ||--o| subscriptions : has
    registration_requests }o--|| tenants : becomes
```

See also: [02-tenant-erd.md](./02-tenant-erd.md), [03-billing-erd.md](./03-billing-erd.md), [04-inventory-erd.md](./04-inventory-erd.md), [06-hotel-erd.md](./06-hotel-erd.md), [07-cafe-erd.md](./07-cafe-erd.md)
