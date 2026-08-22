# Mobile Shops — Overview

**Business code:** `mobile`  
**Documentation pack:** `docs/05-businesses/05-mobile-shops/`  
**Medical Store:** Not applicable (permanently out of product scope)

## Purpose

Enable Mobile Shops tenants on Prabha Billing SaaS using the **Common Core** plus this industry pack.

## Target users

Owner, Manager, Billing User

## Business characteristics

Warranty, exchange, repair/service tracking

| Aspect | Detail |
|--------|--------|
| Billing type | Serialized product billing (IMEI) + accessories |
| Inventory | IMEI/serial unique stock; accessories qty stock |

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

- IMEI number
- Serial number
- Mobile model / brand
- Warranty tracking
- Accessories management
- Mobile exchange
- Repair / service tracking
- Customer purchase history
- Stock by IMEI

## Traceability

Requirements → Features → Modules → DB → API → UI → Tests → Roadmap phases in this folder.  
Global concept: [`../../00-project-foundation/07-requirements-traceability.md`](../../00-project-foundation/07-requirements-traceability.md).
