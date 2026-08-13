import { Box, Container, Paper, Typography } from '@mui/material';
import { Outlet, useLocation } from 'react-router-dom';

const titles = {
  '/login': 'Sign in to continue',
  '/register': 'Create your hotel workspace',
  '/forgot-password': 'Recover account access',
  '/reset-password': 'Choose a new password',
  '/verify-email': 'Activate your account',
};

export default function AuthLayout() {
  const { pathname } = useLocation();
  const subtitle = titles[pathname] || 'Hotel Billing Software';
  const wide = pathname === '/register';

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        py: 4,
        background:
          'linear-gradient(160deg, #E8EEF2 0%, #F3F5F7 45%, #E4EBE7 100%)',
      }}
    >
      <Container maxWidth={wide ? 'md' : 'sm'}>
        <Paper sx={{ p: { xs: 3, sm: 4 } }}>
          <Typography variant="overline" color="primary" letterSpacing={1.2}>
            Hotel Billing Software
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            {subtitle}
          </Typography>
          <Outlet />
        </Paper>
      </Container>
    </Box>
  );
}
