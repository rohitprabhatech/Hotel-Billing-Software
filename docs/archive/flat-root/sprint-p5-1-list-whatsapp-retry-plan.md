# Sprint Plan — P5-1 List-level WhatsApp retry

**Date:** 2026-08-16  
**Status:** Completed  
**Phase:** 5 — Multi-channel bill reach  
**Product:** Business Billing

---

## Phase 5 goal

Get finalized bills to customers reliably across channels — finish WhatsApp ops UX, then add email (later), without inventory or SaaS checkout rebuilds.

## P5-1 Scope

1. Bills history row action: Retry / Send WhatsApp for finalized bills.
2. Phone-missing dialog from the list (same as detail).
3. Owner + Billing lists share `BillsHistoryPage` (parity automatic).
4. In-flight disable + success/error feedback; refresh chips after send.
5. Docs + FE build; reuse existing `POST /bills/:id/send-whatsapp`.

## Non-goals

- Email/SMS, bulk resend, inventory.
