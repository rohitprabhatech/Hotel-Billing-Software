import { Box, Container, Paper, Typography } from '@mui/material';
import { Outlet, useLocation } from 'react-router-dom';
import ThemeModeToggle from '../components/ThemeModeToggle';
import RouteErrorBoundary from '../components/RouteErrorBoundary';
import { useColorMode } from '../context/ColorModeContext';

const pages = {
  '/login': {
    title: 'Sign in',
    subtitle: 'Access your business billing workspace',
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
    title: 'Business Billing Software',
    subtitle: '',
  };
  const wide = pathname === '/register';

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: { xs: 'flex-start', sm: 'center' },
        position: 'relative',
        py: { xs: 3, sm: 4 },
        px: { xs: 2, sm: 0 },
        background: isDark
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
          <Typography variant="overline" color="primary" letterSpacing={1.2}>
            Business Billing Software
          </Typography>
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
