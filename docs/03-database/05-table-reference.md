# Table Reference Index

Complete column-level detail: inspect `backend/app/models/*.py` and `database/schema.sql`.

**Total tables: 96**

---

## Platform & SaaS (10)

| Table | Model | Purpose |
|-------|-------|---------|
| `master_admins` | MasterAdmin | SaaS operator logins |
| `roles` | Role | OWNER, MANAGER, BILLING_USER |
| `subscription_plans` | SubscriptionPlan | Plan catalog |
| `subscriptions` | Subscription | Tenant subscription state |
| `subscription_notices` | SubscriptionNotice | Renewal/expiry notices |
| `platform_settings` | PlatformSettings | Global SaaS settings singleton |
| `platform_notifications` | PlatformNotification | Master dashboard alerts |
| `platform_audit_logs` | PlatformAuditLog | Platform lifecycle audit |
| `registration_requests` | RegistrationRequest | Signup approval queue |
| `password_reset_tokens` | PasswordResetToken | Auth tokens |
| `email_verification_tokens` | EmailVerificationToken | Email verify tokens |

---

## Tenant core (6)

| Table | PK | tenant_id | Soft delete | Purpose |
|-------|-----|-----------|-------------|---------|
| `tenants` | id | — | status | Business account |
| `users` | id | Yes | is_active | Logins |
| `audit_logs` | id | Yes | is_deleted | Activity trail |
| `notifications` | id | Yes | — | In-app alerts |
| `tenant_whatsapp_configs` | tenant_id | PK | — | WhatsApp integration |
| `bill_number_counters` | tenant_id | PK | — | Bill sequence |

---

## CRM & parties (3)

| Table | PK | tenant_id | Notes |
|-------|-----|-----------|-------|
| `customers` | id | Yes | is_active; balance for udhari |
| `suppliers` | id | Yes | is_active; balance |
| `party_ledger_entries` | id | Yes | Credit/collection history |

---

## Catalog (8)

| Table | Purpose |
|-------|---------|
| `categories` | Hierarchy (parent_id) |
| `items` | Products/services; stock_quantity; barcode; SKU; book fields |
| `item_variants` | Size/color (clothing) |
| `item_batches` | Expiry batches (grocery/bakery) |
| `item_price_tiers` | Bulk pricing |
| `item_images` | Product photos |
| `item_accessories` | Mobile bundles |
| `item_addon_groups`, `item_addons` | Cafe add-ons |

---

## Billing (6)

| Table | Purpose |
|-------|---------|
| `bills` | Invoices; payment_method; totals; cancel |
| `bill_items` | Line items |
| `bill_deliveries` | WhatsApp/email delivery log |
| `coupons`, `coupon_redemptions` | Cafe promotions |
| `sales_returns`, `sales_return_items` | Returns/exchange |

---

## Purchases & expenses (4)

| Table | Purpose |
|-------|---------|
| `purchases`, `purchase_items` | Stock receive |
| `expenses` | Operating expenses |
| `purchase_orders`, `purchase_order_items` | PO workflow (wholesale) |

---

## Inventory (2 + warehouse)

| Table | Purpose |
|-------|---------|
| `stock_movements` | All quantity changes audit |
| `wastage_entries` | Spoilage |
| `warehouses`, `warehouse_stocks`, `stock_transfers`, `stock_transfer_items` | Multi-warehouse |

---

## Restaurant / cafe (10)

| Table | Purpose |
|-------|---------|
| `dining_tables` | Table layout |
| `orders`, `order_items` | Restaurant orders |
| `kots`, `kot_items` | Kitchen tickets |
| `combos`, `combo_items` | Cafe bundles |
| `order_item_addons` | Selected add-ons |
| `recipes`, `recipe_ingredients` | BOM |

---

## Service / vertical (20+)

Includes: `serial_units`, `repair_orders`, `installation_orders`, `custom_product_orders`, `production_runs`, `quotations`, `delivery_challans`, `sales_orders`, `price_lists`, `tour_packages`, `travel_bookings`, `travel_agents`, `delivery_jobs`, etc.

See [04-business-type-models.md](./04-business-type-models.md) for mapping by business type.

---

## Example: `customers`

**Purpose:** Tenant-scoped customer master for billing and credit.

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | String(36) | No | PK UUID |
| tenant_id | String(36) | No | FK → tenants |
| name | String | No | |
| phone_country_code | String | Yes | |
| phone | String | Yes | |
| email | String | Yes | |
| balance | Decimal | No | Udhari outstanding |
| credit_limit | Decimal | Yes | |
| is_active | Boolean | No | Soft deactivation |
| created_at / updated_at | DateTime | No | Timestamps |

**Relationships:** 1:N → `bills`, `party_ledger_entries`, `customer_price_lists`

**Delete strategy:** Deactivate (`is_active=false`); bills retain `customer_id` or snapshot name

**Business types:** All

---

## Example: `bills`

**Purpose:** Finalized sales invoice.

| Column | Type | Notes |
|--------|------|-------|
| id | PK UUID | |
| tenant_id | FK | Required |
| bill_number | String | Unique per tenant |
| status | Enum-like | FINALIZED, CANCELLED |
| payment_method | String | cash, online, credit |
| grand_total | Decimal | |
| customer_id | FK | Optional |
| order_id | FK | Restaurant settlement |
| warehouse_id | FK | Optional |
| cancelled_at | DateTime | Cancel timestamp |

**Relationships:** 1:N `bill_items`; N:1 `customers`, `users`, `orders`

**API:** POST `/bills`, GET `/bills`, POST `/bills/:id/cancel`

---

## Number counter tables (tenant_id PK)

`bill_number_counters`, `order_number_counters`, `kot_number_counters`, `purchase_number_counters`, `purchase_order_number_counters`, `quotation_number_counters`, `sales_order_number_counters`, `sales_return_counters`, `delivery_challan_number_counters`, `delivery_number_counters`, `repair_number_counters`, `installation_number_counters`, `custom_order_number_counters`, `production_run_number_counters`, `travel_booking_number_counters`, `stock_transfer_number_counters`

Each allocates sequential document numbers per tenant with row locking in repository layer.
