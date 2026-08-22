# Sprint Plan — P4-3 Failed delivery ops visibility

**Date:** 2026-08-16  
**Status:** Completed  
**Product:** Business Billing

---

## Scope

1. In-app notification type `WHATSAPP_DELIVERY_FAILED` on send failure and webhook/simulator FAILED (dedupe by delivery id).
2. Owner dashboard strip for unread WhatsApp delivery failures → Bills with `whatsapp_status=FAILED`.
3. Notification bell click navigates to filtered Bills; Bills history honors URL query.
4. Optional Billing home one-liner for failed WhatsApp deliveries.
5. Tests + completion report + roadmap update.

## Non-goals

- Email/SMS, delivery analytics KPIs, bulk auto-resend, inventory.
