# Tenant Architecture

Each approved business is a **tenant**. Shared DB, logical isolation via `tenant_id`.

```
Tenant → Users, Catalog, Bills, Inventory, Settings, Industry data
```

Platform globals: MasterAdmin, Plans, BusinessTypes, Module catalog.
