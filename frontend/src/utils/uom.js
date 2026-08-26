/** Base units of measure (BIZ-08 / BIZ-35). */

export const DEFAULT_UOM = 'pcs';

export const UOM_OPTIONS = [
  { value: 'pcs', label: 'Pieces (pcs)', kind: 'count' },
  { value: 'kg', label: 'Kilogram (kg)', kind: 'weight' },
  { value: 'g', label: 'Gram (g)', kind: 'weight' },
  { value: 'l', label: 'Litre (l)', kind: 'volume' },
  { value: 'ml', label: 'Millilitre (ml)', kind: 'volume' },
  { value: 'm', label: 'Metre (m)', kind: 'length' },
  { value: 'cm', label: 'Centimetre (cm)', kind: 'length' },
  { value: 'ft', label: 'Foot (ft)', kind: 'length' },
  { value: 'sqm', label: 'Square metre (sqm)', kind: 'area' },
  { value: 'sqft', label: 'Square foot (sqft)', kind: 'area' },
  { value: 'box', label: 'Box', kind: 'count' },
  { value: 'pack', label: 'Pack', kind: 'count' },
];

export function uomLabel(code) {
  return UOM_OPTIONS.find((row) => row.value === code)?.label || code || DEFAULT_UOM;
}

const MEASUREMENT_KINDS = new Set(['weight', 'volume', 'length', 'area']);

export function uomKind(code) {
  return UOM_OPTIONS.find((row) => row.value === code)?.kind || 'count';
}

export function isWeightUom(code) {
  const kind = uomKind(code);
  return kind === 'weight' || kind === 'volume';
}

export function isMeasurementUom(code) {
  return MEASUREMENT_KINDS.has(uomKind(code));
}

export function qtyStepForUom(code) {
  return isMeasurementUom(code) ? 0.001 : 1;
}

export function defaultScanQty(code) {
  return 1;
}
