# Cafes / Tea Shops — Overview

**Business code:** `cafe_tea`  
**Documentation pack:** `docs/05-businesses/02-cafes-tea-shops/`  
**Medical Store:** Not applicable (permanently out of product scope)

## Purpose

Enable Cafes / Tea Shops tenants on Prabha Billing SaaS using the **Common Core** plus this industry pack.

## Target users

Owner, Manager, Billing User

## Business characteristics

High-speed counter billing, popular-item focus

| Aspect | Detail |
|--------|--------|
| Billing type | Quick POS + takeaway; optional dine-in tables |
| Inventory | Menu items + ingredient stock; combos/add-ons |

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

- Optional Tables / KOT
- Add-ons
- Combo offers
- Discount / coupon
- Popular-item report
- Ingredient stock

## Traceability

Requirements → Features → Modules → DB → API → UI → Tests → Roadmap phases in this folder.  
Global concept: [`../../00-project-foundation/07-requirements-traceability.md`](../../00-project-foundation/07-requirements-traceability.md).
