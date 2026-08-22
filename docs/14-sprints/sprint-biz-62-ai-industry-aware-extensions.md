# Sprint BIZ-62 – AI Industry-Aware Extensions

## Objective

Extend existing AI analysis with optional industry insights (still rule-based unless later approved).

## Business Type

All

## Why This Sprint Is Required

Reuse AI assistant; do not rebuild.

## Existing Functionality

ai_assistant_service sales analysis.

## Missing Functionality

Module-aware metrics (e.g., table turnover, IMEI aging) as optional.

## Scope

### Backend Tasks

- Pluggable analyzers per module

### Frontend Tasks

- AI page sections if module on

### Database Tasks

- N/A

### API Tasks

- /ai/analysis enriched

### UI/UX Tasks

- Same AI page

### Testing Tasks

- Tenant scoped
- No cross data

### Documentation Tasks

- AI

## Database Changes

Conceptual entities only (no SQL in this plan):

- N/A

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- /ai/*

## Frontend Pages

- AiAssistantPage

## User Roles

Owner.

## Tenant Isolation

Critical.

## Audit Requirements

AI decision log if any writes.

## Notifications

Optional insight notices.

## Acceptance Criteria

- Restaurant tenant sees F&B insights only

## Dependencies

BIZ-61

## Risks

- Overclaiming LLM — keep deterministic

## Definition of Done

- Plugin pattern documented

## Status

NOT STARTED

## Phase

Phase 12 – Cross-Business Reports / AI / Notifications
