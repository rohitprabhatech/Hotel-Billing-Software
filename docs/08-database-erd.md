# 08 — Database ERD

## Entity Relationship Diagram

```mermaid
erDiagram
    TENANTS ||--o{ USERS : has
    TENANTS ||--o{ CATEGORIES : has
    TENANTS ||--o{ ITEMS : has
    TENANTS ||--o{ BILLS : has
    TENANTS ||--o{ BILL_ITEMS : has
    TENANTS ||--o{ AUDIT_LOGS : has
    TENANTS ||--o| BILL_NUMBER_COUNTERS : has

    ROLES ||--o{ USERS : assigns

    CATEGORIES ||--o{ CATEGORIES : parent_of
    CATEGORIES ||--o{ ITEMS : contains

    USERS ||--o{ BILLS : creates
    USERS ||--o{ BILLS : cancels
    USERS ||--o{ AUDIT_LOGS : performs

    BILLS ||--|{ BILL_ITEMS : contains
    ITEMS ||--o{ BILL_ITEMS : snapshotted_in

    TENANTS {
        char id PK
        string name
        string business_name
        string address
        string city
        string state
        string pincode
        string phone
        string email
        string gst_number
        string fssai_number
        string bill_number_prefix
        decimal default_gst_percent
        string status
        datetime created_at
        datetime updated_at
    }

    ROLES {
        char id PK
        string name UK
        string description
        datetime created_at
        datetime updated_at
    }

    USERS {
        char id PK
        char tenant_id FK
        char role_id FK
        string name
        string email
        string password_hash
        boolean is_active
        datetime last_login_at
        datetime created_at
        datetime updated_at
    }

    CATEGORIES {
        char id PK
        char tenant_id FK
        char parent_id FK
        string name
        text description
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    ITEMS {
        char id PK
        char tenant_id FK
        char category_id FK
        string name
        text description
        decimal price
        decimal gst_percentage
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    BILLS {
        char id PK
        char tenant_id FK
        string bill_number
        bigint bill_sequence
        string table_number
        decimal subtotal
        decimal discount
        decimal taxable_amount
        decimal cgst_amount
        decimal sgst_amount
        decimal gst_amount
        decimal grand_total
        decimal round_off
        string status
        char created_by FK
        char cancelled_by FK
        datetime cancelled_at
        text cancellation_reason
        int printed_count
        datetime created_at
        datetime updated_at
    }

    BILL_ITEMS {
        char id PK
        char tenant_id FK
        char bill_id FK
        char item_id FK
        string item_name
        decimal quantity
        decimal unit_price
        decimal gst_percentage
        decimal discount
        decimal taxable_amount
        decimal cgst_amount
        decimal sgst_amount
        decimal total
        datetime created_at
    }

    AUDIT_LOGS {
        char id PK
        char tenant_id FK
        char user_id FK
        string user_name
        string action
        string entity_type
        char entity_id
        json old_data
        json new_data
        string ip_address
        string user_agent
        datetime created_at
    }

    BILL_NUMBER_COUNTERS {
        char tenant_id PK
        bigint next_value
        datetime updated_at
    }
```

## Cardinality Summary

| Relationship | Cardinality |
|--------------|-------------|
| Tenant → Users | 1:N |
| Tenant → Categories | 1:N |
| Tenant → Items | 1:N |
| Tenant → Bills | 1:N |
| Category → Items | 1:N |
| Category → Category (parent) | 1:N optional |
| Bill → Bill Items | 1:N |
| User → Bills (created_by) | 1:N |
| Item → Bill Items | 1:N (historical; snapshot stored) |
| Tenant → Audit Logs | 1:N |

## Unique Constraints

```text
roles.name
users (tenant_id, email)
bills (tenant_id, bill_number)
bills (tenant_id, bill_sequence)
categories (tenant_id, parent_id, name)  -- recommended
```

## Isolation Key

Every tenant-scoped FK path is guarded by matching `tenant_id` in application queries. Prefer storing `tenant_id` on child tables (`bill_items`, `audit_logs`) to avoid accidental cross-tenant joins.
