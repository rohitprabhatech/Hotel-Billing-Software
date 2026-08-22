# Stationery Shops — Overview

**Business code:** `stationery`  
**Documentation pack:** `docs/05-businesses/08-stationery/`  
**Medical Store:** Not applicable (permanently out of product scope)

## Purpose

Enable Stationery Shops tenants on Prabha Billing SaaS using the **Common Core** plus this industry pack.

## Target users

Owner, Manager, Billing User

## Business characteristics

Retail counter, search-heavy catalog

| Aspect | Detail |
|--------|--------|
| Billing type | Fast POS with barcode/SKU |
| Inventory | High SKU, brand/category, low-stock, bulk pricing |

## Typical workflow

See [workflow.md](./workflow.md).

## Common modules reused

- Authentication
- Authorization
- Billing Engine
- Customers
- Payments
- Inventory (generic)
- Categories / Products
- Reports (common)
- Notifications
- Audit Logs
- Printing / PDF
- WhatsApp (optional)
- AI Assistant (optional)
- Settings

> Billing details live in [`../../04-common-modules/billing.md`](../../04-common-modules/billing.md). This pack only documents **extensions**.

## Industry-specific modules / features

- Barcode / SKU
- Brand management
- Category management
- Bulk pricing
- Low-stock alerts
- Customer credit
- Fast POS billing
- Product search

## Traceability

Requirements → Features → Modules → DB → API → UI → Tests → Roadmap phases in this folder.  
Global concept: [`../../00-project-foundation/07-requirements-traceability.md`](../../00-project-foundation/07-requirements-traceability.md).
