import {
  Alert,
  Button,
  CircularProgress,
  IconButton,
  InputAdornment,
  Link,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import VisibilityOutlinedIcon from '@mui/icons-material/VisibilityOutlined';
import VisibilityOffOutlinedIcon from '@mui/icons-material/VisibilityOffOutlined';
import { useState } from 'react';
import { Link as RouterLink, Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { loginRequest } from '../../services/authService';
import { getApiErrorMessage } from '../../utils/apiError';
import { homePathForRole, isValidRole } from '../../utils/authRouting';

export default function LoginPage() {
  const { isAuthenticated, role, login } = useAuth();
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
      if (!response.success) {
        throw new Error(response.error?.message || 'Login failed');
      }
      login(response.data.access_token, response.data.user);
      navigate(homePathForRole(response.data.user.role), { replace: true });
    } catch (err) {
      setError(getApiErrorMessage(err, 'Unable to sign in. Check your email and password.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Stack spacing={2.25} component="form" onSubmit={onSubmit} noValidate>
      {error ? <Alert severity="error">{error}</Alert> : null}
      <TextField
        label="Email"
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
      <Stack direction="row" justifyContent="flex-end">
        <Typography variant="body2">
          <Link component={RouterLink} to="/forgot-password" underline="hover" fontWeight={600}>
            Forgot password?
          </Link>
        </Typography>
      </Stack>
      <Button
        type="submit"
        variant="contained"
        fullWidth
        size="large"
        disabled={loading}
        sx={{ py: 1.25, mt: 0.5 }}
        startIcon={loading ? <CircularProgress size={16} color="inherit" /> : null}
      >
        {loading ? 'Signing in…' : 'Sign in'}
      </Button>
    </Stack>
  );
}
