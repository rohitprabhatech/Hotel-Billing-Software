# Sprint BIZ-67 – Industry Modules Migration and Ops Runbook

## Objective

Document Alembic migration order, feature flag rollout, rollback; never full 02_schema.sql on live.

## Status

COMPLETED

## Phase

Phase 14 – Production Readiness

## Delivered

- Ops runbook: `docs/03-database/10-industry-modules-ops-runbook.md`
- Ordered list: `docs/03-database/11-alembic-revision-order.md` (56 revisions → `20260826_biz66_perf_indexes`)
- Helpers: `scripts/print_alembic_chain.py`, `scripts/stamp_alembic_industry_head.py`
- Staging dry-run checklist + per–business-type rollout (module flags via `business_type`)
- Repo dry-run test: `tests/test_biz67_migration_ops_runbook.py`

## Acceptance Criteria

- Runbook reviewed (checklist signed in runbook + status changelog)

## Dependencies

BIZ-66
