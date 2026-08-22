# Inventory Engine — Prabha Billing SaaS V2

## Goal

Flexible, **generic** inventory — not 14 separate stock systems.

## Modes

| Mode | Example |
|------|---------|
| Simple quantity | 10 pieces |
| Weight | 10 kg |
| Volume | 20 L |
| Length | 100 m |
| Area | 500 sq.ft |
| Serial | IMEI / serial |
| Batch / lot | Lot + qty |
| Expiry | Date on batch |
| Variants | Size + color stock |

## Core operations

Receive · Adjust · Sale deduction · Return restock · Transfer (warehouse) · Wastage · Production consume (recipe)

## Restaurant recipes

Finished item → Recipe → ingredients with quantities. Selling one burger deducts configured ingredients when recipe mode enabled.

## Rules

- Stock never negative unless BusinessSettings allow.  
- Movements append-only.  
- Tenant-scoped always.  
- Medical-specific medicine entities **forbidden**; batch/expiry remain for grocery/bakery.

## Current baseline

`items.stock_quantity` + `stock_movements` + adjust/receive + low-stock notifications. Evolve toward variants/serials/batches/warehouses in inventory sprints.
