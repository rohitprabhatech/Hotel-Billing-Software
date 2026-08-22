# Hardware / Building Material — Overview

**Business code:** `building_material`  
**Documentation pack:** `docs/05-businesses/11-building-material/`  
**Medical Store:** Not applicable (permanently out of product scope)

## Purpose

Enable Hardware / Building Material tenants on Prabha Billing SaaS using the **Common Core** plus this industry pack.

## Target users

Owner, Manager, Billing User

## Business characteristics

Quotations, challans, credit, transport

| Aspect | Detail |
|--------|--------|
| Billing type | Measured/bulk trade billing + transport charges |
| Inventory | Multi-unit, warehouse stock, transfers |

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

- Multiple units
- Weight / length / area
- Bulk pricing
- Quotation
- Delivery challan
- Customer / supplier credit
- Transport charges
- Delivery management
- Warehouse stock
- Price history

## Traceability

Requirements → Features → Modules → DB → API → UI → Tests → Roadmap phases in this folder.  
Global concept: [`../../00-project-foundation/07-requirements-traceability.md`](../../00-project-foundation/07-requirements-traceability.md).
