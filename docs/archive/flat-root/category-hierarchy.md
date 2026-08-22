# Category Hierarchy Guide

Parent categories are supported for any business type.

## Rules (enforced in API)

1. Parent must belong to the **same tenant/business**
2. Category cannot be its own parent
3. Category cannot use a descendant as parent (no circular trees)
4. Parent category must be **active**
5. A category with children cannot be deactivated until children are reassigned/deactivated
6. Parent dropdown in the UI lists only the current business’s categories

## Examples

### Food / restaurant

```
Food
 ├── Veg
 ├── Non-Veg
 └── Snacks
```

### Clothing / retail

```
Clothing
 ├── Men
 │    ├── Shirts
 │    └── Pants
 └── Women
      ├── Dresses
      └── Tops
```

API responses include:

- `parent_id` / `parent_category_id`
- `parent_category_name`
- `hierarchy_path` (e.g. `Clothing › Men › Shirts`)

Owner UI: `/owner/categories`  
Billing UI (read-only): `/billing/categories`
