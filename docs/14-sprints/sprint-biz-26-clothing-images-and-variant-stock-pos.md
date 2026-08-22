# Sprint BIZ-26 – Clothing Images and Variant Stock POS

## Objective

Product images + POS variant picker; size/color-wise stock display.

## Business Type

Clothing Shops

## Why This Sprint Is Required

Special clothing UX.

## Existing Functionality

No images.

## Missing Functionality

image storage metadata, POS picker.

## Scope

### Backend Tasks

- Image URL fields or attachments metadata

### Frontend Tasks

- Image upload UI
- POS variant select

### Database Tasks

- item_images or items.image_url

### API Tasks

- upload/metadata

### UI/UX Tasks

- Gallery thumbnails; same theme

### Testing Tasks

- Stock of selected variant

### Documentation Tasks

- frontend clothing

## Database Changes

Conceptual entities only (no SQL in this plan):

- item_images

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- images

## Frontend Pages

- Item images
- Clothing POS

## User Roles

Owner uploads; Billing sells.

## Tenant Isolation

Standard.

## Audit Requirements

Image changes optional.

## Notifications

None.

## Acceptance Criteria

- Cannot sell wrong variant stock

## Dependencies

BIZ-25

## Risks

- File storage ops — start URL metadata

## Definition of Done

- POS variant path

## Status

NOT STARTED

## Phase

Phase 04 – Clothing
