import { Box, Button, Link, Stack, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import SubscriptionPlanInfo from '../../components/SubscriptionPlanInfo';
import { COMPANY } from '../../constants/company';
import { PATHS } from '../../routes/paths';
import { CONTENT_MAX, DISPLAY_FONT, NAV_LINKS } from './constants';
import { LandingSection } from './LandingSection';

function toDisplayPlan(plan) {
  const periodLabel = plan.billing_cycle === 'YEARLY' ? 'per year' : 'per month';
  return {
    ...plan,
    priceLabel: `₹${Number(plan.price).toLocaleString('en-IN')}`,
    periodLabel,
    billingNote:
      'Informational pricing only. Online checkout is not enabled in the app yet — contact Prabha Technology to activate or renew your plan.',
    includes: plan.features || [],
  };
}

export function PricingSection({ plans = [] }) {
  const rows = plans.map(toDisplayPlan);
  return (
    <LandingSection
      id="pricing"
      eyebrow="Pricing"
      title={rows.length > 1 ? 'Simple plans for your business' : 'Simple plan for your business'}
      body="Informational pricing — online checkout is not enabled in the app yet. Contact Prabha Technology to activate or renew."
    >
      <Box
        sx={{
          display: 'grid',
          gap: 3,
          gridTemplateColumns: rows.length > 1 ? { xs: '1fr', md: 'repeat(2, minmax(0, 1fr))' } : '1fr',
        }}
      >
        {rows.length ? (
          rows.map((plan) => (
            <Box
              key={plan.id}
              sx={{
                maxWidth: rows.length === 1 ? 520 : 'none',
                mx: rows.length === 1 ? { xs: 0, md: 'auto' } : 0,
                p: { xs: 3, md: 4 },
                borderRadius: 3,
                border: '1px solid',
                borderColor: 'divider',
                bgcolor: 'background.paper',
                boxShadow: (t) =>
                  t.palette.mode === 'dark'
                    ? '0 16px 40px rgba(0,0,0,0.35)'
                    : '0 20px 50px rgba(15,36,44,0.1)',
              }}
            >
              <SubscriptionPlanInfo plan={plan} showPublicCtas />
            </Box>
          ))
        ) : (
          <Box
            sx={{
              maxWidth: 520,
              mx: { xs: 0, md: 'auto' },
              p: { xs: 3, md: 4 },
              borderRadius: 3,
              border: '1px solid',
              borderColor: 'divider',
              bgcolor: 'background.paper',
            }}
          >
            <Typography variant="subtitle1" sx={{ mb: 1 }}>
              Pricing is available on request
            </Typography>
            <Typography variant="body2" color="text.secondary">
              No public plans are published right now. Contact {COMPANY.legalName} for current
              commercial terms.
            </Typography>
          </Box>
        )}
      </Box>
    </LandingSection>
  );
}

export function FinalCtaSection() {
  return (
    <LandingSection
      tone="ink"
      align="center"
      title="Ready for calmer counters?"
      body="Register your business, invite your team, and run billing, stock, and sales from one place."
    >
      <Stack
        direction={{ xs: 'column', sm: 'row' }}
        spacing={1.5}
        justifyContent="center"
        sx={{ '& > *': { width: { xs: '100%', sm: 'auto' } } }}
      >
        <Button
          component={RouterLink}
          to={PATHS.register}
          variant="contained"
          size="large"
          sx={{
            px: 3,
            py: 1.35,
            borderRadius: 1.5,
            bgcolor: '#fff',
            color: 'primary.dark',
            fontWeight: 700,
            '&:hover': { bgcolor: 'rgba(255,255,255,0.92)' },
          }}
        >
          Register Your Business
        </Button>
        <Button
          component={RouterLink}
          to={PATHS.login}
          variant="outlined"
          size="large"
          sx={{
            px: 3,
            py: 1.35,
            borderRadius: 1.5,
            borderColor: 'rgba(255,255,255,0.55)',
            color: '#fff',
            '&:hover': { borderColor: '#fff', bgcolor: 'rgba(255,255,255,0.08)' },
          }}
        >
          Login
        </Button>
      </Stack>
    </LandingSection>
  );
}

export function ContactSection() {
  return (
    <LandingSection
      id="contact"
      eyebrow="Company"
      title={COMPANY.legalName}
      body={COMPANY.supportNote}
    >
      <Box
        sx={{
          display: 'grid',
          gap: 3,
          gridTemplateColumns: { xs: '1fr', sm: '1.2fr 1fr' },
        }}
      >
        <Box>
          {COMPANY.addressLines.map((line) => (
            <Typography key={line} color="text.secondary" sx={{ lineHeight: 1.6 }}>
              {line}
            </Typography>
          ))}
        </Box>
        <Stack spacing={0.75}>
          <Link href={COMPANY.emailHref} fontWeight={650}>
            {COMPANY.email}
          </Link>
          <Link href={COMPANY.phoneHref} fontWeight={650}>
            {COMPANY.phoneDisplay}
          </Link>
          <Typography variant="body2" color="text.secondary">
            24/7 Technical Support
          </Typography>
        </Stack>
      </Box>
    </LandingSection>
  );
}

export function LandingFooter({ health, error }) {
  return (
    <Box
      component="footer"
      sx={{
        borderTop: '1px solid',
        borderColor: 'divider',
        px: { xs: 2, sm: 3, md: 5 },
        py: { xs: 5, md: 6 },
        bgcolor: (t) => (t.palette.mode === 'dark' ? 'background.paper' : 'rgba(31,78,95,0.04)'),
      }}
    >
      <Box sx={{ maxWidth: CONTENT_MAX, mx: 'auto' }}>
        <Box
          sx={{
            display: 'grid',
            gap: 4,
            gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1.4fr 1fr 1fr 1fr 1fr' },
            mb: 4,
          }}
        >
          <Box>
            <Typography fontWeight={700} sx={{ mb: 1, fontFamily: DISPLAY_FONT }}>
              {COMPANY.productName}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5, maxWidth: 280 }}>
              A product of {COMPANY.legalName}
            </Typography>
            {COMPANY.addressLines.map((line) => (
              <Typography key={line} variant="body2" color="text.secondary" sx={{ lineHeight: 1.55 }}>
                {line}
              </Typography>
            ))}
          </Box>
          <Box>
            <Typography variant="subtitle2" sx={{ mb: 1.25 }}>
              Product
            </Typography>
            <Stack spacing={0.75}>
              {NAV_LINKS.map((l) => (
                <Link key={l.href} href={l.href} underline="hover" color="text.secondary" variant="body2">
                  {l.label}
                </Link>
              ))}
            </Stack>
          </Box>
          <Box>
            <Typography variant="subtitle2" sx={{ mb: 1.25 }}>
              Business
            </Typography>
            <Stack spacing={0.75}>
              <Link href="#how-it-works" underline="hover" color="text.secondary" variant="body2">
                Billing
              </Link>
              <Link href="#solutions" underline="hover" color="text.secondary" variant="body2">
                Stock
              </Link>
              <Link href="#features" underline="hover" color="text.secondary" variant="body2">
                Reports
              </Link>
              <Link href="#features" underline="hover" color="text.secondary" variant="body2">
                Audit
              </Link>
            </Stack>
          </Box>
          <Box>
            <Typography variant="subtitle2" sx={{ mb: 1.25 }}>
              Company
            </Typography>
            <Stack spacing={0.75}>
              <Link href="#contact" underline="hover" color="text.secondary" variant="body2">
                About / Contact
              </Link>
              <Link href={COMPANY.emailHref} underline="hover" color="text.secondary" variant="body2">
                Email
              </Link>
              <Link href={COMPANY.phoneHref} underline="hover" color="text.secondary" variant="body2">
                Phone
              </Link>
            </Stack>
          </Box>
          <Box>
            <Typography variant="subtitle2" sx={{ mb: 1.25 }}>
              Legal & Support
            </Typography>
            <Stack spacing={0.75}>
              <Link
                component={RouterLink}
                to={PATHS.privacy}
                underline="hover"
                color="text.secondary"
                variant="body2"
              >
                Privacy Policy
              </Link>
              <Link
                component={RouterLink}
                to={PATHS.terms}
                underline="hover"
                color="text.secondary"
                variant="body2"
              >
                Terms of Service
              </Link>
              <Link href="#contact" underline="hover" color="text.secondary" variant="body2">
                24/7 Technical Support
              </Link>
            </Stack>
          </Box>
        </Box>
        <Box sx={{ borderTop: '1px solid', borderColor: 'divider', pt: 2.5 }}>
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            justifyContent="space-between"
            spacing={1.5}
          >
            <Typography variant="body2" color="text.secondary">
              © {new Date().getFullYear()} {COMPANY.legalName}
            </Typography>
            {health?.success ? (
              <Typography variant="caption" color="text.secondary">
                API connected · {health.data?.service || 'Business Billing API'}
              </Typography>
            ) : null}
          </Stack>
          {error ? (
            <Typography variant="caption" color="warning.main" display="block" sx={{ mt: 1.5 }}>
              {error}
            </Typography>
          ) : null}
        </Box>
      </Box>
    </Box>
  );
}
