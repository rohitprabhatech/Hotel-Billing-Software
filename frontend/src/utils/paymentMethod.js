/** Controlled payment methods — keep in sync with backend `app.constants.payments`. */

export const PAYMENT_CASH = 'cash';
export const PAYMENT_ONLINE = 'online';
export const ALLOWED_PAYMENT_METHODS = Object.freeze([PAYMENT_CASH, PAYMENT_ONLINE]);
export const DEFAULT_PAYMENT_METHOD = PAYMENT_CASH;

export function isAllowedPaymentMethod(value) {
  return ALLOWED_PAYMENT_METHODS.includes(String(value || '').toLowerCase());
}

export function paymentMethodLabel(value) {
  const method = String(value || DEFAULT_PAYMENT_METHOD).toLowerCase();
  if (method === PAYMENT_ONLINE) return 'Online';
  return 'Cash';
}
