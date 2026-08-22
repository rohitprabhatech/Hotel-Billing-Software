# Sprint BIZ-16 – Recipe and Ingredient Stock

## Objective

Recipes map menu items to ingredient items; deduct ingredients on settle/KOT policy.

## Business Type

Hotels / Restaurants (+ Bakery later reuse)

## Why This Sprint Is Required

Food wastage + ingredient stock; bakery will reuse patterns.

## Existing Functionality

Item stock qty.

## Missing Functionality

recipes, recipe_lines, deduction engine.

## Scope

### Backend Tasks

- Recipe CRUD
- Deduct ingredients on settle

### Frontend Tasks

- Recipe editor

### Database Tasks

- recipes
- recipe_ingredients

### API Tasks

- /recipes

### UI/UX Tasks

- Simple BOM UI

### Testing Tasks

- Insufficient ingredient blocks or warns per config

### Documentation Tasks

- Recipe module

## Database Changes

Conceptual entities only (no SQL in this plan):

- recipes
- recipe_ingredients

Every tenant-owned entity must include `tenant_id` set from JWT/server context — never from client body.

## API Requirements

Conceptual endpoints (do not implement until sprint approval):

- CRUD recipes

## Frontend Pages

- RecipesPage

## User Roles

Owner/Manager manage recipes.

## Tenant Isolation

Recipes tenant-scoped; ingredients same tenant.

## Audit Requirements

Recipe changes; deduction movements.

## Notifications

Low ingredient stock.

## Acceptance Criteria

- Settle deducts ingredients via stock_movements

## Dependencies

BIZ-15

## Risks

- Timing of deduct (KOT vs settle) — document policy

## Definition of Done

- Policy documented + implemented one way

## Status

COMPLETED

## Deduction policy

**Settle-time deduction** (`RECIPE_DEDUCTION_POLICY = "settle"`): ingredients deduct when an order is settled or a POS bill is finalized — **not** when KOT is fired. This avoids double-deduct on KOT reprints and matches BIZ-15 stock-once rules.

## Deliverables (implemented)

- **DB:** `recipes`, `recipe_ingredients` — migration `20260822_biz16_recipes.py`
- **API:** CRUD `/api/v1/recipes`, lookup `/api/v1/recipes/by-menu-item/:id`
- **Engine:** `RecipeStockService.expand_for_deduction` hooked into order settle + direct billing + bill cancel restore
- **Stock movements:** `RECIPE` source on ingredient deductions at settle
- **Permissions:** `recipes.read`, `recipes.write` (Owner/Manager)
- **Frontend:** `RecipesPage` BOM editor (Owner nav)
- **Tests:** `test_biz16_recipe_ingredient_stock.py`

## Phase

Phase 02 – Restaurant / Cafe
