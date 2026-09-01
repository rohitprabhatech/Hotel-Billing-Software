# Core Billing ERD

```mermaid
erDiagram
    tenants ||--o{ bill_number_counters : allocates
    tenants ||--o{ bills : issues
    customers ||--o{ bills : optional
    users ||--o{ bills : created_by
    orders ||--o| bills : settled_from

    bills ||--|{ bill_items : lines
    items ||--o{ bill_items : product
    item_variants ||--o{ bill_items : variant
    serial_units ||--o{ bill_items : serial

    bills ||--o{ bill_deliveries : whatsapp_email
    bills ||--o{ sales_returns : returned
    coupons ||--o{ coupon_redemptions : applied

    bills {
        string id PK
        string tenant_id FK
        string bill_number
        string status
        string payment_method
        decimal grand_total
        string customer_id FK
        datetime cancelled_at
    }

    bill_items {
        string id PK
        string tenant_id FK
        string bill_id FK
        string item_id FK
        decimal quantity
        decimal unit_price
        decimal line_total
    }

    bill_number_counters {
        string tenant_id PK
        int next_value
    }
```

## Bill creation flow (atomic transaction)

1. Lock `bill_number_counters` (`FOR UPDATE`)
2. Insert `bills` + `bill_items`
3. Deduct stock / serial / recipe ingredients
4. Insert `stock_movements`
5. Post credit to `customers.balance` if payment_method = credit
6. Insert `audit_logs`
7. `COMMIT`

Service: `BillService.create_bill()`

## Financial integrity

Totals computed in service layer before persist. Cancelled bills retain rows; status → `CANCELLED`.
