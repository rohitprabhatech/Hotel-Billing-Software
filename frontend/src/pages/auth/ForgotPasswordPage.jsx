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
import { Link as RouterLink } from 'react-router-dom';
import { forgotPasswordRequest } from '../../services/authService';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const onSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);
    try {
      const response = await forgotPasswordRequest(email);
      setSuccess(
        response.data?.message ||
          'If the account exists, a password reset email has been sent.'
      );
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to send reset email');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Stack spacing={2.5} component="form" onSubmit={onSubmit}>
      {error ? <Alert severity="error">{error}</Alert> : null}
      {success ? <Alert severity="success">{success}</Alert> : null}
      <TextField
        label="Email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
        fullWidth
      />
      <Button
        type="submit"
        variant="contained"
        fullWidth
        disabled={loading}
        startIcon={loading ? <CircularProgress size={16} color="inherit" /> : null}
      >
        Send Reset Link
      </Button>
      <Typography variant="body2">
        <Link component={RouterLink} to="/login">
          Back to Login
        </Link>
      </Typography>
    </Stack>
  );
}
