/** Base units of measure (BIZ-08). */

export const DEFAULT_UOM = 'pcs';

export const UOM_OPTIONS = [
  { value: 'pcs', label: 'Pieces (pcs)' },
  { value: 'kg', label: 'Kilogram (kg)' },
  { value: 'g', label: 'Gram (g)' },
  { value: 'l', label: 'Litre (l)' },
  { value: 'ml', label: 'Millilitre (ml)' },
  { value: 'm', label: 'Metre (m)' },
  { value: 'cm', label: 'Centimetre (cm)' },
  { value: 'box', label: 'Box' },
  { value: 'pack', label: 'Pack' },
];

export function uomLabel(code) {
  return UOM_OPTIONS.find((row) => row.value === code)?.label || code || DEFAULT_UOM;
}

const WEIGHT_UOMS = new Set(['kg', 'g', 'l', 'ml']);

export function isWeightUom(code) {
  return WEIGHT_UOMS.has((code || DEFAULT_UOM).toLowerCase());
}

export function qtyStepForUom(code) {
  return isWeightUom(code) ? 0.001 : 1;
}

export function defaultScanQty(code) {
  return isWeightUom(code) ? 1 : 1;
}
