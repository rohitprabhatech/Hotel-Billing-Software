export const VALID_ROLES = ['OWNER', 'BILLING_USER', 'MASTER_ADMIN'];

export function isValidRole(role) {
  return VALID_ROLES.includes(role);
}

/** Post-login / authenticated home path for a known role. */
export function homePathForRole(role) {
  if (role === 'MASTER_ADMIN') return '/master/dashboard';
  if (role === 'OWNER') return '/owner/dashboard';
  if (role === 'BILLING_USER') return '/billing';
  return '/login';
}
