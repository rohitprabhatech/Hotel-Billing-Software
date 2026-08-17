# Phase 2 Sprint P2-7 — Responsive design checklist

**Date:** 2026-08-14  
**Goal:** Usable layouts at 320 / 375 / 768 / 1024 / 1280 / 1440.  
**Rule:** No horizontal **page** scroll; table scroll stays inside `TableCard`.

---

## Changes shipped

| Area | Fix |
|------|-----|
| Landing nav | Desktop links from `lg+`; hamburger through tablet (`md`) |
| Landing hero / support / pricing CTAs | Full-width on `xs`; short “Email support” label |
| Landing footer / business types | 1 → 2 → 4 column progression |
| Owner / Billing AppBar | Hide role chip below `sm`; tighter `xs` gutters |
| Auth layout | Top-align on `xs` (tall register form); submit buttons `fullWidth` |
| New Bill catalog | Stack name / price+Add on `xs` |
| Theme dialogs | Wrap actions; narrower padding; paper `maxWidth: calc(100% - 32px)` |
| TableCard | Tighter cell padding on `xs` |
| Section actions | Wrap / stretch on `xs` |
| Billing home KPIs | 4-up from `lg` (not `md`) when drawer visible |
| Bill preview | `overflowX: auto` inside dialogs |
| Charts | Narrower Y-axis + smaller ticks (Owner dashboard + Reports) |

---

## Breakpoint sign-off

| Width | Landing | Auth | App shell | Tables | Dialogs | New Bill | Charts |
|-------|---------|------|-----------|--------|---------|----------|--------|
| **320** | ✅ Nav hamburger; CTAs stack; email CTA short | ✅ Top-aligned form; full-width submit | ✅ Chip hidden; title truncates | ✅ Scroll in card | ✅ Actions wrap | ✅ Catalog stacks | ✅ Axis fits |
| **375** | ✅ Same as 320 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **768** | ✅ Hamburger (links at `lg`); footer 2-col | ✅ Centered | ✅ Temporary drawer | ✅ | ✅ | ✅ | ✅ |
| **1024** | ✅ Full desktop nav (`lg`) | ✅ | ✅ Permanent drawer | ✅ | ✅ | ✅ | ✅ |
| **1280** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **1440** | ✅ Content capped by `MAIN_MAX_WIDTH` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

Manual verification: resize browser / DevTools device mode across the widths above on `/`, `/login`, `/register`, owner dashboard, items, bills, billing new bill.

---

## Acceptance

| Criterion | Met? |
|-----------|------|
| Landing, auth, dashboards, tables, dialogs, sidebar usable | ✅ |
| No page-level horizontal scroll (table scroll OK) | ✅ |
| Checklist signed for listed breakpoints | ✅ (this file) |
