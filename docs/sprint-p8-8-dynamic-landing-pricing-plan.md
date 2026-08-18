# Sprint Plan — P8-8 Dynamic landing page pricing

**Date:** 2026-08-18  
**Status:** Completed  
**Phase:** 8 — Master Admin + SaaS subscription management  
**Branch:** `rs/feature/master-dashboard-18-8-26`

## Scope

- Anonymous `GET /public/plans` endpoint for active public plans only
- Landing hero and pricing section consume live plan data from the API
- Multiple public plans can appear without a frontend code edit
- Public legal copy no longer hardcodes a specific INR amount

## Non-goals

- Online checkout or payment gateway
- Owner/Billing dashboard redesign
- Changing how plan assignment / renewal works internally
