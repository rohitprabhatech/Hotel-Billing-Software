import { Alert, Button, CircularProgress, Stack, Typography } from '@mui/material';
import { useEffect, useState } from 'react';
import { Link as RouterLink, useSearchParams } from 'react-router-dom';
import { verifyEmailRequest } from '../../services/authService';

export default function VerifyEmailPage() {
  const [params] = useSearchParams();
  const token = params.get('token') || '';
  const [status, setStatus] = useState(token ? 'loading' : 'missing');
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!token) return undefined;
    let cancelled = false;
    verifyEmailRequest(token)
      .then((res) => {
        if (cancelled) return;
        setStatus('success');
        setMessage(res.data?.message || 'Email verified successfully.');
      })
      .catch((err) => {
        if (cancelled) return;
        setStatus('error');
        setMessage(
          err.response?.data?.error?.message || 'Verification failed or link expired.'
        );
      });
    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    <Stack spacing={2}>
      <Typography variant="h5" fontWeight={700}>
        Verify Email
      </Typography>
      {status === 'loading' ? <CircularProgress size={28} /> : null}
      {status === 'missing' ? (
        <Alert severity="warning">Verification token is missing from the link.</Alert>
      ) : null}
      {status === 'success' ? <Alert severity="success">{message}</Alert> : null}
      {status === 'error' ? <Alert severity="error">{message}</Alert> : null}
      <Button component={RouterLink} to="/login" variant="contained">
        Go to Login
      </Button>
    </Stack>
  );
}
