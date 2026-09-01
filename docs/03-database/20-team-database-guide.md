# Team Database Guide

A plain-language guide for explaining the billing database to your development team.

---

## 1. What is a Tenant?

A **tenant** is one customer business on your SaaS platform — e.g. "Shree Kirana Store", "Hotel Paradise", "City Mobile Shop".

- Stored in table: **`tenants`**
- One tenant = one business account = one subscription
- Has: `business_name`, `business_type`, GST/FSSAI, bill print settings, `status`

There is **no separate `businesses` table**. When the API says "business", it usually means the **tenant row**.

---

## 2. What is Business Type?

**Business type** is a code on the tenant that decides which **industry features** are enabled.

Examples:

- `hotel_restaurant` → tables, KOT, kitchen, recipes
- `grocery_kirana` → barcode POS, bulk pricing, udhari
- `travel_agency` → tour packages, bookings, commission

Stored in: **`tenants.business_type`**

It does **not** create a separate database partition. All items and bills for that tenant live in the same tables regardless of type. Changing type in Settings switches **modules**, not historical data storage.

---

## 3. What is a User?

A **user** is a login (owner, manager, or billing counter staff) belonging to **one tenant**.

- Table: **`users`**
- FK: `users.tenant_id` → `tenants.id`
- FK: `users.role_id` → `roles.id` (OWNER, MANAGER, BILLING_USER)

**Platform admins** (your SaaS operator) use **`master_admins`** — separate from tenant users.

---

## 4. How does tenant isolation work?

```
Login → JWT contains tenant_id
     → Every API loads RequestContext from JWT
     → Services call require_request_context()
     → Repositories filter: WHERE tenant_id = ctx.tenant_id
```

**Rules for developers:**

1. Never trust `tenant_id` from request body — always use JWT context.
2. Every new tenant-owned table needs `tenant_id` + repository filters.
3. Use `get_by_id_and_tenant(id, tenant_id)` pattern on reads/updates/deletes.

**Test suite:** `test_biz64_tenant_isolation_regression_suite.py` (parametrized IDOR tests).

---

## 5. How does billing work?

### Retail / POS (Grocery, Stationery, Hardware, Clothing)

```
Customer (optional) → Bill → BillItems → Item
                    → Payment method on Bill (cash/online/credit)
                    → StockMovement + Item.stock_quantity decrease
```

Tables: **`bills`**, **`bill_items`**, **`bill_number_counters`**

### Restaurant / Hotel

```
DiningTable → Order → OrderItems
            → KOT → Kitchen
            → Settle → Bill → Payment
            → Recipe may consume ingredient stock on bill
```

Tables: **`dining_tables`**, **`orders`**, **`order_items`**, **`kots`**, **`kots_items`**, **`bills`**

### Cafe

Same as restaurant + **addons/combos/coupons** on order lines.

---

## 6. How does inventory work?

### Product stock (most shops)

- **`items.stock_quantity`** — current on-hand (nullable = not tracked)
- **`stock_movements`** — audit trail (source: BILL, PURCHASE, WASTAGE, ADJUSTMENT, etc.)

**When stock decreases:** On **finalized bill** creation (POS) or order settlement (restaurant), inside the same DB transaction.

**When stock increases:** Purchase receive, production run, sales return, manual adjustment.

### Warehouse (hardware/wholesale)

- **`warehouses`**, **`warehouse_stocks`**, **`stock_transfers`**
- Bills may specify `warehouse_id`

### Serial / IMEI (mobile/electronics)

- **`serial_units`** — one row per device; status IN_STOCK → SOLD
- Bill line links `serial_unit_id`

### Recipes (hotel/cafe/bakery)

```
Menu Item (sold)
  → Recipe
  → RecipeIngredients (ingredient items)
  → StockMovement on each ingredient when bill finalized
```

Service: `RecipeStockService` — avoids double deduction if configured correctly.

---

## 7. How do purchases work?

```
Supplier → Purchase → PurchaseItems → Item stock IN
         → StockMovement (source PURCHASE)
```

Tables: **`suppliers`**, **`purchases`**, **`purchase_items`**

Wholesale may use **`purchase_orders`** first, then convert to **`purchases`**.

---

## 8. How does credit (udhari) work?

- **`customers.balance`** — amount customer owes
- Credit bills: `bills.payment_method = 'credit'`
- Collections: **`party_ledger_entries`** + payment APIs reduce balance

No separate `credit_accounts` table — balance on customer row + ledger history.

---

## 9. Invoice / bill numbering

- Table: **`bill_number_counters`** (PK = `tenant_id`)
- Allocation uses **`SELECT ... FOR UPDATE`** row lock
- Format: optional prefix from tenant settings + sequence number

Safe under concurrent billing users on same tenant.

---

## 10. Delete rules (financial safety)

| Entity | Strategy |
|--------|----------|
| Customer, Item, Category | **`is_active = false`** — soft deactivation |
| Bill | **`status = CANCELLED`** + reason — not hard deleted |
| BillItem | Kept for history; FK to item may SET NULL on item delete |
| Audit log | Owner can **`is_deleted`** hide from UI |
| Purchase | **`cancelled_at`** reverses stock where implemented |

**Never hard-delete finalized bills** in normal operations.

---

## 11. Primary keys

All entity IDs are **UUID strings (36 chars)** generated in application code.

Counter tables use **`tenant_id` as primary key** (one counter row per tenant per document type).

---

## 12. Simple ER example — retail sale

```
tenants
   │
   ├── customers
   │
   ├── items ← categories
   │
   └── bills ── bill_items ── items
            │
            └── stock_movements
```

---

## 13. Where to look in code

| Layer | Path |
|-------|------|
| Models | `backend/app/models/` |
| Repositories | `backend/app/repositories/` |
| Business logic | `backend/app/services/` |
| Bill + stock | `backend/app/services/bill_service.py` |
| Tenant context | `backend/app/utils/request_context.py` |
| Business types | `backend/app/constants/business_types.py` |
| Modules matrix | `backend/app/constants/modules.py` |

---

## 14. Questions developers ask

**Q: Do we need `hotel_items` and `grocery_items`?**  
A: No. One `items` table with `tenant_id`.

**Q: Where is business_id?**  
A: Nowhere. Use `tenant_id`. Business type is configuration on tenant.

**Q: Can two tenants share SKU?**  
A: Yes. Uniqueness is **per tenant** (barcode/SKU scoped in validation).

**Q: How do I add a new industry feature?**  
A: Add module code in `modules.py`, optional new tables with `tenant_id`, gate routes with `@module_required`.

---

## 15. Diagrams

See [`erd/`](./erd/) for Mermaid ERDs:

- System overview
- Tenant & auth
- Core billing
- Inventory
- Hotel / Cafe
- Business-specific summary
