# Cafes / Tea Shops — Testing

| Test ID | Purpose | Precondition | Steps (summary) | Expected | Priority |
|---------|---------|--------------|-----------------|----------|----------|
| TEST-CAFE-001 | Quick bill with add-on | Tenant type=cafe_tea; user logged in | Execute quick bill with add-on | Line totals correct | P0 |
| TEST-CAFE-002 | Combo pricing | Tenant type=cafe_tea; user logged in | Execute combo pricing | Bundle price applied | P0 |
| TEST-CAFE-003 | Coupon discount | Tenant type=cafe_tea; user logged in | Execute coupon discount | Validation rules | P0 |
| TEST-CAFE-004 | Stock deduction | Tenant type=cafe_tea; user logged in | Execute stock deduction | Ingredients/items reduced | P0 |
| TEST-CAFE-005 | Insufficient stock | Tenant type=cafe_tea; user logged in | Execute insufficient stock | Blocked with available qty | P0 |
| TEST-CAFE-006 | Optional KOT | Tenant type=cafe_tea; user logged in | Execute optional kot | Appears when enabled | P0 |
| TEST-CAFE-007 | Cross-tenant | Tenant type=cafe_tea; user logged in | Execute cross-tenant | 403/404 | P0 |

## Isolation

| TEST-CAFE-ISO-001 | Use Tenant A token on Tenant B industry IDs | 403 or 404 | P0 |

Do not run destructive tests on production data.

## Automated gate (BIZ-19)

Same pytest gate as restaurant — cafe scenarios covered in `test_biz17_cafe_pack.py` and `test_biz19_restaurant_cafe_testing_gate.py`. See [../../14-sprints/biz-19-restaurant-cafe-gate-report.md](../../14-sprints/biz-19-restaurant-cafe-gate-report.md).
