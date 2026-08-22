# Subscription Notifications

# Notification System — Prabha Billing SaaS V2

## Architecture

Generic notification service + typed events. Avoid hard-coded one-off alerts without a type registry.

## Channels

| Channel | Audience |
|---------|----------|
| In-app tenant notifications | Owner / Billing |
| Platform notifications | Master |
| Email | Optional (SMTP) |
| WhatsApp | Optional (configured tenant) |

## Example events

Low stock · Subscription expiring/expired · Payment pending · Important audit · System · Booking due (travel) · Custom order due (bakery/furniture)

## Low stock

If quantity ≤ configured minimum → notify Owner and Billing dashboards.

## Rules

Configurable thresholds in BusinessSettings; respect tenant isolation; Master expiry alerts for all tenants.
