# Cafe ERD (extends Hotel)

Cafe reuses hotel floor/KOT tables and adds promotional catalog structures.

```mermaid
erDiagram
    items ||--o{ item_addon_groups : has
    item_addon_groups ||--|{ item_addons : options
    order_items ||--o{ order_item_addons : selected
    item_addons ||--o{ order_item_addons : addon

    combos ||--|{ combo_items : bundle
    items ||--o{ combo_items : part_of
    combos ||--o{ order_items : combo_line

    coupons ||--o{ coupon_redemptions : used
    orders ||--o{ coupon_redemptions : on_order
    bills ||--o{ coupon_redemptions : on_bill
```

## Cafe vs Hotel

| Feature | Hotel | Cafe |
|---------|-------|------|
| Tables/KOT | Yes | Yes |
| Service charge | Yes | No (module) |
| Add-ons/Combos | No | Yes |
| Coupons | No | Yes |
| Recipes/Wastage | Yes | Yes |

Same **`orders`** / **`bills`** tables — module gates control UI/API visibility.
