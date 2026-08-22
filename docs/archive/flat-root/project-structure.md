# Project Structure — Prabha Billing SaaS V2

**Conceptual target** after approved sprints. Current tree remains valid until migrated gradually.

```
Hotel-Billing-Software/          # repo name may stay; product = Prabha Billing SaaS
├── backend/
│   ├── app/
│   │   ├── core/                # NEW — billing/inventory/tax kernels
│   │   ├── modules/             # NEW — industry + domain packs
│   │   ├── controllers/         # existing
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── middleware/
│   │   └── ...
│   ├── migrations/
│   ├── scripts/                 # inspect, apply, seed, backup
│   ├── sql/                     # greenfield 02_schema only for empty DBs
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── modules/             # NEW
│   │   ├── pages/
│   │   ├── layouts/
│   │   ├── components/
│   │   └── ...
│   └── ...
├── docs/                        # V2 docs + historical sprint reports
└── README.md
```

### Migration approach

1. Keep existing folders working.  
2. Add `core/` and `modules/` incrementally.  
3. Move logic only when a sprint owns that module.  
4. No big-bang rewrite.
