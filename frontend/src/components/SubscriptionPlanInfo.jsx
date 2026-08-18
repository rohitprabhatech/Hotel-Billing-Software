import { Box, Button, Link, Stack, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { COMPANY, SUBSCRIPTION_PLAN } from '../constants/company';
import { PATHS } from '../routes/paths';

/**
 * Informational subscription plan display — never renders a fake checkout.
 */
export default function SubscriptionPlanInfo({
  variant = 'public',
  showPublicCtas = true,
  dense = false,
  plan = null,
}) {
  const isOwner = variant === 'owner';
  const currentPlan = plan || SUBSCRIPTION_PLAN;
  const priceLabel = currentPlan.priceLabel || SUBSCRIPTION_PLAN.priceLabel;
  const periodLabel = currentPlan.periodLabel || SUBSCRIPTION_PLAN.periodLabel;
  const billingNote = currentPlan.billingNote || SUBSCRIPTION_PLAN.billingNote;
  const includes = currentPlan.includes || SUBSCRIPTION_PLAN.includes;

  return (
    <Box>
      <Stack
        direction={{ xs: 'column', sm: 'row' }}
        spacing={2}
        alignItems={{ xs: 'flex-start', sm: 'baseline' }}
        sx={{ mb: dense ? 2 : 3 }}
      >
        <Typography
          sx={{
            fontFamily: '"Sora", "Source Sans 3", sans-serif',
            fontWeight: 700,
            fontSize: dense ? '1.75rem' : '2.25rem',
            letterSpacing: '-0.03em',
            lineHeight: 1,
          }}
        >
          {priceLabel}
        </Typography>
        <Typography color="text.secondary" fontWeight={600}>
          {periodLabel}
        </Typography>
      </Stack>

      <Typography variant="subtitle1" sx={{ mb: 0.5 }}>
        {currentPlan.name}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2.5, maxWidth: 560 }}>
        {billingNote}
      </Typography>

      <Box
        component="ul"
        sx={{
          m: 0,
          pl: 2.25,
          mb: 3,
          '& li': { mb: 0.75, color: 'text.secondary' },
        }}
      >
        {includes.map((item) => (
          <Typography component="li" variant="body2" key={item}>
            {item}
          </Typography>
        ))}
      </Box>

      <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
        {SUBSCRIPTION_PLAN.currencyNote}
      </Typography>

      {showPublicCtas && !isOwner ? (
        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          spacing={1.5}
          useFlexGap
          flexWrap="wrap"
          sx={{ '& > *': { width: { xs: '100%', sm: 'auto' } } }}
        >
          <Button component={RouterLink} to={PATHS.register} variant="contained">
            {currentPlan.ctaRegister || SUBSCRIPTION_PLAN.ctaRegister}
          </Button>
          <Button component={RouterLink} to={PATHS.login} variant="outlined">
            {currentPlan.ctaLogin || SUBSCRIPTION_PLAN.ctaLogin}
          </Button>
          <Button href="#contact" variant="text">
            {currentPlan.ctaContact || SUBSCRIPTION_PLAN.ctaContact}
          </Button>
        </Stack>
      ) : null}

      {isOwner ? (
        <Stack spacing={1.25}>
          <Typography variant="body2" color="text.secondary">
            To activate, renew, or ask about invoices, contact{' '}
            <Link href={COMPANY.emailHref} fontWeight={600}>
              {COMPANY.email}
            </Link>{' '}
            or call{' '}
            <Link href={COMPANY.phoneHref} fontWeight={600}>
              {COMPANY.phoneDisplay || COMPANY.phone}
            </Link>
            .
          </Typography>
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            spacing={1.5}
            sx={{ '& > *': { width: { xs: '100%', sm: 'auto' } } }}
          >
            <Button
              component="a"
              href={COMPANY.emailHref}
              variant="contained"
            >
              Email support
            </Button>
            <Button component="a" href={COMPANY.phoneHref} variant="outlined">
              Call {COMPANY.phoneDisplay || COMPANY.phone}
            </Button>
          </Stack>
        </Stack>
      ) : null}
    </Box>
  );
}
