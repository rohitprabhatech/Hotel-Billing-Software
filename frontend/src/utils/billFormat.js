/** Printed bill layout variants — keep aligned with backend `billing_format` constants. */

export const BILL_FORMAT_STANDARD = 'standard';
export const BILL_FORMAT_TRAVEL = 'travel';

export const BILL_FORMAT_OPTIONS = [
  { value: BILL_FORMAT_TRAVEL, label: 'Travel Booking Voucher' },
  { value: BILL_FORMAT_STANDARD, label: 'Standard Cash Memo' },
];

const DEFAULT_BY_BUSINESS = {
  travel_agency: BILL_FORMAT_TRAVEL,
};

export function defaultBillFormat(businessType) {
  if (!businessType) return BILL_FORMAT_STANDARD;
  return DEFAULT_BY_BUSINESS[String(businessType).toLowerCase()] || BILL_FORMAT_STANDARD;
}

export function resolveBillFormat(billingSettings = {}, tenant = {}) {
  const explicit = billingSettings.bill_format;
  if (explicit) return explicit;
  return defaultBillFormat(tenant.business_type);
}

export function billFormatLabel(value) {
  const match = BILL_FORMAT_OPTIONS.find((option) => option.value === value);
  return match?.label || 'Standard Cash Memo';
}
