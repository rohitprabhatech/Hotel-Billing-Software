# WhatsApp Integration — Prabha Billing SaaS V2

## Use cases

Send invoice · Payment confirmation · Quotation · Booking info · Customer notices

## Flow

Billing user selects **Send on WhatsApp** → delivery attempt recorded → provider (Meta Cloud API or mock) → status webhooks (DELIVERED/READ/FAILED).

## Architecture

- Per-tenant WhatsApp config; tokens **encrypted** at rest  
- Never return raw tokens to clients  
- Industry message templates optional  

## Current baseline

`tenant_whatsapp_configs`, `bill_deliveries`, send/retry, webhooks — extend message types beyond bills.
