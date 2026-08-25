/** Resolve unit price from quantity price tiers (BIZ-21). */

export function resolveTierUnitPrice(basePrice, quantity, tiers = []) {
  const qty = Number(quantity);
  const base = Number(basePrice);
  if (!Number.isFinite(qty) || qty <= 0) return Number.isFinite(base) ? base : 0;
  if (!Array.isArray(tiers) || !tiers.length) return Number.isFinite(base) ? base : 0;

  let matched = null;
  const sorted = [...tiers]
    .filter((row) => row && row.is_active !== false)
    .sort((a, b) => Number(a.min_quantity) - Number(b.min_quantity));

  for (const tier of sorted) {
    if (Number(tier.min_quantity) <= qty) {
      matched = tier;
    } else {
      break;
    }
  }
  if (!matched) return Number.isFinite(base) ? base : 0;
  const price = Number(matched.unit_price);
  return Number.isFinite(price) ? price : base;
}
