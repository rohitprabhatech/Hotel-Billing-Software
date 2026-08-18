export function subscriptionAllowsAccess(subscription) {
  if (!subscription) return false;
  if (typeof subscription.access_allowed === 'boolean') return subscription.access_allowed;
  return ['TRIAL', 'ACTIVE', 'EXPIRING'].includes(subscription.status);
}

export function isAccountPath(pathname) {
  return (
    pathname === '/owner/profile' ||
    pathname === '/owner/change-password' ||
    pathname === '/billing/profile' ||
    pathname === '/billing/change-password'
  );
}
