# Clothing Shops — Overview

**Business code:** `clothing`  
**Documentation pack:** `docs/05-businesses/04-clothing/`  
**Medical Store:** Not applicable (permanently out of product scope)

## Purpose

Enable Clothing Shops tenants on Prabha Billing SaaS using the **Common Core** plus this industry pack.

## Target users

Owner, Manager, Billing User

## Business characteristics

Fashion variants, brand analytics, exchange/return

| Aspect | Detail |
|--------|--------|
| Billing type | Variant-based product billing (size/color) |
| Inventory | Size-wise and color-wise stock; SKU/barcode |

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

- Size management (S–XXL)
- Color management
- Brand management
- Barcode / SKU
- Product images
- Size-wise / color-wise stock
- Exchange / Return
- Sales by brand / category
- Customer purchase history

## Traceability

Requirements → Features → Modules → DB → API → UI → Tests → Roadmap phases in this folder.  
Global concept: [`../../00-project-foundation/07-requirements-traceability.md`](../../00-project-foundation/07-requirements-traceability.md).
