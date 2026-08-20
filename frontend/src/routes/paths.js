/** Central route paths — keep navigation consistent across layouts. */

export const PATHS = {
  home: '/',
  login: '/login',
  register: '/register',
  forgotPassword: '/forgot-password',
  resetPassword: '/reset-password',
  verifyEmail: '/verify-email',
  privacy: '/privacy',
  terms: '/terms',

  masterLogin: '/master/login',
  masterDashboard: '/master/dashboard',
  masterRegistrationRequests: '/master/registration-requests',
  masterTrials: '/master/trials',
  masterPlans: '/master/plans',
  masterBusinesses: '/master/businesses',
  masterAudit: '/master/audit',
  masterTrialSettings: '/master/settings/trial',
  masterChangePassword: '/master/change-password',

  ownerDashboard: '/owner/dashboard',
  ownerBills: '/owner/bills',
  ownerItems: '/owner/items',
  ownerItemActivity: '/owner/item-activity',
  ownerStockMovements: '/owner/stock-movements',
  ownerCategories: '/owner/categories',
  ownerReports: '/owner/reports',
  ownerAi: '/owner/ai',
  ownerAudit: '/owner/audit',
  ownerUsers: '/owner/users',
  ownerSettings: '/owner/settings',
  ownerProfile: '/owner/profile',
  ownerChangePassword: '/owner/change-password',

  billingHome: '/billing',
  billingNew: '/billing/new',
  billingBills: '/billing/bills',
  billingItems: '/billing/items',
  billingCategories: '/billing/categories',
  billingProfile: '/billing/profile',
  billingChangePassword: '/billing/change-password',
};

export function masterBusinessesPath({ status, tenant_status } = {}) {
  const params = new URLSearchParams();
  if (status) params.set('status', status);
  if (tenant_status) params.set('tenant_status', tenant_status);
  const query = params.toString();
  return query ? `${PATHS.masterBusinesses}?${query}` : PATHS.masterBusinesses;
}
