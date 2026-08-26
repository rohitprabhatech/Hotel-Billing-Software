# Reporting System — Prabha Billing SaaS V2

## Common reports

Today / week / month / custom sales · Export (xlsx/csv/pdf) · Outstanding aging · Dashboard summary widgets

## Report registry (BIZ-61)

`GET /api/v1/reports/available` returns only reports whose **modules are enabled** for the tenant.

| id | Kind | Modules | Where |
|----|------|---------|-------|
| sales | hub | `core_reports` | Reports page |
| fb | hub | `order_channels` | Reports page |
| kirana | hub | `customer_credit` | Reports page |
| apparel | hub | `variants` | Reports page |
| mobile | hub | `serial_imei` | Reports page |
| outstanding | link | `customer_credit` | `/owner/outstanding` |
| travel_commission | link | `travel_commission` | `/owner/travel-agents` |
| tour_packages | link | `tour_packages` | `/owner/tour-packages` |
| travel_bookings | link | `travel_bookings` | `/owner/travel-bookings` |

Catalog source: `backend/app/constants/report_registry.py` — add entries only when an API/UI already exists.

## Perf guards

- Custom date range max **366** days (`MAX_CUSTOM_RANGE_DAYS`)
- Bills list paginated (`page` / `per_page`, default 50, max 200) with `bills_meta`
- Existing index: `ix_bills_tenant_status_created_at` on `(tenant_id, status, created_at)`

## Industry reports (examples)

| Industry | Reports |
|----------|---------|
| Restaurant | Food sales, table sales, KOT, wastage |
| Cafe | Popular menu, ingredient usage |
| Grocery | Fast movers, expiry/stock |
| Clothing | Size/color/brand sales |
| Mobile | IMEI stock, warranty |
| Wholesale | Customer/supplier outstanding, warehouse |
| Travel | Bookings, packages, commission, pending payments |

## Principles

- Tenant-scoped queries only  
- Export where useful (existing report export)  
- Dashboard widgets are a subset of report metrics  
- AI consumes the same scoped aggregates — no invented numbers
- Module-aware registry — avoid 14 isolated report apps
