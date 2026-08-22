# AI Business Assistant — Prabha Billing SaaS V2

## Goal

Generic, tenant-scoped decision support — **not** restaurant-only.

## Inputs (examples)

Today/week/month/year sales · Top/slow movers · Customer trends · Revenue · Stock · Expenses · Payments · Industry metrics (brands, IMEI, packages, …)

## Outputs

Insights and suggested actions. Must not fabricate metrics not backed by tenant data (current product rule — keep).

## Isolation

AI must never mix or reveal another tenant’s data. Master Admin does not get pooled tenant AI that leaks identities without policy.

## Current baseline

`/ai/analysis`, `/ai/decisions`, Owner AI page. Broaden prompts/metrics as industry data appears.
