# Product Overview — Prabha Billing SaaS

**Working product name:** Prabha Billing SaaS (UI may continue as **Business Billing** until rename sprint)  
**Provider:** Prabha Technology Pvt. Ltd.  
**Phase:** Documentation only

---

## Vision

Transform the existing Hotel / Business Billing product into a **professional multi-tenant, multi-business billing and business management SaaS** sold on a **monthly subscription** with a configurable **free trial** (default **15 days**).

One platform:

```
COMMON CORE  +  INDUSTRY-SPECIFIC MODULES
```

Not fourteen separate billing applications.

---

## Company

| Field | Value |
|-------|--------|
| Legal name | Prabha Technology Pvt. Ltd. |
| Address | B-05, First Floor, Shreya Business Hub, Pari Chowk, Mokarwadi, Pune, Maharashtra – 411041 |
| Email | prabha.technology.01@gmail.com |
| Phone | 8767865572 |
| Support | 24/7 technical support for registered businesses |

---

## Who uses the product

| Actor | Purpose |
|-------|---------|
| **Master Admin** | Prabha Technology operators — approve businesses, plans, trials, lifecycle |
| **Business Owner** | Configure shop, users, catalog, reports, subscription view |
| **Billing User** | POS / billing (permissions configurable) |
| **Manager** (target) | Optional mid-tier role where needed |
| **Public visitor** | Landing, register, pricing |

Master login remains **footer-dot** → `/master/login` (not a public navbar CTA).

---

## Commercial model

- Monthly subscription (example default ₹550 — **catalog-driven**, not hard-coded in UI long-term).  
- Master Admin configures plans, features, visibility, trial on/off and days.  
- No requirement for in-app SaaS payment gateway in early V2 sprints (manual activation / contact).  
- **Business customer payments** (cash/UPI/card/credit) are separate from **SaaS subscription** payments.

---

## Supported industries (exactly 14)

1. Hotels / Restaurants  
2. Cafes / Tea Shops  
3. Grocery Stores / Kirana  
4. Clothing Shops  
5. Mobile Shops  
6. Hardware Stores  
7. Bakery / Sweet Shops  
8. Stationery Shops  
9. Electronics Shops  
10. Furniture Shops  
11. Hardware / Building Material  
12. Book Stores  
13. Wholesale Shops  
14. Travel Agencies  

**Removed from scope:** Medical Stores (and all medicine/prescription entities).

---

## Value proposition

| For businesses | For Prabha Technology |
|----------------|------------------------|
| Fast billing, inventory, reports | Multi-tenant SaaS revenue |
| Industry-aware dashboards & workflows | Central Master control plane |
| Trial then paid plan | Configurable plans & trial |
| WhatsApp / print / PDF invoices | Platform audit & ops tools |

---

## Non-goals (initial V2 waves)

- Building 14 isolated codebases  
- Medical / pharmacy compliance modules  
- Automatic destructive DB resets  
- Claiming legal certifications without counsel review  

---

## Related docs

[product-requirements.md](./product-requirements.md) · [business-types.md](./business-types.md) · [architecture.md](./architecture.md) · [sprint-plan.md](./sprint-plan.md)
