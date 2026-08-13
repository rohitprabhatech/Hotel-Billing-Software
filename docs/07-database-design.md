# 07 — Database Design

## Design Principles

1. Tenant isolation via `tenant_id` on all tenant-scoped tables
2. Decimal money fields (`DECIMAL(12,2)` typical; GST rates `DECIMAL(5,2)`)
3. Soft status changes for financial records (no hard delete via app)
4. Historical snapshots on `bill_items`
5. Proper PKs, FKs, unique constraints, and selective indexes
6. UTC timestamps (`created_at`, `updated_at`)

## Tables

### `tenants`

| Column | Type | Notes |
|--------|------|-------|
| id | CHAR(36) PK | UUID |
| name | VARCHAR(120) | Internal name |
| business_name | VARCHAR(200) | Printed on receipt |
| address | VARCHAR(255) | |
| city | VARCHAR(100) | |
| state | VARCHAR(100) | |
| pincode | VARCHAR(20) | |
| phone | VARCHAR(30) | |
| email | VARCHAR(255) | |
| gst_number | VARCHAR(30) NULL | GSTIN |
| fssai_number | VARCHAR(50) NULL | |
| bill_number_prefix | VARCHAR(20) NULL | e.g. `INV-2026-` or empty for plain sequence |
| default_gst_percent | DECIMAL(5,2) NULL | Optional default for new items |
| status | ENUM/VARCHAR | ACTIVE, SUSPENDED |
| created_at | DATETIME | |
| updated_at | DATETIME | |

### `roles`

| Column | Type | Notes |
|--------|------|-------|
| id | CHAR(36) PK | or SMALLINT |
| name | VARCHAR(50) UNIQUE | `OWNER`, `BILLING_USER` |
| description | VARCHAR(255) | |
| created_at | DATETIME | |
| updated_at | DATETIME | |

Seeded globally; not tenant-scoped.

### `users`

| Column | Type | Notes |
|--------|------|-------|
| id | CHAR(36) PK | |
| tenant_id | CHAR(36) FK → tenants | Indexed |
| role_id | FK → roles | |
| name | VARCHAR(120) | |
| email | VARCHAR(255) | Unique per tenant: `(tenant_id, email)` |
| password_hash | VARCHAR(255) | Never exposed in API |
| is_active | BOOLEAN | |
| last_login_at | DATETIME NULL | |
| created_at | DATETIME | |
| updated_at | DATETIME | |

Indexes: `(tenant_id)`, UNIQUE `(tenant_id, email)`, `(tenant_id, role_id)`

### `categories`

| Column | Type | Notes |
|--------|------|-------|
| id | CHAR(36) PK | |
| tenant_id | CHAR(36) FK | |
| parent_id | CHAR(36) NULL FK → categories | Subcategory support |
| name | VARCHAR(120) | |
| description | TEXT NULL | |
| is_active | BOOLEAN | |
| created_at | DATETIME | |
| updated_at | DATETIME | |

Indexes: `(tenant_id)`, UNIQUE `(tenant_id, parent_id, name)` (or `(tenant_id, name)` if flat)

### `items`

| Column | Type | Notes |
|--------|------|-------|
| id | CHAR(36) PK | |
| tenant_id | CHAR(36) FK | |
| category_id | CHAR(36) FK → categories | |
| name | VARCHAR(200) | |
| description | TEXT NULL | |
| price | DECIMAL(12,2) | Current selling price |
| gst_percentage | DECIMAL(5,2) | |
| is_active | BOOLEAN | Deactivate instead of delete |
| created_at | DATETIME | |
| updated_at | DATETIME | |

Indexes: `(tenant_id)`, `(tenant_id, category_id)`, `(tenant_id, is_active)`, search on name (prefix/like)

UNIQUE optional: `(tenant_id, name)` if business requires unique names.

### `bills`

| Column | Type | Notes |
|--------|------|-------|
| id | CHAR(36) PK | |
| tenant_id | CHAR(36) FK | |
| bill_number | VARCHAR(50) | Unique per tenant |
| bill_sequence | BIGINT | Internal monotonic sequence per tenant |
| table_number | VARCHAR(30) NULL | Optional |
| subtotal | DECIMAL(12,2) | |
| discount | DECIMAL(12,2) | Default 0 |
| taxable_amount | DECIMAL(12,2) | |
| cgst_amount | DECIMAL(12,2) | |
| sgst_amount | DECIMAL(12,2) | |
| gst_amount | DECIMAL(12,2) | cgst + sgst |
| grand_total | DECIMAL(12,2) | |
| round_off | DECIMAL(12,2) | Optional Indian rounding |
| status | VARCHAR(20) | DRAFT, FINALIZED, CANCELLED, VOID |
| created_by | CHAR(36) FK → users | |
| cancelled_by | CHAR(36) NULL FK → users | |
| cancelled_at | DATETIME NULL | |
| cancellation_reason | TEXT NULL | Required on cancel |
| printed_count | INT | Default 0; increment on print/reprint |
| created_at | DATETIME | |
| updated_at | DATETIME | |

Constraints/Indexes:

- UNIQUE `(tenant_id, bill_number)`
- UNIQUE `(tenant_id, bill_sequence)`
- INDEX `(tenant_id, created_at)`
- INDEX `(tenant_id, status)`
- INDEX `(tenant_id, created_by)`

### `bill_items`

| Column | Type | Notes |
|--------|------|-------|
| id | CHAR(36) PK | |
| tenant_id | CHAR(36) FK | Denormalized for isolation queries |
| bill_id | CHAR(36) FK → bills | |
| item_id | CHAR(36) NULL FK → items | Nullable if item later removed |
| item_name | VARCHAR(200) | Snapshot |
| quantity | DECIMAL(10,3) | Usually integer qty; decimal allowed |
| unit_price | DECIMAL(12,2) | Snapshot |
| gst_percentage | DECIMAL(5,2) | Snapshot |
| discount | DECIMAL(12,2) | Line or allocated |
| taxable_amount | DECIMAL(12,2) | |
| cgst_amount | DECIMAL(12,2) | |
| sgst_amount | DECIMAL(12,2) | |
| total | DECIMAL(12,2) | Line total |
| created_at | DATETIME | |

Indexes: `(tenant_id, bill_id)`, `(tenant_id, item_id)`

**No hard delete of rows after FINALIZED** via application. Draft line edits allowed only while `DRAFT`.

### `audit_logs`

| Column | Type | Notes |
|--------|------|-------|
| id | CHAR(36) PK | |
| tenant_id | CHAR(36) FK | |
| user_id | CHAR(36) NULL FK → users | |
| user_name | VARCHAR(120) | Snapshot for display |
| action | VARCHAR(50) | See action catalog |
| entity_type | VARCHAR(50) | BILL, ITEM, CATEGORY, USER, AUTH, REPORT |
| entity_id | CHAR(36) NULL | |
| old_data | JSON NULL | |
| new_data | JSON NULL | |
| ip_address | VARCHAR(45) NULL | |
| user_agent | VARCHAR(255) NULL | |
| created_at | DATETIME | |

Indexes: `(tenant_id, created_at)`, `(tenant_id, user_id)`, `(tenant_id, action)`, `(tenant_id, entity_type, entity_id)`

**Append-only** from application perspective.

### Optional: `bill_number_counters`

For concurrency-safe sequences:

| Column | Type | Notes |
|--------|------|-------|
| tenant_id | CHAR(36) PK | |
| next_value | BIGINT | Locked/updated in transaction |
| updated_at | DATETIME | |

Alternative: `SELECT MAX(bill_sequence) ... FOR UPDATE` on tenant row/counter.

## Bill Status Lifecycle

```text
DRAFT ──finalize──► FINALIZED ──cancel──► CANCELLED
                         │
                         └──void──► VOID   (if distinguished)
```

v1 may use CANCELLED and VOID as synonyms or treat VOID as owner-level cancel; document in billing workflow.

## Money & GST Notes

- Store amounts with 2 decimal places
- Split GST into CGST + SGST (equal halves of gst_percentage for intra-state model in v1)
- Backend recalculates; reject mismatched client totals

## Referential Integrity

- ON DELETE RESTRICT for bills/items referenced historically
- Soft-deactivate users/items/categories
- Cascades avoided for financial tables

## Improvements vs Initial Spec

| Addition | Why |
|----------|-----|
| `bill_sequence` | Reliable ordering/locking |
| `bill_number_counters` | Concurrent unique numbers |
| `parent_id` on categories | Subcategory hierarchy |
| `printed_count` | Reprint monitoring |
| `round_off` | Match Indian cash-memo totals |
| `user_name` on audit | Readable history if user renamed |
| `bill_number_prefix` on tenant | Configurable INV format |
