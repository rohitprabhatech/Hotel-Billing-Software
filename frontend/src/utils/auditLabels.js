const ACTION_LABELS = {
  DEACTIVATE_CUSTOMER: 'Customer Deleted',
  CREATE_CUSTOMER: 'Customer Created',
  UPDATE_CUSTOMER: 'Customer Updated',
  CREATE_BILL: 'Bill Generated',
  CANCEL_BILL: 'Bill Cancelled',
  PRINT_BILL: 'Bill Printed',
  REPRINT_BILL: 'Bill Reprinted',
  ITEM_CREATED: 'Item Created',
  ITEM_UPDATED: 'Item Updated',
  ITEM_DEACTIVATED: 'Item Deleted',
  ITEM_REACTIVATED: 'Item Reactivated',
  CREATE_CATEGORY: 'Category Created',
  UPDATE_CATEGORY: 'Category Updated',
  DEACTIVATE_CATEGORY: 'Category Deleted',
  CREATE_EXPENSE: 'Expense Created',
  UPDATE_EXPENSE: 'Expense Updated',
  DELETE_EXPENSE: 'Expense Deleted',
  CREATE_WASTAGE: 'Wastage Created',
  UPDATE_WASTAGE: 'Wastage Updated',
  DELETE_WASTAGE: 'Wastage Deleted',
  CREATE_RECIPE: 'Recipe Created',
  UPDATE_RECIPE: 'Recipe Updated',
  DELETE_RECIPE: 'Recipe Deleted',
  MENU_UPDATED: 'Menu Updated',
  MENU_DELETED: 'Menu Deleted',
  CREATE_KOT: 'KOT Created',
  UPDATE_KOT: 'KOT Updated',
  DELETE_KOT: 'KOT Deleted',
  KOT_UPDATED: 'KOT Updated',
  KOT_DELETED: 'KOT Deleted',
  REPRINT_KOT: 'KOT Reprinted',
  UPDATE_KOT_STATUS: 'KOT Status Updated',
  CREATE_USER: 'Billing User Created',
  UPDATE_USER: 'Billing User Updated',
  DEACTIVATE_USER: 'Billing User Deactivated',
  UPDATE_BILLING_SETTINGS: 'Billing Settings Updated',
  COLLECT_CREDIT_PAYMENT: 'Payment Collected',
  LOGIN: 'Signed In',
  LOGOUT: 'Signed Out',
  PASSWORD_CHANGED: 'Password Changed',
};

const ROLE_LABELS = {
  OWNER: 'Owner',
  MANAGER: 'Manager',
  BILLING_USER: 'Billing User',
};

export function formatAuditAction(action) {
  if (!action) return '—';
  if (ACTION_LABELS[action]) return ACTION_LABELS[action];
  return action
    .split('_')
    .map((part) => part.charAt(0) + part.slice(1).toLowerCase())
    .join(' ');
}

export function formatUserRole(role) {
  if (!role) return '—';
  return ROLE_LABELS[role] || role.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

export const ACTIVITY_CATEGORIES = [
  { value: '', label: 'All Activities' },
  { value: 'customer', label: 'Customer' },
  { value: 'item', label: 'Item' },
  { value: 'category', label: 'Category' },
  { value: 'billing', label: 'Billing' },
  { value: 'payment', label: 'Payment' },
  { value: 'expense', label: 'Expense' },
  { value: 'recipe', label: 'Recipe' },
  { value: 'wastage', label: 'Wastage' },
  { value: 'table', label: 'Table' },
  { value: 'user', label: 'User' },
  { value: 'inventory', label: 'Inventory' },
];

export const DATE_PRESETS = [
  { value: 'today', label: 'Today' },
  { value: 'yesterday', label: 'Yesterday' },
  { value: 'last_7_days', label: 'Last 7 Days' },
  { value: 'last_30_days', label: 'Last 30 Days' },
  { value: 'custom', label: 'Custom Date' },
];

function formatLocalDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export function dateRangeForPreset(preset) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const fmt = formatLocalDate;

  if (preset === 'today') {
    return { from: fmt(today), to: fmt(today) };
  }
  if (preset === 'yesterday') {
    const y = new Date(today);
    y.setDate(y.getDate() - 1);
    return { from: fmt(y), to: fmt(y) };
  }
  if (preset === 'last_7_days') {
    const start = new Date(today);
    start.setDate(start.getDate() - 6);
    return { from: fmt(start), to: fmt(today) };
  }
  if (preset === 'last_30_days') {
    const start = new Date(today);
    start.setDate(start.getDate() - 29);
    return { from: fmt(start), to: fmt(today) };
  }
  return { from: '', to: '' };
}

export function receiptClassFromSettings(settings = {}) {
  const paper = settings.paper_size || '80mm';
  if (paper === '58mm') return '58';
  if (paper === '80mm') return '80';
  if (paper === 'A4') return 'a4';
  if (paper === 'A5') return 'a5';
  return 'custom';
}

export function receiptStyleFromSettings(settings = {}) {
  const width = settings.width_mm;
  const height = settings.height_mm;
  if (!width) return {};
  const style = { width: `${width}mm` };
  if (height) style.minHeight = `${height}mm`;
  return style;
}
