# Wholesale Shops — Testing

## Automated (BIZ-51)

Suite: `backend/tests/test_biz51_wholesale_price_lists.py` (7 passed, 2026-08-26)

| Test | Covers |
|------|--------|
| `test_restaurant_price_lists_forbidden` | 403 without module |
| `test_wholesale_module_has_price_lists` | module matrix |
| `test_price_resolution_customer_over_wholesale_over_retail` | 75 < 85 < 100 on bills |
| `test_bulk_tier_applies_when_no_list_price` | tier fallback |
| `test_pos_catalog_includes_list_price_for_customer` | catalog `base_price` |
| `test_billing_cannot_create_price_list` | permissions |
| `test_price_list_cross_tenant_isolation` | 404 |

## Automated (BIZ-52)

Suite: `backend/tests/test_biz52_sales_purchase_orders.py` (5 passed, 2026-08-26)

| Test | Covers |
|------|--------|
| `test_restaurant_so_po_forbidden` | 403 |
| `test_sales_order_convert_to_bill` | SO-##### → bill; stock ↓ |
| `test_purchase_order_convert_to_purchase` | PO-##### → purchase; stock ↑ |
| `test_so_po_cross_tenant_isolation` | 404 |
| `test_cannot_convert_cancelled_sales_order` | 400 |

## Manual smoke

| Test ID | Purpose | Expected | Priority |
|---------|---------|----------|----------|
| TEST-WHL-001 | Create default wholesale list | Saved; default chip | P0 |
| TEST-WHL-002 | Set item price on list | Matrix saved | P0 |
| TEST-WHL-003 | Assign customer to VIP list | Assignment row | P0 |
| TEST-WHL-004 | Bill walk-in vs assigned customer | Different unit prices | P0 |
| TEST-WHL-005 | POS customer picker updates cart price | base_price changes | P1 |
| TEST-WHL-010 | Create SO; convert to bill | SO CONVERTED; stock decreases | P0 |
| TEST-WHL-011 | Create PO; convert to purchase | PO CONVERTED; stock increases | P0 |
| TEST-WHL-020 | Create second warehouse; transfer stock | Balances move; item total unchanged | P0 |
| TEST-WHL-021 | Bill with warehouse picker (POS / New Bill) | Deducts from selected WH only | P0 |
| TEST-WHL-030 | Outstanding report aging buckets | 0–30 / 31–60 / 61–90 / 90+ | P0 |
| TEST-WHL-031 | Print tax invoice PDF | Title TAX INVOICE when GST | P1 |
| TEST-WHL-032 | Create delivery challan; download PDF | Challan PDF opens | P1 |

## Automated (BIZ-53)

Suite: `backend/tests/test_biz53_wholesale_warehouse.py` (5 passed, 2026-08-26)

| Test | Covers |
|------|--------|
| `test_wholesale_module_has_warehouse` | module matrix |
| `test_wholesale_warehouse_aliases_and_default_seed` | `/wholesale/warehouses` + MAIN seed |
| `test_wholesale_sell_from_selected_warehouse` | transfer + bill `warehouse_id` |
| `test_transfer_rejects_insufficient_source_before_any_move` | pre-validation; no partial move |
| `test_warehouse_low_stock_notification_on_sale` | `WAREHOUSE_STOCK` LOW_STOCK |

## Automated (BIZ-54)

Suite: `backend/tests/test_biz54_wholesale_outstanding.py` (4 passed, 2026-08-26)

| Test | Covers |
|------|--------|
| `test_aged_outstanding_buckets_customer_and_supplier` | 0–30 + 61–90 + supplier |
| `test_fifo_payment_reduces_oldest_bucket` | FIFO + wholesale alias |
| `test_wholesale_challan_alias_and_tax_invoice_pdf` | challan PDF + TAX INVOICE |
| `test_billing_user_cannot_access_outstanding_report` | Owner/Manager only |

## Automated (BIZ-55 gate)

Full Phase 10 matrix (2026-08-26): **28 passed**

```bash
python -m pytest tests/test_biz51_wholesale_price_lists.py \
  tests/test_biz52_sales_purchase_orders.py \
  tests/test_biz53_wholesale_warehouse.py \
  tests/test_biz54_wholesale_outstanding.py \
  tests/test_biz55_wholesale_testing_gate.py -q
```

Gate report: [`../../14-sprints/biz-55-wholesale-gate-report.md`](../../14-sprints/biz-55-wholesale-gate-report.md)  
Manual checklist: [`../../14-sprints/biz-55-manual-frontend-checklist.md`](../../14-sprints/biz-55-manual-frontend-checklist.md)

Do not run destructive tests on production data.
