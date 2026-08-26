/** Map Axios / API failures to short user-facing messages (no stack traces). */

const STATUS_FALLBACKS = {
  400: 'Invalid request. Please check your input and try again.',
  401: 'Your session has expired. Please sign in again.',
  403: 'You do not have permission to perform this action.',
  404: 'The requested record was not found.',
  409: 'This action conflicts with the current data. Refresh and try again.',
  422: 'Some fields are invalid. Please review and correct them.',
  429: 'Too many requests. Please wait a moment and try again.',
  500: 'Something went wrong on the server. Please try again later.',
  502: 'Service temporarily unavailable. Please try again later.',
  503: 'Service temporarily unavailable. Please try again later.',
};

/**
 * @param {unknown} err
 * @param {string} [fallback]
 * @returns {string}
 */
export function getApiErrorMessage(err, fallback = 'Something went wrong. Please try again.') {
  const status = err?.response?.status;
  const payload = err?.response?.data;
  const apiMessage =
    payload?.error?.message ||
    payload?.message ||
    (typeof payload?.error === 'string' ? payload.error : null);

  if (apiMessage && typeof apiMessage === 'string') {
    // Never surface raw HTML / huge dumps
    const trimmed = apiMessage.trim();
    if (trimmed && !trimmed.startsWith('<') && trimmed.length < 500) {
      return trimmed;
    }
  }

  if (status && STATUS_FALLBACKS[status]) {
    return STATUS_FALLBACKS[status];
  }

  if (!err?.response && err?.message === 'Network Error') {
    return 'Unable to reach the server. Check your connection and try again.';
  }

  return fallback;
}
