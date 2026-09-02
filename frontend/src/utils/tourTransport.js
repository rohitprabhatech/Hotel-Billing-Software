/** Tour package transport modes — keep labels aligned with backend `tour_transport` constants. */

export const TOUR_TRANSPORT_OTHER = 'other';

export const TOUR_TRANSPORT_OPTIONS = [
  { value: 'bus', label: 'Bus' },
  { value: 'car', label: 'Car' },
  { value: 'train', label: 'Train' },
  { value: 'flight', label: 'Flight' },
  { value: 'van', label: 'Van' },
  { value: 'tempo', label: 'Tempo Traveller' },
  { value: 'cruise', label: 'Cruise' },
  { value: 'boat', label: 'Boat' },
  { value: 'bike', label: 'Bike / Scooter' },
  { value: TOUR_TRANSPORT_OTHER, label: 'Other' },
];

const LABEL_BY_VALUE = Object.fromEntries(
  TOUR_TRANSPORT_OPTIONS.map((option) => [option.value, option.label]),
);

export function tourTransportLabel(value) {
  if (!value) return '';
  const key = String(value).toLowerCase();
  return LABEL_BY_VALUE[key] || String(value);
}

export function resolveTourTransportPayload(transportType, transportOther) {
  const selected = (transportType || '').trim();
  if (!selected) return null;
  if (selected === TOUR_TRANSPORT_OTHER) {
    return (transportOther || '').trim() || null;
  }
  return selected;
}

export function splitTourTransportValue(value) {
  if (!value) {
    return { transport_type: '', transport_type_other: '' };
  }
  const key = String(value).toLowerCase();
  if (LABEL_BY_VALUE[key]) {
    return { transport_type: key, transport_type_other: '' };
  }
  return { transport_type: TOUR_TRANSPORT_OTHER, transport_type_other: String(value) };
}
