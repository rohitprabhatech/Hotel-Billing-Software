# Module / Feature Matrix (BIZ-02)

**Source of truth (runtime):** `backend/app/constants/modules.py`  
**Resolve API:** `GET /api/v1/tenants/me/modules`  
**Guard helper:** `@module_required("…")` in `backend/app/utils/module_access.py`

## Design

```
COMMON PLATFORM
+ business_type defaults (this sprint)
+ optional tenant overrides (later — not enabled yet)
+ industry module implementations (later sprints)
```

- Defaults are **code-defined** per the 14 business types (no hard-coded `if business_type ==` in UI/API beyond the matrix).
- Tenant / Master overrides are **reserved** (`overrides: []` in API). Optional future tables:
  - `business_type_module_defaults` (DB-backed matrix)
  - `tenant_module_overrides` (per-tenant enable/disable with audit)

## Core modules (all 14 types)

| Code | Label |
|---|---|
| `core_billing` | Billing |
| `core_catalog` | Products & Categories |
| `core_inventory` | Inventory & Stock |
| `core_reports` | Sales Reports |
| `core_users` | Users |
| `core_audit` | Audit Logs |
| `core_ai` | AI Assistant |
| `core_settings` | Settings |

## Industry modules (examples)

| Module | Hotels/Rest. | Cafe | Grocery | Clothing | Mobile | … |
|---|---|---|---|---|---|---|
| `restaurant_menu` | ✅ | ✅ | | | | |
| `table_management` | ✅ | ✅ | | | | |
| `kot` / `kitchen` | ✅ | ✅ | | | | |
| `variants` | | | | ✅ | | hardware also |
| `serial_imei` | | | | | ✅ | electronics |
| `barcode_pos` | | | ✅ | ✅ | | stationery, books, wholesale |
| `customer_credit` | | | ✅ | | | hardware, wholesale, … |
| `tour_packages` | | | | | | travel_agency |

Full per-type sets live in `modules.py` (`_BUSINESS_TYPE_INDUSTRY`).

## API behavior

| Call | Enabled | Disabled |
|---|---|---|
| `GET /tenants/me/modules` | Lists all modules with `enabled` flags | — |
| `GET /tables` (stub) | 200 empty list | **403** FORBIDDEN |
| `GET /item-variants` (stub) | 200 empty list | **403** FORBIDDEN |

## Frontend

- `ModulesProvider` + `useModules()` / `useModuleGate(code)`
- Owner / Billing nav items may set `module: 'table_management'` etc.; disabled modules are hidden.
- Placeholder pages under `/owner/tables`, `/owner/variants`, `/billing/tables`.

## Medical Store

Permanently excluded — no medical modules in the catalog.
