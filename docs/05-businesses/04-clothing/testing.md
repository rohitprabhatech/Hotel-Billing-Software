# Clothing Shops — Testing

| Test ID | Purpose | Precondition | Steps (summary) | Expected | Priority |
|---------|---------|--------------|-----------------|----------|----------|
| TEST-CLTH-001 | Create variant | Tenant type=clothing | POST `/items/:id/variants` | Size+color stock row; first variant may inherit item stock | P0 |
| TEST-CLTH-002 | Unique size+color | Clothing tenant | Duplicate size+color | 409 | P0 |
| TEST-CLTH-003 | Sell variant | Clothing tenant | Bill with `variant_id` | Only that variant stock reduces | P0 |
| TEST-CLTH-004 | Missing/wrong variant | Clothing tenant | Bill without variant or other item's id | 400 | P0 |
| TEST-CLTH-005 | Cancel restock | Clothing tenant | Cancel bill | Variant qty restored | P0 |
| TEST-CLTH-006 | Isolation | Two clothing tenants | Tenant B reads Tenant A variants | 403/404 | P0 |
| TEST-CLTH-007 | Restaurant gate | Restaurant tenant | GET variants | 403 | P0 |
| TEST-CLTH-010 | Image URL | Clothing tenant | POST images with https URL | 201; restaurant 403 | P0 |
| TEST-CLTH-011 | POS catalog stock | Clothing tenant | GET `/clothing/pos-catalog` | Size/color qty shown | P0 |
| TEST-CLTH-012 | Selected variant sale | Clothing tenant | Bill selected cell | Only that stock reduces; oversell 400 | P0 |
| TEST-CLTH-013 | Return restock | Clothing tenant | POST `/returns` RETURN | Correct variant qty restored | P0 |
| TEST-CLTH-014 | Exchange swap | Clothing tenant | POST EXCHANGE | Old in, new out | P0 |
| TEST-CLTH-015 | Billing limited | Billing user | POST `/returns` | 403 | P0 |
| TEST-CLTH-009 | Brand report | Clothing tenant | GET `/clothing/sales` | Nike vs Adidas revenue split; restaurant 403 | P0 |
| TEST-CLTH-016 | Size / category dims | Clothing tenant | GET `/clothing/sales` | Size and category rows match bills | P0 |
| TEST-CLTH-017 | Customer history | Clothing tenant | GET `/clothing/customer-history` | Bills include `variant_id` lines | P0 |
| TEST-CLTH-018 | Report isolation | Two clothing tenants | Tenant B sales | Tenant A brand absent | P0 |

Automated: `backend/tests/test_biz25_clothing_variants.py`, `backend/tests/test_biz26_clothing_images_pos.py`, `backend/tests/test_biz27_clothing_returns.py`, `backend/tests/test_biz28_clothing_reports_and_testing_gate.py`.

Phase gate (from `backend/`):

```bash
python -m pytest tests/test_biz25_clothing_variants.py tests/test_biz26_clothing_images_pos.py tests/test_biz27_clothing_returns.py tests/test_biz28_clothing_reports_and_testing_gate.py tests/test_clth_billing_polish_gate.py -q
```

Billing polish gate (CLTH-6): [`../../14-sprints/clth-6-billing-polish-gate-report.md`](../../14-sprints/clth-6-billing-polish-gate-report.md).

Sign-off: [`../../14-sprints/biz-28-clothing-gate-report.md`](../../14-sprints/biz-28-clothing-gate-report.md).

## Isolation

| TEST-CLTH-ISO-001 | Use Tenant A token on Tenant B industry IDs | 403 or 404 | P0 |

Do not run destructive tests on production data.
