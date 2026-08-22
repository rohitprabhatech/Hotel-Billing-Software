# Travel Agencies — Overview

**Business code:** `travel_agency`  
**Documentation pack:** `docs/05-businesses/14-travel-agencies/`  
**Medical Store:** Not applicable (permanently out of product scope)

## Purpose

Enable Travel Agencies tenants on Prabha Billing SaaS using the **Common Core** plus this industry pack.

## Target users

Owner, Manager, Billing User / Agent

## Business characteristics

Bookings, advances, itineraries, commissions — not traditional inventory POS

| Aspect | Detail |
|--------|--------|
| Billing type | Service-first (packages/bookings); mixed product optional |
| Inventory | Usually none; optional merchandise light stock |

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

- Tour package management
- Package pricing
- Booking management
- Advance / remaining payment
- Booking status
- Hotel / vehicle / ticket details
- Customer documents
- Travel itinerary
- Agent / commission management

## Traceability

Requirements → Features → Modules → DB → API → UI → Tests → Roadmap phases in this folder.  
Global concept: [`../../00-project-foundation/07-requirements-traceability.md`](../../00-project-foundation/07-requirements-traceability.md).
