# Subscription Requirements

# Subscription System — Prabha Billing SaaS V2

## Purpose

SaaS commercial control for Prabha Technology — **separate** from a shop’s customer payment collection.

## States

`PENDING` · `TRIAL` · `ACTIVE` · `EXPIRING` · `EXPIRED` · `CANCELLED` · `SUSPENDED`

`EXPIRING` may be derived (warning window) rather than stored.

## Master capabilities

Create/edit/deactivate plans; monthly price; features; visibility; trial eligibility; **limits** (users, products, invoices, branches, reports, storage — enforce gradually).

## Landing

`GET /public/plans` drives pricing — do not hard-code ₹550 in UI long-term (informational constant may remain until fully dynamic).

## Entitlement

Expired/cancelled/suspended subscription → billing APIs **402**; login may still work unless tenant deactivated.

## Payments

SaaS fee collection may remain **offline / contact** until a gateway sprint is approved. Manual renew exists today.
