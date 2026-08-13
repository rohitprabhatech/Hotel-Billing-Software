import {
  Alert,
  Button,
  CircularProgress,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { loginRequest } from '../../services/authService';

export default function LoginPage() {
  const { isAuthenticated, role, login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('owner@hotela.com');
  const [password, setPassword] = useState('Owner@12345');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) {
    return (
      <Navigate
        to={role === 'OWNER' ? '/owner/dashboard' : '/billing'}
        replace
      />
    );
  }

  const onSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);
    try {
      const response = await loginRequest(email, password);
      if (!response.success) {
        throw new Error(response.error?.message || 'Login failed');
      }
      login(response.data.access_token, response.data.user);
      navigate(
        response.data.user.role === 'OWNER' ? '/owner/dashboard' : '/billing',
        { replace: true },
      );
    } catch (err) {
      const message =
        err.response?.data?.error?.message ||
        err.message ||
        'Unable to sign in';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Stack spacing={2} component="form" onSubmit={onSubmit}>
      {error ? <Alert severity="error">{error}</Alert> : null}
      <TextField
        label="Email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        fullWidth
        required
        autoComplete="username"
      />
      <TextField
        label="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        fullWidth
        required
        autoComplete="current-password"
      />
      <Button
        type="submit"
        variant="contained"
        size="large"
        disabled={loading}
        startIcon={loading ? <CircularProgress size={16} color="inherit" /> : null}
      >
        Sign in
      </Button>
      <Typography variant="caption" color="text.secondary">
        Demo: owner@hotela.com / Owner@12345 or billing@hotela.com / Billing@12345
      </Typography>
    </Stack>
  );
}