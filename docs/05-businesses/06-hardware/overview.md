# Hardware Stores — Overview

**Business code:** `hardware`  
**Documentation pack:** `docs/05-businesses/06-hardware/`  
**Medical Store:** Not applicable (permanently out of product scope)

## Purpose

Enable Hardware Stores tenants on Prabha Billing SaaS using the **Common Core** plus this industry pack.

## Target users

Owner, Manager, Billing User

## Business characteristics

Trade counters, credit, price history

| Aspect | Detail |
|--------|--------|
| Billing type | Unit/weight/length based product billing |
| Inventory | Multi-unit stock; bulk quantity; brand variants |

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

- Unit management
- Weight / length based products
- Bulk quantity
- Brand management
- Product variants
- Low-stock alerts
- Customer / supplier credit
- Price history

## Traceability

Requirements → Features → Modules → DB → API → UI → Tests → Roadmap phases in this folder.  
Global concept: [`../../00-project-foundation/07-requirements-traceability.md`](../../00-project-foundation/07-requirements-traceability.md).
