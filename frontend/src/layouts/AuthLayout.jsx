import { Box, Button, Link, Stack, Typography } from '@mui/material';
import { Link as RouterLink, Outlet, useLocation } from 'react-router-dom';
import ThemeModeToggle from '../components/ThemeModeToggle';
import RouteErrorBoundary from '../components/RouteErrorBoundary';
import { COMPANY } from '../constants/company';
import { useColorMode } from '../context/ColorModeContext';
import { PATHS } from '../routes/paths';

const DISPLAY_FONT = '"Sora", "Source Sans 3", sans-serif';

const pages = {
  '/login': {
    overline: 'Business sign-in',
    title: 'Welcome back',
    subtitle: 'Sign in to your Business Billing workspace.',
    brandLine: 'Run billing, stock, and sales from one calm counter system.',
  },
  '/master/login': {
    overline: 'Platform access',
    title: 'Master Admin',
    subtitle: 'Sign in to the Prabha Technology control plane.',
    brandLine: 'Approve businesses, manage plans, and keep the platform healthy.',
  },
  '/register': {
    overline: 'Get started',
    title: 'Register your business',
    subtitle: 'Create a tenant workspace. Approval may be required before login.',
    brandLine: 'One product for restaurants, retail, grocery, and more.',
  },
  '/forgot-password': {
    overline: 'Account recovery',
    title: 'Forgot password',
    subtitle: 'Enter your email and we will send a secure reset link.',
    brandLine: 'We never email your password — only a time-limited reset link.',
  },
  '/reset-password': {
    overline: 'Account recovery',
    title: 'Choose a new password',
    subtitle: 'Use a strong password you have not used elsewhere.',
    brandLine: 'Protect your business data with a unique password.',
  },
  '/verify-email': {
    overline: 'Account setup',
    title: 'Verify your email',
    subtitle: 'Confirm your address to activate the account.',
    brandLine: 'Verified owners keep billing access secure.',
  },
};

export default function AuthLayout() {
  const { pathname } = useLocation();
  const { isDark } = useColorMode();
  const meta = pages[pathname] || {
    overline: COMPANY.productName,
    title: 'Continue',
    subtitle: '',
    brandLine: COMPANY.tagline,
  };
  const wide = pathname === '/register';
  const isMaster = pathname.startsWith('/master');

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'grid',
        gridTemplateColumns: { xs: '1fr', md: 'minmax(280px, 0.92fr) minmax(0, 1.08fr)' },
        position: 'relative',
        '@keyframes authRise': {
          from: { opacity: 0, transform: 'translateY(12px)' },
          to: { opacity: 1, transform: 'translateY(0)' },
        },
        '@media (prefers-reduced-motion: reduce)': {
          '& *': { animation: 'none !important' },
        },
      }}
    >
      <Box sx={{ position: 'absolute', top: 12, right: 12, zIndex: 3 }}>
        <ThemeModeToggle />
      </Box>

      {/* Brand panel — full-height visual plane */}
      <Box
        sx={{
          position: 'relative',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: { xs: 'flex-end', md: 'space-between' },
          minHeight: { xs: 200, sm: 240, md: '100vh' },
          px: { xs: 2.5, sm: 4, md: 5 },
          py: { xs: 3, md: 5 },
          color: '#F4F8FA',
          background: isMaster
            ? `
              linear-gradient(155deg, #0B1620 0%, #132633 48%, #1A3544 100%)
            `
            : `
              radial-gradient(900px 520px at 12% 18%, rgba(110,180,200,0.22), transparent 55%),
              radial-gradient(700px 480px at 88% 92%, rgba(47,107,128,0.35), transparent 50%),
              linear-gradient(155deg, #123A48 0%, #1F4E5F 46%, #163A47 100%)
            `,
          '&::after': {
            content: '""',
            position: 'absolute',
            inset: 0,
            opacity: 0.28,
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.07'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
            pointerEvents: 'none',
          },
        }}
      >
        <Stack
          spacing={1.25}
          sx={{ position: 'relative', zIndex: 1, maxWidth: 420, animation: 'authRise 0.7s ease-out both' }}
        >
          <Button
            component={RouterLink}
            to={PATHS.home}
            color="inherit"
            sx={{
              alignSelf: 'flex-start',
              px: 0,
              minWidth: 0,
              fontFamily: DISPLAY_FONT,
              fontWeight: 700,
              fontSize: '0.95rem',
              letterSpacing: '-0.02em',
              opacity: 0.95,
              '&:hover': { opacity: 1, bgcolor: 'transparent', textDecoration: 'underline' },
            }}
          >
            {COMPANY.productName}
          </Button>
          <Typography
            sx={{
              fontFamily: DISPLAY_FONT,
              fontWeight: 700,
              fontSize: { xs: '1.65rem', md: '2.05rem' },
              lineHeight: 1.15,
              letterSpacing: '-0.035em',
              display: { xs: 'none', md: 'block' },
            }}
          >
            {meta.brandLine}
          </Typography>
          <Typography
            sx={{
              fontSize: '0.92rem',
              lineHeight: 1.55,
              opacity: 0.78,
              display: { xs: 'none', md: 'block' },
              maxWidth: 360,
            }}
          >
            {COMPANY.legalName}
          </Typography>
        </Stack>

        <Typography
          sx={{
            position: 'relative',
            zIndex: 1,
            mt: { xs: 2, md: 0 },
            fontSize: '0.8rem',
            opacity: 0.65,
            display: { xs: 'none', md: 'block' },
          }}
        >
          Secure multi-tenant billing for real shops.
        </Typography>
      </Box>

      {/* Form panel */}
      <Box
        sx={{
          display: 'flex',
          alignItems: { xs: 'flex-start', sm: 'center' },
          justifyContent: 'center',
          px: { xs: 2, sm: 3.5, md: 5 },
          py: { xs: 3.5, sm: 5 },
          bgcolor: isDark ? 'background.default' : '#F7FAFB',
          backgroundImage: isDark
            ? 'none'
            : 'linear-gradient(180deg, #F7FAFB 0%, #EEF3F6 100%)',
        }}
      >
        <Box
          sx={{
            width: '100%',
            maxWidth: wide ? 720 : 420,
            animation: 'authRise 0.75s ease-out 0.08s both',
          }}
        >
          <Typography
            variant="overline"
            sx={{
              color: 'primary.main',
              letterSpacing: '0.14em',
              fontWeight: 700,
              fontSize: '0.7rem',
            }}
          >
            {meta.overline}
          </Typography>
          <Typography
            component="h1"
            sx={{
              mt: 0.75,
              fontFamily: DISPLAY_FONT,
              fontWeight: 700,
              fontSize: { xs: '1.65rem', sm: '1.85rem' },
              letterSpacing: '-0.03em',
              lineHeight: 1.15,
              color: 'text.primary',
            }}
          >
            {meta.title}
          </Typography>
          {meta.subtitle ? (
            <Typography
              sx={{
                mt: 1,
                mb: 3.25,
                color: 'text.secondary',
                fontSize: '0.95rem',
                lineHeight: 1.55,
              }}
            >
              {meta.subtitle}
            </Typography>
          ) : (
            <Box sx={{ mb: 3.25 }} />
          )}

          <RouteErrorBoundary key={pathname}>
            <Outlet />
          </RouteErrorBoundary>

          {!isMaster && pathname === '/login' ? (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 3 }}>
              New here?{' '}
              <Link component={RouterLink} to={PATHS.register} fontWeight={600}>
                Register your business
              </Link>
            </Typography>
          ) : null}

          <Typography variant="body2" sx={{ mt: 2.5 }}>
            <Link component={RouterLink} to={PATHS.home} color="text.secondary" underline="hover">
              ← Back to home
            </Link>
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}
