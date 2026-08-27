# Alembic Revision Order

**Head:** `20260827_cafe_coupons`  
**Count:** 59 (single linear chain)

Regenerate:

```powershell
cd backend
.\.venv\Scripts\python.exe scripts\print_alembic_chain.py
```

| # | Revision ID | File |
|--:|-------------|------|
| 1 | `20260326_saas_auth` | `20260326_saas_auth_tokens.py` |
| 2 | `20260326_item_created_by` | `20260326_item_created_by.py` |
| 3 | `20260326_bill_payment_method` | `20260326_bill_payment_method.py` |
| 4 | `20260814_tenant_business_type` | `20260814_tenant_business_type.py` |
| 5 | `20260814_schema_rel_fixes` | `20260814_schema_relationship_fixes.py` |
| 6 | `20260814_item_catalog_fields` | `20260814_item_catalog_fields.py` |
| 7 | `20260814_category_parent_key` | `20260814_category_parent_key.py` |
| 8 | `20260814_bill_report_index` | `20260814_bill_report_index.py` |
| 9 | `20260814_stock_notifications` | `20260814_stock_notifications.py` |
| 10 | `20260814_whatsapp_bill` | `20260814_whatsapp_bill_delivery.py` |
| 11 | `20260814_users_email_unique` | `20260814_users_email_unique.py` |
| 12 | `20260814_wa_webhook_status` | `20260814_whatsapp_webhook_statuses.py` |
| 13 | `20260818_phase8_saas` | `20260818_phase8_saas.py` |
| 14 | `20260820_biz01_business_types` | `20260820_biz01_business_types.py` |
| 15 | `20260822_biz03_manager_role` | `20260822_biz03_manager_role.py` |
| 16 | `20260822_biz04_customers` | `20260822_biz04_customers.py` |
| 17 | `20260822_biz05_suppliers` | `20260822_biz05_suppliers.py` |
| 18 | `20260822_biz06_purchases` | `20260822_biz06_purchases.py` |
| 19 | `20260822_biz07_expenses` | `20260822_biz07_expenses.py` |
| 20 | `20260822_biz08_barcode_uom` | `20260822_biz08_barcode_uom.py` |
| 21 | `20260822_biz09_party_ledger` | `20260822_biz09_party_ledger.py` |
| 22 | `20260822_biz11_restaurant_menu` | `20260822_biz11_restaurant_menu.py` |
| 23 | `20260822_biz12_dining_tables` | `20260822_biz12_dining_tables.py` |
| 24 | `20260822_biz13_orders` | `20260822_biz13_orders.py` |
| 25 | `20260822_biz14_kots` | `20260822_biz14_kots.py` |
| 26 | `20260822_biz15_restaurant_billing` | `20260822_biz15_restaurant_billing.py` |
| 27 | `20260822_biz16_recipes` | `20260822_biz16_recipes.py` |
| 28 | `20260822_biz17_cafe_addons_combos` | `20260822_biz17_cafe_addons_combos.py` |
| 29 | `20260822_biz18_fb_reports_wastage` | `20260822_biz18_fb_reports_wastage.py` |
| 30 | `20260824_biz21_item_price_tiers` | `20260824_biz21_item_price_tiers.py` |
| 31 | `20260824_biz22_item_batches` | `20260824_biz22_item_batches.py` |
| 32 | `20260825_biz25_item_variants` | `20260825_biz25_item_variants.py` |
| 33 | `20260825_biz26_item_images` | `20260825_biz26_item_images.py` |
| 34 | `20260825_biz27_sales_returns` | `20260825_biz27_sales_returns.py` |
| 35 | `20260825_biz29_serial_units` | `20260825_biz29_serial_units.py` |
| 36 | `20260825_audit_db_hardening` | `20260825_audit_db_hardening.py` |
| 37 | `20260825_biz30_warranty_accessories` | `20260825_biz30_warranty_accessories.py` |
| 38 | `20260825_biz31_repairs_serial_exchange` | `20260825_biz31_repairs_serial_exchange.py` |
| 39 | `20260825_biz32_mobile_brand_model` | `20260825_biz32_mobile_brand_model.py` |
| 40 | `20260825_biz33_installation_orders` | `20260825_biz33_installation_orders.py` |
| 41 | `20260825_biz35_sale_uom_measurement` | `20260825_biz35_sale_uom_measurement.py` |
| 42 | `20260825_biz36_quotations_delivery_challans` | `20260825_biz36_quotations_delivery_challans.py` |
| 43 | `20260825_biz37_transport_supplier_credit` | `20260825_biz37_transport_supplier_credit.py` |
| 44 | `20260825_biz38_warehouse_stock_foundation` | `20260825_biz38_warehouse_stock_foundation.py` |
| 45 | `20260825_biz40_bakery_production_runs` | `20260825_biz40_bakery_production_runs.py` |
| 46 | `20260825_biz42_custom_product_orders` | `20260825_biz42_custom_product_orders.py` |
| 47 | `20260826_biz45_book_store_metadata` | `20260826_biz45_book_store_metadata.py` |
| 48 | `20260826_biz47_furniture_product_attributes` | `20260826_biz47_furniture_product_attributes.py` |
| 49 | `20260826_biz49_furniture_delivery_tracking` | `20260826_biz49_furniture_delivery_tracking.py` |
| 50 | `20260826_biz51_wholesale_price_lists` | `20260826_biz51_wholesale_price_lists.py` |
| 51 | `20260826_biz52_sales_purchase_orders` | `20260826_biz52_sales_purchase_orders.py` |
| 52 | `20260826_biz56_tour_packages` | `20260826_biz56_tour_packages.py` |
| 53 | `20260826_biz57_travel_bookings` | `20260826_biz57_travel_bookings.py` |
| 54 | `20260826_biz58_travel_itinerary_documents` | `20260826_biz58_travel_itinerary_documents.py` |
| 55 | `20260826_biz59_travel_agent_commission` | `20260826_biz59_travel_agent_commission.py` |
| 56 | `20260826_biz66_perf_indexes` | `20260826_biz66_perf_indexes.py` |
| 57 | `20260827_hotel_billing_settings_audit_delete` | `20260827_hotel_billing_settings_audit_delete.py` |
| 58 | `20260827_stock_movement_sources` | `20260827_stock_movement_sources.py` |
| 59 | `20260827_cafe_coupons` | `20260827_cafe_coupons.py` |

Ops runbook: [`10-industry-modules-ops-runbook.md`](./10-industry-modules-ops-runbook.md)
