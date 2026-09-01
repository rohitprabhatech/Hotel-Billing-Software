# Business Type → Database Models

**Source of truth:** `backend/app/constants/business_types.py`, `backend/app/constants/modules.py`

There are **13 canonical business type codes**. Legacy `building_material` maps to `hardware`. There is **no separate `businesses` table** and **no `business_id` column** on operational tables.

## Important: business type vs data isolation

| Concept | How it works |
|---------|----------------|
| **Tenant isolation** | `tenant_id` on rows — Tenant A cannot read Tenant B |
| **Business type** | Column on `tenants` — enables/disables modules and APIs |
| **Business data partition** | **Not implemented** — switching `business_type` does not create a new data partition; existing items/bills remain in the same tenant |

Industry packs share **`customers`**, **`items`**, **`bills`**, **`categories`**, etc. Module gates (`@module_required`) hide APIs; they do not split tables.

---

## All supported business types

| # | Code | Label | Industry modules (beyond core) |
|---|------|-------|--------------------------------|
| 1 | `hotel_restaurant` | Hotels / Restaurants | restaurant_menu, table_management, kot, kitchen, order_channels, recipe, wastage, service_charge |
| 2 | `cafe_tea` | Cafes / Tea Shops | restaurant_menu, table_management, kot, kitchen, order_channels, addons_combos, recipe, wastage |
| 3 | `grocery_kirana` | Grocery / Kirana | barcode_pos, bulk_pricing, batch_expiry, customer_credit |
| 4 | `clothing` | Clothing Shops | variants, product_images, returns_exchange, barcode_pos |
| 5 | `mobile` | Mobile Shops | serial_imei, warranty, repair_service, returns_exchange |
| 6 | `hardware` | Hardware / Building Material | uom_measurement, bulk_pricing, customer_credit, variants, quotation, delivery_challan, warehouse, transport_charges |
| 7 | `bakery_sweet` | Bakery / Sweet Shops | production, recipe, batch_expiry, custom_orders, wastage |
| 8 | `stationery` | Stationery Shops | barcode_pos, bulk_pricing, customer_credit |
| 9 | `electronics` | Electronics Shops | serial_imei, warranty, repair_service, installation, returns_exchange |
| 10 | `furniture` | Furniture Shops | furniture_attributes, custom_orders, quotation, delivery_tracking, installation |
| 11 | `book_store` | Book Stores | book_metadata, barcode_pos, bulk_pricing, returns_exchange |
| 12 | `wholesale` | Wholesale Shops | price_lists, sales_orders, purchase_orders, warehouse, customer_credit, quotation, delivery_challan, barcode_pos, bulk_pricing |
| 13 | `travel_agency` | Travel Agencies | tour_packages, travel_bookings, travel_commission, custom_orders |

**Core modules (all types):** core_billing, core_catalog, core_inventory, core_reports, core_users, core_audit, core_ai, core_settings

---

## Shared models (all / most business types)

| Domain | Tables |
|--------|--------|
| Tenant & auth | `tenants`, `users`, `roles`, `subscriptions`, `subscription_plans` |
| CRM | `customers`, `suppliers`, `party_ledger_entries` |
| Catalog | `categories`, `items`, `item_price_tiers`, `item_batches`, `item_variants`, `item_images` |
| Billing | `bills`, `bill_items`, `bill_number_counters`, `bill_deliveries`, `coupons`, `coupon_redemptions` |
| Purchases | `purchases`, `purchase_items`, `purchase_number_counters` |
| Inventory | `stock_movements`, `items.stock_quantity`, `warehouse_stocks` (if warehouse module) |
| Finance | `expenses`, `sales_returns`, `sales_return_items` |
| Audit | `audit_logs`, `notifications` |

---

## Business-specific tables (by type)

### Hotel / Restaurant (`hotel_restaurant`)

| Table | Purpose |
|-------|---------|
| `dining_tables` | Table layout, merge, status |
| `orders`, `order_items` | Open table orders |
| `kots`, `kot_items` | Kitchen tickets |
| `recipes`, `recipe_ingredients` | Menu → ingredient consumption |
| `wastage_entries` | Spoilage |

**Flow:** `dining_tables` → `orders` → `kots` → settle → `bills` → stock/recipe deduction

### Cafe (`cafe_tea`)

Same as hotel for floor/KOT **plus:**

| Table | Purpose |
|-------|---------|
| `item_addon_groups`, `item_addons`, `order_item_addons` | Add-ons |
| `combos`, `combo_items` | Combo meals |
| `coupons`, `coupon_redemptions` | Promotions |

### Grocery / Kirana (`grocery_kirana`)

Uses shared catalog + **`item_batches`** (expiry), **`item_price_tiers`** (bulk), **`customers.balance`** (udhari). No separate grocery tables.

### Clothing (`clothing`)

| Table | Purpose |
|-------|---------|
| `item_variants` | Size/color stock |
| `item_images` | Thumbnails |
| `sales_returns`, `sales_return_items` | Returns/exchange |

### Mobile / Electronics (`mobile`, `electronics`)

| Table | Purpose |
|-------|---------|
| `serial_units` | IMEI/serial tracking |
| `repair_orders` | Service tickets |
| `installation_orders` | Install scheduling (electronics/furniture) |
| `item_accessories` | Bundled accessories |

### Hardware (`hardware`)

Shared UOM fields on `items` + **`quotations`**, **`delivery_challans`**, **`warehouses`**, **`warehouse_stocks`**, **`stock_transfers`**

### Bakery (`bakery_sweet`)

| Table | Purpose |
|-------|---------|
| `production_runs`, `production_run_items` | Batch production |
| `custom_product_orders`, `custom_order_payments` | Cake/custom orders |
| `recipes`, `recipe_ingredients`, `item_batches`, `wastage_entries` |

### Stationery / Book store (`stationery`, `book_store`)

Shared barcode POS + bulk tiers. Book metadata lives on **`items`** columns (ISBN, author, publisher) — no separate books table.

### Wholesale (`wholesale`)

| Table | Purpose |
|-------|---------|
| `price_lists`, `price_list_items`, `customer_price_lists` | Customer-wise pricing |
| `sales_orders`, `sales_order_items` | SO → bill |
| `purchase_orders`, `purchase_order_items` | PO → purchase |
| Warehouse tables | Multi-location stock |

### Travel (`travel_agency`)

| Table | Purpose |
|-------|---------|
| `tour_packages` | Packages (links to `items`) |
| `travel_bookings`, `travel_booking_payments` | Bookings & advances |
| `travel_itinerary_items`, `travel_booking_documents` | Itinerary/docs |
| `travel_agents`, `travel_commission_entries` | Agent commission |

### Furniture (`furniture`)

| Table | Purpose |
|-------|---------|
| `custom_product_orders` | Made-to-order |
| `delivery_jobs` | Delivery tracking |
| `quotations`, `delivery_challans`, `installation_orders` | Quote → deliver → install |

---

## Duplicate tables — audit result

**No duplicate per-business customer/item/bill tables found.** Single shared schema with module gating.

Intentional parallel patterns (not duplicates):

- `orders` (restaurant) vs `sales_orders` (wholesale) vs `purchase_orders` (supplier)
- `AuditLog` (tenant) vs `PlatformAuditLog` (SaaS operator)
- `Notification` vs `PlatformNotification`
