# Security Testing

Auth matrix · role checks · secret leakage · rate limits · XSS/SQLi via normal inputs.

## Tenant isolation regression (BIZ-64)

Hard rule: `tenant_id` comes from JWT/server context — never from the client body.

Suite: `backend/tests/test_biz64_tenant_isolation_regression_suite.py`

| Cluster | Entities probed |
|---------|-----------------|
| F&B KOT | KOT, order |
| Mobile | repair, serial by-serial |
| Electronics | installation |
| Hardware | quotation, challan, warehouse |
| Bakery | production, custom order, recipe |
| Furniture | custom order, delivery |
| Wholesale | price list, SO, PO, customer |
| Travel | package, booking, itinerary, agent |

Attacker roles:

- **Owner of tenant B** — permission-parity IDOR (expects **404** when both tenants share the module)
- **Billing User of tenant B** — additional probes on billing-readable paths (404 or 403; never **200** with A’s data)

Also covered:

- Audit logs are tenant-scoped (A’s entity IDs never appear in B’s audit list)
- Injecting `tenant_id` on create is ignored (customer stays on A)

### Run / CI

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests/test_biz64_tenant_isolation_regression_suite.py -q
# or all isolation-marked tests:
.\.venv\Scripts\python.exe -m pytest -m isolation -q
```

Include this file (or `-m isolation`) in the standard backend pytest job. `pytest.ini` already sets `testpaths = tests`, so a full `pytest` run picks up the suite automatically.
