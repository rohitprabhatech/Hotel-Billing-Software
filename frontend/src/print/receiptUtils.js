export function formatMoney(value) {
  return Number(value || 0).toFixed(2);
}

export function formatRupee(value) {
  const amount = Number(value || 0);
  return `₹ ${amount.toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export function formatDate(value) {
  if (!value) return '';
  const d = new Date(value);
  return d.toLocaleString('en-IN', {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatDateLong(value) {
  if (!value) return '';
  const d = new Date(value);
  return d.toLocaleString('en-IN', {
    weekday: 'short',
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatDateShort(value) {
  if (!value) return '';
  const d = new Date(value);
  return d.toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

export function commonGstRate(items = []) {
  const rates = [...new Set(items.map((i) => Number(i.gst_percentage)))];
  if (rates.length === 1) return rates[0];
  return null;
}

const WIDTH_BY_CLASS = {
  58: 58,
  80: 80,
  a4: 210,
  a5: 148,
};

export function receiptDimensions(width, billingSettings = {}) {
  const settings = billingSettings || {};
  const style = {};

  const presetWidth = WIDTH_BY_CLASS[width];
  const resolvedWidth = settings.width_mm || presetWidth;
  const resolvedHeight = settings.height_mm;

  if (resolvedWidth) {
    style.width = `${resolvedWidth}mm`;
    style.maxWidth = `${resolvedWidth}mm`;
  }
  if (resolvedHeight) {
    style.minHeight = `${resolvedHeight}mm`;
  }

  return Object.keys(style).length ? style : undefined;
}
