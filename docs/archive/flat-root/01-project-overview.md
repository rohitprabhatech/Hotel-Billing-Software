# 01 — Project Overview

## Product Name

**Hotel Billing Software** — Multi-Tenant Hotel Billing and Sales Management SaaS

## Purpose

A production-oriented billing and sales management system for food-related hotels and restaurants. The product is sold to multiple hotels; each hotel operates as an isolated **tenant**.

## Problem Statement

Hotels and restaurants need:

- Fast day-to-day billing at the counter
- Accurate GST calculations and printable cash-memo receipts
- Owner-level visibility into sales, discounts, cancellations, and staff activity
- Strict separation of data between hotels (multi-tenancy)
- Protection of historical financial records against accidental or malicious deletion

Existing basic CRUD billing tools often lack tenant isolation, audit trails, historical price snapshots, and fraud-monitoring visibility for owners.

## Target Users

| Role | Description |
|------|-------------|
| **Hotel Owner** | Full management dashboard: sales, reports, items, GST, billing users, audit/fraud monitoring |
| **Billing User** | Simplified billing interface: create bills, print, limited history |

Only these two roles exist in this version. No Manager, Admin, Accountant, or Supervisor roles.

## Product Goals

1. **Reliable billing** — Backend-authoritative calculations, atomic bill finalization, unique bill numbers
2. **Tenant isolation** — Data of Hotel A never visible or accessible to Hotel B
3. **Historical integrity** — Bills and audit logs are never hard-deleted by normal users
4. **Owner visibility** — Sales analytics, exports, and complete audit of billing-user actions
5. **Professional receipts** — Indian restaurant thermal/cash-memo style print layout
6. **Maintainable architecture** — Flask MVC + service/repository layers; React + MUI frontend

## Out of Scope (This Version)

- Online payment gateway
- Inventory / stock management
- Kitchen display system (KDS)
- Online ordering / customer portal
- Multi-branch within a tenant (beyond single hotel per tenant)
- Roles beyond OWNER and BILLING_USER
- Hard delete of finalized financial records via application UI

## Success Criteria

- Owner and Billing User can log in and use role-appropriate dashboards
- Bills are calculated on the backend with Decimal money fields
- Receipts print with hotel-configured header data (name, address, GSTIN, FSSAI)
- Cross-tenant API access always fails authorization
- Cancelled/void bills remain queryable with reason and actor
- Owner can filter audit logs and export tenant-scoped sales reports

## Technology Summary

| Layer | Stack |
|-------|-------|
| Backend | Python, Flask, Flask REST API, SQLAlchemy, Flask-Migrate, JWT |
| Frontend | React.js, Material UI, React Router, Axios |
| Database | MySQL |
| Auth | JWT + password hashing + RBAC + tenant from JWT |

## Document Map

| Doc | Topic |
|-----|-------|
| 02 | Functional requirements |
| 03 | Non-functional requirements |
| 04 | System architecture |
| 05 | Multi-tenant architecture |
| 06 | User roles & permissions |
| 07 | Database design |
| 08 | Database ERD |
| 09 | API documentation |
| 10 | Authentication & authorization |
| 11 | Billing workflow |
| 12 | Bill printing |
| 13 | Sales reporting |
| 14 | Audit & fraud monitoring |
| 15 | Frontend architecture |
| 16 | Backend architecture |
| 17 | Security |
| 18 | Testing strategy |
| 19 | Deployment |
| 20 | Development sprints |
| 21 | Production readiness |

## Development Approach

Work **sprint-by-sprint**. Sprint 1 delivers documentation only. Application code begins in Sprint 2 after architecture acceptance.
