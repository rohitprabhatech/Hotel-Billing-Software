import {
  Alert,
  Button,
  CircularProgress,
  Link,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useState } from 'react';
import { Link as RouterLink, Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { loginRequest } from '../../services/authService';
import { homePathForRole, isValidRole } from '../../utils/authRouting';

export default function LoginPage() {
  const { isAuthenticated, role, login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  if (isAuthenticated && isValidRole(role)) {
    return <Navigate to={homePathForRole(role)} replace />;
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
      navigate(homePathForRole(response.data.user.role), { replace: true });
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
    <Stack spacing={2.5} component="form" onSubmit={onSubmit}>
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
        fullWidth
        disabled={loading}
        startIcon={loading ? <CircularProgress size={16} color="inherit" /> : null}
      >
        Login
      </Button>
      <Typography variant="body2">
        <Link component={RouterLink} to="/forgot-password">
          Forgot Password?
        </Link>
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Don&apos;t have an account?{' '}
        <Link component={RouterLink} to="/register">
          Register Business
        </Link>
      </Typography>
    </Stack>
  );
}
