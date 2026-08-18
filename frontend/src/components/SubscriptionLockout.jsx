import { Alert, Button, Stack, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { COMPANY } from '../constants/company';
import { PATHS } from '../routes/paths';
import { subscriptionAllowsAccess } from '../utils/subscriptionAccess';

export default function SubscriptionLockout({ user, accountPath }) {
  const sub = user?.tenant?.subscription;
  if (subscriptionAllowsAccess(sub)) return null;

  const status = sub?.status || 'NONE';
  return (
    <Alert severity="error" sx={{ mb: 2 }}>
      <Typography fontWeight={650} sx={{ mb: 0.5 }}>
        Billing access is paused
      </Typography>
      <Typography variant="body2" sx={{ mb: 1.5 }}>
        {status === 'NONE'
          ? 'This business does not have an active subscription yet.'
          : `Subscription status: ${status}.`}{' '}
        Contact {COMPANY.legalName} at {COMPANY.email} or {COMPANY.phoneDisplay} to renew.
      </Typography>
      <Stack direction="row" spacing={1}>
        <Button component={RouterLink} to={accountPath} size="small" variant="outlined">
          Account
        </Button>
        <Button href={COMPANY.emailHref} size="small" variant="contained">
          Email support
        </Button>
      </Stack>
    </Alert>
  );
}

export function useLockedOutlet(user, pathname, { owner = true } = {}) {
  const allowed = subscriptionAllowsAccess(user?.tenant?.subscription);
  const accountPath = owner ? PATHS.ownerProfile : PATHS.billingProfile;
  const accountOk = pathname === accountPath || pathname.includes('/change-password');
  return { allowed, accountOk, accountPath };
}
