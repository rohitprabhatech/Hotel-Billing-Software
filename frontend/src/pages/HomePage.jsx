import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Stack,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { fetchHealth } from '../services/healthService';

export default function HomePage() {
  const [health, setHealth] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    fetchHealth()
      .then((payload) => {
        if (active) setHealth(payload);
      })
      .catch(() => {
        if (active) {
          setError('API health check failed. Start the Flask backend on port 5000.');
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        px: 2,
        background:
          'linear-gradient(160deg, #E8EEF2 0%, #F3F5F7 45%, #E4EBE7 100%)',
      }}
    >
      <Card sx={{ width: '100%', maxWidth: 640 }}>
        <CardContent>
          <Typography variant="h4" gutterBottom>
            Hotel Billing Software
          </Typography>
          <Typography color="text.secondary" sx={{ mb: 2 }}>
            Multi-tenant billing foundation (Sprint 2). Choose a shell to preview
            layouts, or open login.
          </Typography>

          {loading ? <CircularProgress size={28} /> : null}
          {health?.success ? (
            <Alert severity="success" sx={{ mb: 2 }}>
              API connected: {health.data.service} ({health.data.status})
            </Alert>
          ) : null}
          {error ? (
            <Alert severity="warning" sx={{ mb: 2 }}>
              {error}
            </Alert>
          ) : null}

          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
            <Button component={RouterLink} to="/login" variant="contained">
              Login
            </Button>
            <Button component={RouterLink} to="/owner/dashboard" variant="outlined">
              Owner Shell
            </Button>
            <Button component={RouterLink} to="/billing" variant="outlined">
              Billing Shell
            </Button>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
}