# Electronics Shops — Overview

**Business code:** `electronics`  
**Documentation pack:** `docs/05-businesses/09-electronics/`  
**Medical Store:** Not applicable (permanently out of product scope)

## Purpose

Enable Electronics Shops tenants on Prabha Billing SaaS using the **Common Core** plus this industry pack.

## Target users

Owner, Manager, Billing User

## Business characteristics

Warranty, installation, repair, exchange/return

| Aspect | Detail |
|--------|--------|
| Billing type | Serialized + standard product billing |
| Inventory | Serial/warranty items + accessory qty |

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

- Serial number
- Warranty tracking
- Product model / brand
- Barcode
- Exchange / Return
- Repair / service
- Installation tracking
- Customer purchase history

## Traceability

Requirements → Features → Modules → DB → API → UI → Tests → Roadmap phases in this folder.  
Global concept: [`../../00-project-foundation/07-requirements-traceability.md`](../../00-project-foundation/07-requirements-traceability.md).
