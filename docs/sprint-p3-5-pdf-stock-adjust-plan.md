# Sprint Plan — P3-5 Bill PDF parity + stock ops hardening

**Date:** 2026-08-14  
**Status:** Completed  
**Sprint ID:** P3-5

## Scope

1. `GET /bills/:id/pdf` — same saved-bill PDF as WhatsApp  
2. FE Download PDF next to Print / WhatsApp  
3. `POST /items/:id/adjust-stock` (± delta + reason + row lock + audit)  
4. Items page Adjust Stock dialog  
5. ErrorBoundary on auth + print routes  
6. Document MySQL `FOR UPDATE` stock locking (SQLite cannot prove races)

## Non-goals

Meta webhooks, email/SMS, replacing thermal HTML print, full inventory module
