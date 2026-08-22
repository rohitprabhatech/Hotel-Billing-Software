# Database Architecture — Prabha Billing SaaS V2 (CONCEPTUAL)

> **CRITICAL:** This document is a **design**.  
> Do **not** create tables, migrations, or alter the live database until documentation is approved and a sprint explicitly authorizes schema work.  
> **Current live schema** (23 tables) remains authoritative for production until then — see [07-database-design.md](./07-database-design.md).

---

## 1. Design principles

1. Shared MySQL/MariaDB; logical multi-tenancy.  
2. Every tenant-owned row carries `tenant_id` (or reaches tenant via FK).  
3. Money as `DECIMAL`; never float.  
4. Soft-deactivate / cancel financial history; append-only audit & stock ledger.  
5. Extensibility via BusinessType → Module/Feature — not 14 schemas.  
6. **No Medical / prescription entities.**

---

## 2. Entity classes

| Class | Examples |
|-------|----------|
| **GLOBAL** | BusinessType, Module, Feature, SubscriptionPlan, MasterAdmin, PlatformSettings |
| **TENANT** | User, Customer, Supplier, Product, Bill, Stock, Expense, … |
| **BRIDGE** | RegistrationRequest, Subscription, BusinessTypeModule mapping |

---

## 3. Common entities (conceptual)

### Platform / tenancy

| Entity | Purpose |
|--------|---------|
| Tenant | Business workspace |
| BusinessType | One of 14 industries |
| Module | Catalog of core/industry modules |
| Feature | Fine-grained capability |
| BusinessTypeModule | Type ↔ module enablement |
| BusinessTypeFeature | Type ↔ feature enablement |
| TenantModuleOverride | Optional plan/tenant overrides |
| MasterAdmin | Platform operator |
| RegistrationRequest | Pending signup |
| PlatformSettings | Trial defaults, warning days |
| SubscriptionPlan | SaaS catalog |
| Subscription | Tenant entitlement |
| SubscriptionNotice | Expiry idempotency |
| PlatformNotification | Master alerts |
| PlatformAuditLog | Master actions |

### Identity

| Entity | Purpose |
|--------|---------|
| Role | OWNER, BILLING_USER, MANAGER (+ industry roles later) |
| Permission | Capability codes |
| RolePermission | M:N |
| User | Tenant user |
| UserPermission | Optional overrides |
| PasswordResetToken / EmailVerificationToken | Auth tokens |

### Catalog

| Entity | Purpose |
|--------|---------|
| Category | Hierarchy (`parent_id`) |
| Product | Sellable product |
| Service | Sellable service |
| ProductVariant | Size/color/SKU matrix |
| Unit | piece, kg, L, m, sq.ft, … |
| Brand | Optional shared within tenant |
| ProductImage | Optional media refs |
| Barcode / SKU fields | On product/variant |

### Parties

| Entity | Purpose |
|--------|---------|
| Customer | CRM |
| Supplier | Vendors |
| CustomerLedger / Credit | Udhari / outstanding (or payment allocations) |

### Commerce

| Entity | Purpose |
|--------|---------|
| Bill / Invoice | Header |
| BillItem | Product/service lines + snapshots |
| Payment | Allocations to bills (cash/UPI/card/credit/partial/advance) |
| BillReturn / Refund | Returns lifecycle |
| Quotation | Optional pre-bill |
| DeliveryChallan | Optional dispatch |

### Inventory

| Entity | Purpose |
|--------|---------|
| StockBalance | Per product/variant/warehouse/location |
| StockMovement | Ledger |
| BatchLot | Batch/lot + expiry |
| SerialUnit | IMEI/serial instances |
| Warehouse | Multi-location (wholesale/building) |
| StockTransfer | Between warehouses |
| Recipe / RecipeIngredient | Restaurant ingredient consumption |
| WastageEntry | Food/production waste |

### Procurement & expenses

| Entity | Purpose |
|--------|---------|
| PurchaseOrder / PurchaseItem | Buying |
| Expense / ExpenseCategory | P&L support |

### Ops

| Entity | Purpose |
|--------|---------|
| Notification | Tenant alerts |
| AuditLog | Tenant audit |
| BusinessSettings | Stock negative allow, GST mode, etc. |
| BillNumberCounter | Sequences |

---

## 4. Industry-specific entities (conceptual)

| Industry | Entities |
|----------|----------|
| Restaurant / Cafe | RestaurantTable, Order, KOT, KOTItem, KitchenTicket, WaiterAssignment |
| Clothing | Size, Color (or attribute tables), VariantStock |
| Mobile / Electronics | SerialUnit, Warranty, RepairTicket, InstallationJob |
| Bakery | ProductionBatch, CakeOrder |
| Furniture | CustomOrder, DeliveryJob |
| Wholesale / Building | Warehouse, StockTransfer, SalesOrder, PurchaseOrder, Quotation, DeliveryChallan |
| Books | BookMetadata (ISBN, author, publisher, edition) |
| Travel | TourPackage, Booking, Itinerary, TravelDocument, Agent, AgentCommission |

Avoid duplicating Product/Bill when a thin extension table suffices.

---

## 5. Product vs service

```
BillItem.line_type = PRODUCT | SERVICE
  PRODUCT → product_id / variant_id / serial_id / batch_id
  SERVICE → service_id / booking_id (travel)
```

Mixed invoices allowed.

---

## 6. Mapping from current 23 tables

| Current | V2 fate |
|---------|---------|
| tenants, users, roles, categories, items, bills, bill_items | Extend / rename conceptually (items → products) |
| stock_movements | Feed InventoryEngine |
| master_admins, registration_requests, plans, subscriptions, … | Keep |
| New CRM/procurement/industry tables | Added only in approved sprints |

---

## 7. Indexing (guidelines)

- `(tenant_id, …)` on all hot tenant tables  
- Unique business keys per tenant (email, SKU, bill_number, IMEI)  
- Partial uniques where NULL semantics matter (follow `parent_key` pattern)

---

## 8. Explicit non-entities

Medicine, Prescription, PharmacyBatch, MedicalReturn, MedicalDashboard — **forbidden** in this program.
