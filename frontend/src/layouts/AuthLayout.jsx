import { Box, Container, Paper, Typography } from '@mui/material';
import { Outlet } from 'react-router-dom';

export default function AuthLayout() {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        background:
          'linear-gradient(160deg, #E8EEF2 0%, #F3F5F7 45%, #E4EBE7 100%)',
      }}
    >
      <Container maxWidth="sm">
        <Paper sx={{ p: 4 }}>
          <Typography variant="h5" gutterBottom>
            Hotel Billing Software
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Sign in to continue
          </Typography>
          <Outlet />
        </Paper>
      </Container>
    </Box>
  );
}