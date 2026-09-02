/** Mirrors backend `normalize_email` rules for optional bill email fields. */
const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

export function isValidEmail(value) {
  const email = (value || '').trim().toLowerCase();
  return email.length > 0 && email.length <= 255 && EMAIL_RE.test(email);
}

/** Returns `{ value, error }` for bill payloads — empty input is allowed. */
export function resolveBillCustomerEmail(value) {
  const trimmed = (value || '').trim();
  if (!trimmed) return { value: null, error: null };
  if (!isValidEmail(trimmed)) {
    return {
      value: null,
      error: 'Enter a valid email address or clear the email field.',
    };
  }
  return { value: trimmed.toLowerCase(), error: null };
}
