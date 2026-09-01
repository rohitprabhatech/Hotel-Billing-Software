# Tenant & Authentication ERD

```mermaid
erDiagram
    tenants {
        string id PK
        string business_name
        string business_type
        string status
        string gstin
        datetime created_at
    }

    users {
        string id PK
        string tenant_id FK
        string role_id FK
        string email
        string name
        boolean is_active
    }

    roles {
        string id PK
        string name
    }

    subscriptions {
        string id PK
        string tenant_id FK
        string plan_id FK
        string status
    }

    subscription_plans {
        string id PK
        string code
        string name
    }

    master_admins {
        string id PK
        string email
        boolean is_active
    }

    tenants ||--o{ users : employs
    roles ||--o{ users : role
    tenants ||--o| subscriptions : subscribed
    subscription_plans ||--o{ subscriptions : plan
```

## Isolation rule

Every query on `users`, `customers`, `items`, `bills`, etc. must include **`tenant_id = JWT tenant`**.

Master admin routes use `master_admins` and may read cross-tenant **`tenants`** for SaaS operations only.
