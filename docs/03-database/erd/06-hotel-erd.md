# Hotel / Restaurant ERD

```mermaid
erDiagram
    dining_tables ||--o{ orders : hosts
    orders ||--|{ order_items : lines
    items ||--o{ order_items : menu_item
    orders ||--o{ kots : kitchen
    kots ||--|{ kot_items : lines
    order_items ||--o{ kot_items : from
    orders ||--o| bills : settles_to
    dining_tables ||--o{ kots : table_ref

    items ||--o| recipes : menu_recipe
    recipes ||--|{ recipe_ingredients : uses
    items ||--o{ recipe_ingredients : ingredient

    dining_tables {
        string id PK
        string tenant_id FK
        string table_number
        string status
    }

    orders {
        string id PK
        string tenant_id FK
        string dining_table_id FK
        string status
        string channel
    }

    kots {
        string id PK
        string tenant_id FK
        string order_id FK
        string status
    }
```

## Flow

```
Table (FREE) → Open Order → Add OrderItems → Print KOT → Kitchen updates status
           → Settle Order → Bill → Payment → Table FREE
           → Stock/recipe deduction on bill
```

Table **`orders`** here is **restaurant POS orders**, not wholesale **`sales_orders`**.
