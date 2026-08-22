# Grocery Stores / Kirana — Overview

**Business code:** `grocery_kirana`  
**Documentation pack:** `docs/05-businesses/03-grocery-kirana/`  
**Medical Store:** Not applicable (permanently out of product scope)

## Purpose

Enable Grocery Stores / Kirana tenants on Prabha Billing SaaS using the **Common Core** plus this industry pack.

## Target users

Owner, Manager, Billing User

## Business characteristics

High SKU count, credit/udhari, bulk pricing

| Aspect | Detail |
|--------|--------|
| Billing type | Fast POS product billing; barcode-driven |
| Inventory | Units (kg/g/L/piece), batch/expiry, low-stock |

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

- Barcode scanner flow
- Unit management (kg, g, L, piece)
- Low-stock alerts
- Stock adjustment
- Customer credit / Udhari
- Customer payment history
- Bulk pricing
- Expiry tracking (generic inventory)
- Fast POS billing

## Traceability

Requirements → Features → Modules → DB → API → UI → Tests → Roadmap phases in this folder.  
Global concept: [`../../00-project-foundation/07-requirements-traceability.md`](../../00-project-foundation/07-requirements-traceability.md).
