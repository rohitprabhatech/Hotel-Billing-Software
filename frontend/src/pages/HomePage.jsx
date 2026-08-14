import {
  Alert,
  Box,
  Button,
  Link,
  Stack,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { Link as RouterLink, Navigate } from 'react-router-dom';
import { COMPANY } from '../constants/company';
import SubscriptionPlanInfo from '../components/SubscriptionPlanInfo';
import ThemeModeToggle from '../components/ThemeModeToggle';
import { useAuth } from '../context/AuthContext';
import { useColorMode } from '../context/ColorModeContext';
import { fetchHealth } from '../services/healthService';
import { PATHS } from '../routes/paths';
import { homePathForRole, isValidRole } from '../utils/authRouting';

const NAV_LINKS = [
  { href: '#features', label: 'Features' },
  { href: '#modules', label: 'Modules' },
  { href: '#businesses', label: 'Businesses' },
  { href: '#pricing', label: 'Pricing' },
  { href: '#contact', label: 'Contact' },
];

const FEATURES = [
  {
    title: 'Multi-business ready',
    body: 'Restaurants, hotels, clothing, grocery, pharmacy, and more — one billing platform.',
  },
  {
    title: 'Fast counter billing',
    body: 'Search items, build a cart, apply discount, pick Cash or Online, and generate in seconds.',
  },
  {
    title: 'Owner control',
    body: 'Catalog, users, reports, audit trail, and AI insights stay scoped to your business.',
  },
];

const MODULES = [
  'Billing counter',
  'Items & categories',
  'Bill history & print',
  'Sales reports',
  'AI assistant',
  'Audit & activity',
];

const BUSINESSES = [
  'Restaurant',
  'Hotel',
  'Clothing store',
  'Grocery',
  'Pharmacy',
  'Salon',
  'Cafe',
  'General retail',
];

const HERO_IMAGE =
  'https://images.unsplash.com/photo-1556740738-b6a63e27c4df?auto=format&fit=crop&w=1800&q=80';

function Section({ id, eyebrow, title, body, children, invert = false }) {
  return (
    <Box
      id={id}
      component="section"
      sx={{
        px: { xs: 2.5, md: 6 },
        py: { xs: 7, md: 10 },
        bgcolor: invert ? 'action.hover' : 'transparent',
      }}
    >
      <Box sx={{ maxWidth: 1080, mx: 'auto' }}>
        {eyebrow ? (
          <Typography
            variant="overline"
            sx={{ color: 'primary.main', letterSpacing: '0.12em', fontWeight: 700 }}
          >
            {eyebrow}
          </Typography>
        ) : null}
        <Typography
          variant="h3"
          component="h2"
          sx={{
            mt: eyebrow ? 1 : 0,
            mb: 1.5,
            fontFamily: '"Sora", "Source Sans 3", sans-serif',
            fontWeight: 650,
            fontSize: { xs: '1.75rem', md: '2.25rem' },
            letterSpacing: '-0.03em',
            maxWidth: 640,
          }}
        >
          {title}
        </Typography>
        {body ? (
          <Typography color="text.secondary" sx={{ mb: 4, maxWidth: 560, fontSize: '1.05rem' }}>
            {body}
          </Typography>
        ) : null}
        {children}
      </Box>
    </Box>
  );
}

export default function HomePage() {
  const { isAuthenticated, role } = useAuth();
  const { isDark } = useColorMode();
  const [health, setHealth] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    fetchHealth()
      .then((payload) => {
        if (active) setHealth(payload);
      })
      .catch(() => {
        if (active) setError('API offline — start the backend to connect live data.');
      });
    return () => {
      active = false;
    };
  }, []);

  if (isAuthenticated && isValidRole(role)) {
    return <Navigate to={homePathForRole(role)} replace />;
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        bgcolor: 'background.default',
        color: 'text.primary',
        '@keyframes landingFadeUp': {
          from: { opacity: 0, transform: 'translateY(18px)' },
          to: { opacity: 1, transform: 'translateY(0)' },
        },
        '@keyframes landingPan': {
          from: { transform: 'scale(1.06)' },
          to: { transform: 'scale(1)' },
        },
        '@media (prefers-reduced-motion: reduce)': {
          '& *': {
            animation: 'none !important',
          },
        },
      }}
    >
      <Box
        component="header"
        sx={{
          position: 'sticky',
          top: 0,
          zIndex: 20,
          backdropFilter: 'blur(10px)',
          bgcolor: isDark ? 'rgba(15, 22, 28, 0.88)' : 'rgba(243, 245, 247, 0.88)',
          borderBottom: '1px solid',
          borderColor: 'divider',
        }}
      >
        <Stack
          direction="row"
          alignItems="center"
          justifyContent="space-between"
          spacing={2}
          sx={{ px: { xs: 2, md: 4 }, py: 1.5, maxWidth: 1200, mx: 'auto' }}
        >
          <Typography
            component={RouterLink}
            to={PATHS.home}
            sx={{
              fontFamily: '"Sora", "Source Sans 3", sans-serif',
              fontWeight: 700,
              fontSize: '1.05rem',
              color: 'inherit',
              textDecoration: 'none',
              letterSpacing: '-0.02em',
            }}
          >
            {COMPANY.productName}
          </Typography>
          <Stack
            direction="row"
            spacing={2.5}
            sx={{ display: { xs: 'none', md: 'flex' } }}
          >
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                underline="none"
                color="text.secondary"
                sx={{ fontSize: '0.9rem', fontWeight: 600, '&:hover': { color: 'primary.main' } }}
              >
                {link.label}
              </Link>
            ))}
          </Stack>
          <Stack direction="row" spacing={1} alignItems="center">
            <ThemeModeToggle size="small" />
            <Button component={RouterLink} to={PATHS.login} color="inherit" size="small">
              Login
            </Button>
            <Button component={RouterLink} to={PATHS.register} variant="contained" size="small">
              Register Business
            </Button>
          </Stack>
        </Stack>
      </Box>

      {/* Hero — brand first, one composition, full-bleed visual */}
      <Box
        component="section"
        sx={{
          position: 'relative',
          minHeight: { xs: '88vh', md: '92vh' },
          display: 'flex',
          alignItems: 'flex-end',
          overflow: 'hidden',
          color: '#fff',
        }}
      >
        <Box
          aria-hidden
          sx={{
            position: 'absolute',
            inset: 0,
            backgroundImage: `linear-gradient(105deg, rgba(15, 36, 44, 0.88) 0%, rgba(15, 36, 44, 0.55) 48%, rgba(15, 36, 44, 0.25) 100%), url(${HERO_IMAGE})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            animation: 'landingPan 12s ease-out both',
          }}
        />
        <Box
          sx={{
            position: 'relative',
            zIndex: 1,
            width: '100%',
            maxWidth: 1200,
            mx: 'auto',
            px: { xs: 2.5, md: 6 },
            pb: { xs: 7, md: 10 },
            pt: { xs: 14, md: 16 },
            animation: 'landingFadeUp 0.9s ease-out both',
          }}
        >
          <Typography
            component="p"
            sx={{
              fontFamily: '"Sora", "Source Sans 3", sans-serif',
              fontWeight: 700,
              fontSize: { xs: '2.6rem', sm: '3.5rem', md: '4.5rem' },
              lineHeight: 0.95,
              letterSpacing: '-0.04em',
              maxWidth: 720,
              mb: 2,
            }}
          >
            {COMPANY.productName}
          </Typography>
          <Typography
            sx={{
              fontSize: { xs: '1.15rem', md: '1.35rem' },
              maxWidth: 460,
              opacity: 0.92,
              mb: 3.5,
              lineHeight: 1.45,
            }}
          >
            {COMPANY.tagline}
          </Typography>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
            <Button
              component={RouterLink}
              to={PATHS.register}
              variant="contained"
              size="large"
              sx={{
                bgcolor: '#fff',
                color: 'primary.dark',
                '&:hover': { bgcolor: 'rgba(255,255,255,0.92)' },
                animation: 'landingFadeUp 1s ease-out 0.15s both',
              }}
            >
              Register Business
            </Button>
            <Button
              component={RouterLink}
              to={PATHS.login}
              variant="outlined"
              size="large"
              sx={{
                borderColor: 'rgba(255,255,255,0.7)',
                color: '#fff',
                '&:hover': { borderColor: '#fff', bgcolor: 'rgba(255,255,255,0.08)' },
                animation: 'landingFadeUp 1s ease-out 0.28s both',
              }}
            >
              Login
            </Button>
          </Stack>
        </Box>
      </Box>

      <Section
        id="features"
        eyebrow="Features"
        title="Built for the counter and the owner desk"
        body="Everything your staff needs to bill quickly — and everything you need to stay in control."
      >
        <Box
          sx={{
            display: 'grid',
            gap: { xs: 4, md: 5 },
            gridTemplateColumns: { xs: '1fr', md: 'repeat(3, 1fr)' },
          }}
        >
          {FEATURES.map((feature) => (
            <Box key={feature.title}>
              <Typography
                variant="h6"
                sx={{ fontFamily: '"Sora", "Source Sans 3", sans-serif', mb: 1 }}
              >
                {feature.title}
              </Typography>
              <Typography color="text.secondary">{feature.body}</Typography>
            </Box>
          ))}
        </Box>
      </Section>

      <Section
        id="modules"
        invert
        eyebrow="Modules"
        title="One product, clear modules"
        body="From catalog setup to AI analysis — each area has a single job."
      >
        <Box
          sx={{
            display: 'grid',
            gap: 2,
            gridTemplateColumns: { xs: '1fr 1fr', md: 'repeat(3, 1fr)' },
          }}
        >
          {MODULES.map((name) => (
            <Typography
              key={name}
              sx={{
                py: 2,
                borderTop: '1px solid',
                borderColor: 'divider',
                fontWeight: 600,
              }}
            >
              {name}
            </Typography>
          ))}
        </Box>
      </Section>

      <Section
        id="businesses"
        eyebrow="Supported businesses"
        title="Not just hotels"
        body="Register with a business type that matches how you sell — terminology and optional licenses adapt accordingly."
      >
        <Stack direction="row" useFlexGap flexWrap="wrap" spacing={1.25}>
          {BUSINESSES.map((name) => (
            <Box
              key={name}
              sx={{
                px: 1.75,
                py: 1,
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1,
                bgcolor: 'background.paper',
                fontWeight: 600,
                fontSize: '0.9rem',
              }}
            >
              {name}
            </Box>
          ))}
        </Stack>
      </Section>

      <Section
        id="billing"
        invert
        eyebrow="Billing"
        title="Counter billing without the clutter"
        body="Search by name or SKU, adjust quantity, remove lines from the cart (not your catalog), apply discount, choose Cash or Online, then generate and print."
      />

      <Section
        id="reports"
        eyebrow="Reports"
        title="Know today’s numbers"
        body="Daily, weekly, monthly, and custom sales with cash/online split, top items, category sales, and exports — owner-only and tenant-scoped."
      />

      <Section
        id="ai"
        invert
        eyebrow="AI"
        title="Assistant grounded in your sales"
        body="The AI Business Assistant reads only your finalized bills. Insights and recommendations never invent metrics — and say so when history is thin."
      />

      <Section
        id="security"
        eyebrow="Security"
        title="Tenant walls by design"
        body="JWT sessions, role guards, soft-cancel bills, append-only audit logs, and isolation so one business never sees another’s data."
      />

      <Section
        id="pricing"
        invert
        eyebrow="Subscription"
        title={`${COMPANY.planPriceLabel} — simple plan`}
        body="One clear monthly price for Business Billing. No online checkout here — register or contact us to subscribe."
      >
        <SubscriptionPlanInfo variant="public" showPublicCtas />
      </Section>

      <Section
        id="contact"
        eyebrow="Contact & support"
        title="Talk to Prabha Technology"
        body={COMPANY.supportNote}
      >
        <Box
          sx={{
            display: 'grid',
            gap: 4,
            gridTemplateColumns: { xs: '1fr', md: '1.2fr 1fr' },
          }}
        >
          <Box>
            <Typography
              sx={{ fontFamily: '"Sora", "Source Sans 3", sans-serif', fontWeight: 700, mb: 1 }}
            >
              {COMPANY.legalName}
            </Typography>
            {COMPANY.addressLines.map((line) => (
              <Typography key={line} color="text.secondary">
                {line}
              </Typography>
            ))}
          </Box>
          <Stack spacing={1}>
            <Typography>
              Email:{' '}
              <Link href={COMPANY.emailHref} fontWeight={600}>
                {COMPANY.email}
              </Link>
            </Typography>
            <Typography>
              Phone:{' '}
              <Link href={COMPANY.phoneHref} fontWeight={600}>
                {COMPANY.phone}
              </Link>
            </Typography>
            <Typography color="text.secondary" sx={{ pt: 1 }}>
              24/7 Support for billing outages, access issues, and onboarding help.
            </Typography>
            <Stack direction="row" spacing={1.5} sx={{ pt: 1 }}>
              <Button component={RouterLink} to={PATHS.register} variant="contained">
                Register Business
              </Button>
              <Button component={RouterLink} to={PATHS.login} variant="outlined">
                Login
              </Button>
            </Stack>
          </Stack>
        </Box>
      </Section>

      <Box
        component="footer"
        sx={{
          borderTop: '1px solid',
          borderColor: 'divider',
          px: { xs: 2.5, md: 6 },
          py: 4,
          bgcolor: 'action.hover',
        }}
      >
        <Box sx={{ maxWidth: 1080, mx: 'auto' }}>
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            justifyContent="space-between"
            spacing={2}
          >
            <Box>
              <Typography fontWeight={700}>{COMPANY.productName}</Typography>
              <Typography variant="body2" color="text.secondary">
                A product of {COMPANY.legalName}
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              © {new Date().getFullYear()} {COMPANY.legalName}
            </Typography>
          </Stack>
          {health?.success ? (
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2 }}>
              API connected · {health.data?.service || 'Business Billing API'}
            </Typography>
          ) : null}
          {error ? (
            <Alert severity="warning" sx={{ mt: 2 }}>
              {error}
            </Alert>
          ) : null}
        </Box>
      </Box>
    </Box>
  );
}
