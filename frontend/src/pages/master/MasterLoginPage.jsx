import {
  Alert,
  Button,
  CircularProgress,
  IconButton,
  InputAdornment,
  Stack,
  TextField,
} from '@mui/material';
import VisibilityOutlinedIcon from '@mui/icons-material/VisibilityOutlined';
import VisibilityOffOutlinedIcon from '@mui/icons-material/VisibilityOffOutlined';
import { useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { loginRequest } from '../../services/authService';
import { PATHS } from '../../routes/paths';
import { getApiErrorMessage } from '../../utils/apiError';
import { homePathForRole, isValidRole } from '../../utils/authRouting';

const GENERIC_ERROR = 'Invalid email or password';

export default function MasterLoginPage() {
  const { isAuthenticated, role, login, logout } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
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
      if (status === 401 || status === 403) {
        setError(GENERIC_ERROR);
      } else {
        const message = getApiErrorMessage(err, GENERIC_ERROR);
        setError(message === 'Login failed' ? GENERIC_ERROR : message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Stack spacing={2.25} component="form" onSubmit={onSubmit} noValidate>
      {error ? <Alert severity="error">{error}</Alert> : null}
      <TextField
        label="Admin email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        fullWidth
        required
        autoComplete="username"
        autoFocus
      />
      <TextField
        label="Password"
        type={showPassword ? 'text' : 'password'}
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        fullWidth
        required
        autoComplete="current-password"
        InputProps={{
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                onClick={() => setShowPassword((v) => !v)}
                edge="end"
                size="small"
              >
                {showPassword ? <VisibilityOffOutlinedIcon /> : <VisibilityOutlinedIcon />}
              </IconButton>
            </InputAdornment>
          ),
        }}
      />
      <Button
        type="submit"
        variant="contained"
        fullWidth
        size="large"
        disabled={loading}
        sx={{ py: 1.25, mt: 0.5 }}
        startIcon={loading ? <CircularProgress size={16} color="inherit" /> : null}
      >
        {loading ? 'Signing in…' : 'Sign in to Master'}
      </Button>
    </Stack>
  );
}
