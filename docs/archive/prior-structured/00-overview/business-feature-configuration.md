# Business Feature Configuration

## Resolution chain

```
Tenant.business_type
  → BusinessType record
  → BusinessTypeModule / BusinessTypeFeature
  → Runtime: navigation, API allow-list, dashboard widgets
```

## Examples

### Restaurant

| Feature | Enabled |
|---------|---------|
| Billing | YES |
| Inventory | YES |
| Table Management | YES |
| KOT / Kitchen | YES |
| Travel Booking | NO |
| IMEI | NO |
| Size/Color | NO |

### Clothing

| Feature | Enabled |
|---------|---------|
| Billing | YES |
| Inventory | YES |
| Size / Color / Brand | YES |
| KOT / Kitchen / Tables | NO |

### Travel Agency

| Feature | Enabled |
|---------|---------|
| Billing (service) | YES |
| Packages / Bookings | YES |
| Inventory | LIGHT / NO |
| IMEI / Tables | NO |

Full matrix: [business-feature-matrix.md](./business-feature-matrix.md).

This configuration must be agreed **before** database implementation of module tables.
