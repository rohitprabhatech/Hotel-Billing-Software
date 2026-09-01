import { Box, Container, Paper, Typography } from '@mui/material';
import { Outlet, useLocation } from 'react-router-dom';
import BrandLogo from '../components/BrandLogo';
import ThemeModeToggle from '../components/ThemeModeToggle';
import RouteErrorBoundary from '../components/RouteErrorBoundary';
import { COMPANY } from '../constants/company';
import { useColorMode } from '../context/ColorModeContext';

const pages = {
  '/login': {
    overline: 'Business Billing Software',
    title: 'Sign in',
    subtitle: 'Access your business billing workspace',
  },
  '/master/login': {
    overline: 'Master Admin Console',
    title: 'Sign in',
    subtitle: 'Prabha Technology platform administration — manage businesses, plans, and subscriptions.',
    showBrandLogo: true,
  },
  '/register': {
    title: 'Register Business',
    subtitle: 'Create your business workspace',
  },
  '/forgot-password': {
    title: 'Forgot Password',
    subtitle: 'Enter your account email and we will send a secure reset link.',
  },
  '/reset-password': {
    title: 'Reset Password',
    subtitle: 'Choose a new password',
  },
  '/verify-email': {
    title: 'Verify Email',
    subtitle: 'Activate your account',
  },
};

export default function AuthLayout() {
  const { pathname } = useLocation();
  const { isDark } = useColorMode();
  const meta = pages[pathname] || {
    overline: 'Business Billing Software',
    title: 'Business Billing Software',
    subtitle: '',
  };
  const wide = pathname === '/register';
  const isMasterLogin = pathname === '/master/login';

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: { xs: 'flex-start', sm: 'center' },
        position: 'relative',
        py: { xs: 3, sm: 4 },
        px: { xs: 2, sm: 0 },
        background: isMasterLogin
          ? isDark
            ? `linear-gradient(160deg, ${COMPANY.brandColor} 0%, #0F161C 55%, #152028 100%)`
            : `linear-gradient(160deg, #E8EEF2 0%, #DDE8F0 45%, #E4EBE7 100%)`
          : isDark
            ? 'linear-gradient(160deg, #0B1218 0%, #0F161C 45%, #152028 100%)'
            : 'linear-gradient(160deg, #E8EEF2 0%, #F3F5F7 45%, #E4EBE7 100%)',
      }}
    >
      <Box sx={{ position: 'absolute', top: 12, right: 12, zIndex: 2 }}>
        <ThemeModeToggle />
      </Box>
      <Container maxWidth={wide ? 'md' : 'sm'} disableGutters={false}>
        <Paper
          elevation={0}
          sx={{
            p: { xs: 2.5, sm: 3.5 },
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 3,
            boxShadow: isDark
              ? '0 1px 2px rgba(0, 0, 0, 0.35)'
              : '0 1px 2px rgba(26, 35, 48, 0.04)',
          }}
        >
          {meta.showBrandLogo ? (
            <Box sx={{ mb: 2 }}>
              <BrandLogo size={52} title={COMPANY.legalName} subtitle={null} />
            </Box>
          ) : (
            <Typography variant="overline" color="primary" letterSpacing={1.2}>
              {meta.overline || 'Business Billing Software'}
            </Typography>
          )}
          {meta.showBrandLogo ? (
            <Typography variant="overline" color="primary" letterSpacing={1.2} sx={{ display: 'block' }}>
              {meta.overline}
            </Typography>
          ) : null}
          <Typography
            variant="h5"
            component="h1"
            sx={{ mt: 0.5, fontWeight: 700, fontSize: { xs: '1.35rem', sm: '1.5rem' } }}
          >
            {meta.title}
          </Typography>
          {meta.subtitle ? (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.75, mb: 3 }}>
              {meta.subtitle}
            </Typography>
          ) : (
            <Box sx={{ mb: 3 }} />
          )}
          <RouteErrorBoundary key={pathname}>
            <Outlet />
          </RouteErrorBoundary>
        </Paper>
      </Container>
    </Box>
  );
}
