# Inventory ERD

```mermaid
erDiagram
    tenants ||--o{ items : catalog
    items ||--o{ stock_movements : history
    items ||--o{ item_variants : variants
    items ||--o{ item_batches : batches
    items ||--o{ item_price_tiers : bulk_tiers
    items ||--o{ serial_units : serials

    warehouses ||--o{ warehouse_stocks : balances
    items ||--o{ warehouse_stocks : per_wh

    purchases ||--|{ purchase_items : lines
    purchases ||--o{ stock_movements : receive

    bills ||--o{ stock_movements : sale
    wastage_entries ||--o| stock_movements : spoilage
    production_runs ||--o{ stock_movements : produce

    items {
        string id PK
        string tenant_id FK
        decimal stock_quantity
        string uom
        string barcode
        string sku
    }

    stock_movements {
        string id PK
        string tenant_id FK
        string item_id FK
        string source
        decimal quantity_change
        decimal quantity_after
        string reference_type
        string reference_id
    }
```

## Stock timing

| Event | Stock change |
|-------|----------------|
| Purchase finalized | **+** quantity |
| Bill finalized (POS) | **−** quantity |
| Order settled (restaurant) | **−** via bill |
| Sales return approved | **+** quantity |
| Wastage recorded | **−** quantity |
| Production run | **−** ingredients, **+** finished goods |
| Recipe on bill | **−** ingredient items via `RecipeStockService` |

Concurrent updates use row locks on `items` (`ItemRepository.lock_for_update`).
