# Hotels / Restaurants — Testing

| Test ID | Purpose | Precondition | Steps (summary) | Expected | Priority |
|---------|---------|--------------|-----------------|----------|----------|
| TEST-REST-001 | Create table | Tenant type=hotel_restaurant; user logged in | Execute create table | Table appears Available | P0 |
| TEST-REST-002 | Occupy table | Tenant type=hotel_restaurant; user logged in | Execute occupy table | Status Occupied | P0 |
| TEST-REST-003 | Create KOT | Tenant type=hotel_restaurant; user logged in | Execute create kot | Kitchen receives ticket | P0 |
| TEST-REST-004 | Complete order → bill | Tenant type=hotel_restaurant; user logged in | Execute complete order → bill | Bill created from order | P0 |
| TEST-REST-005 | Inventory deduction | Tenant type=hotel_restaurant; user logged in | Execute inventory deduction | Recipe/stock reduced | P0 |
| TEST-REST-006 | Prevent negative stock | Tenant type=hotel_restaurant; user logged in | Execute prevent negative stock | Bill blocked if insufficient | P0 |
| TEST-REST-007 | Split bill | Tenant type=hotel_restaurant; user logged in | Execute split bill | Two invoices from one order | P0 |
| TEST-REST-008 | Merge tables | Tenant type=hotel_restaurant; user logged in | Execute merge tables | Orders combined | P0 |
| TEST-REST-009 | Track wastage | Tenant type=hotel_restaurant; user logged in | Execute track wastage | Wastage entry + stock impact | P0 |
| TEST-REST-010 | Cross-tenant table ID | Tenant type=hotel_restaurant; user logged in | Execute cross-tenant table id | 403/404 | P0 |

## Isolation

| TEST-REST-ISO-001 | Use Tenant A token on Tenant B industry IDs | 403 or 404 | P0 |

Do not run destructive tests on production data.

## Automated gate (BIZ-19)

Run the full F&B pytest gate from `backend/`:

```bash
python -m pytest tests/test_biz11_restaurant_foundation.py tests/test_biz12_table_management.py tests/test_biz13_order_channels.py tests/test_biz14_kot_kitchen_dashboard.py tests/test_biz15_restaurant_billing.py tests/test_biz16_recipe_ingredient_stock.py tests/test_biz17_cafe_pack.py tests/test_biz18_fb_reports_wastage.py tests/test_biz19_restaurant_cafe_testing_gate.py -q
```

See [../../14-sprints/biz-19-restaurant-cafe-gate-report.md](../../14-sprints/biz-19-restaurant-cafe-gate-report.md).
