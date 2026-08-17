# Sprint Plan — P3-4 WhatsApp delivery polish

**Date:** 2026-08-14  
**Status:** Completed  
**Sprint ID:** P3-4

## Scope (residuals from P3-3)

1. Rate-limit `POST /bills/:id/send-whatsapp` (20/min)
2. Include recent `deliveries[]` on bill detail (masked phones)
3. Bills history: phone dialog when sending without stored number
4. Audit filters + descriptions for `BILL_SENT_WHATSAPP` / `BILL_WHATSAPP_FAILED`
5. Meta Cloud API owner setup notes in docs

## Non-goals

- Live Meta webhooks, unofficial WhatsApp, changing print engine
