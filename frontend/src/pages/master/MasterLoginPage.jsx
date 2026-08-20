import {
  Alert,
  Button,
  CircularProgress,
  Stack,
  TextField,
} from '@mui/material';
import { useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { loginRequest } from '../../services/authService';
import { PATHS } from '../../routes/paths';
import { homePathForRole, isValidRole } from '../../utils/authRouting';

const GENERIC_ERROR = 'Invalid email or password';

export default function MasterLoginPage() {
  const { isAuthenticated, role, login, logout } = useAuth();
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
      const user = response?.data?.user;
      const token = response?.data?.access_token;
      if (!response.success || !token || !user) {
        throw new Error(GENERIC_ERROR);
      }
      if (user.role !== 'MASTER_ADMIN') {
        logout();
        setError(GENERIC_ERROR);
        return;
      }
      login(token, user);
      navigate(PATHS.masterDashboard, { replace: true });
    } catch (err) {
      const status = err.response?.status;
      const message =
        status === 401 || status === 403
          ? GENERIC_ERROR
          : err.response?.data?.error?.message || err.message || GENERIC_ERROR;
      setError(message === 'Login failed' ? GENERIC_ERROR : message);
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
        Sign In
      </Button>
    </Stack>
  );
}
