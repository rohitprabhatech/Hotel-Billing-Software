# Sprint Plan — P5-2 Email PDF bill delivery

**Date:** 2026-08-16  
**Status:** Completed  
**Phase:** 5 — Multi-channel bill reach  

---

## Scope

1. Schema: `bills.customer_email`; `bill_deliveries` method `EMAIL` + recipient email columns.
2. `EmailBillService` + `POST /bills/:id/send-email` (PDF attach via EmailService; mock via `MAIL_SUPPRESS_SEND`).
3. Persist delivery SENT/FAILED; audits `BILL_SENT_EMAIL` / `BILL_EMAIL_FAILED`.
4. FE: Send email from New Bill + Bills history (detail + list); email prompt if missing.
5. Tests + docs; register apply script.

## Non-goals

- SMS, email open tracking, delivery KPIs for email, inventory.
