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
import { Link as RouterLink, useNavigate, useSearchParams } from 'react-router-dom';
import { resetPasswordRequest } from '../../services/authService';

export default function ResetPasswordPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const token = params.get('token') || '';
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const onSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSuccess('');
    if (!token) {
      setError('Reset token is missing from the link.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Password and confirm password do not match');
      return;
    }
    setLoading(true);
    try {
      const response = await resetPasswordRequest({
        token,
        password,
        confirm_password: confirmPassword,
      });
      setSuccess(response.data?.message || 'Password updated successfully.');
      setTimeout(() => navigate('/login', { replace: true }), 1500);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to reset password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Stack spacing={2.5} component="form" onSubmit={onSubmit}>
      {error ? <Alert severity="error">{error}</Alert> : null}
      {success ? <Alert severity="success">{success}</Alert> : null}
      <TextField
        label="New Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
        fullWidth
        autoComplete="new-password"
      />
      <TextField
        label="Confirm New Password"
        type="password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        required
        fullWidth
        autoComplete="new-password"
      />
      <Button
        type="submit"
        variant="contained"
        fullWidth
        disabled={loading || Boolean(success)}
        startIcon={loading ? <CircularProgress size={16} color="inherit" /> : null}
      >
        Update Password
      </Button>
      <Typography variant="body2">
        <Link component={RouterLink} to="/login">
          Back to Login
        </Link>
      </Typography>
    </Stack>
  );
}
