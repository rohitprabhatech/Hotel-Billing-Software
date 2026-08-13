import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Divider,
  Grid,
  Link,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useState } from 'react';
import { Link as RouterLink, Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { registerHotelRequest } from '../../services/authService';
import { homePathForRole, isValidRole } from '../../utils/authRouting';

const initial = {
  hotel_name: '',
  business_name: '',
  address: '',
  city: '',
  state: '',
  pincode: '',
  mobile: '',
  email: '',
  gst_number: '',
  fssai_number: '',
  owner_name: '',
  owner_email: '',
  password: '',
  confirm_password: '',
};

export default function RegisterHotelPage() {
  const { isAuthenticated, role } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState(initial);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  if (isAuthenticated && isValidRole(role)) {
    return <Navigate to={homePathForRole(role)} replace />;
  }

  const onChange = (field) => (event) => {
    setForm((prev) => ({ ...prev, [field]: event.target.value }));
  };

  const onSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSuccess('');
    if (form.password !== form.confirm_password) {
      setError('Password and confirm password do not match');
      return;
    }
    setLoading(true);
    try {
      const payload = {
        ...form,
        business_name: form.business_name || form.hotel_name,
        email: form.email || form.owner_email,
      };
      const response = await registerHotelRequest(payload);
      if (!response.success) {
        throw new Error(response.error?.message || 'Registration failed');
      }
      const msg =
        response.data?.message ||
        'Hotel registered. Please verify your email, then sign in.';
      if (response.data?.verification_token) {
        setSuccess(
          `${msg} Dev verify link ready — open Verify Email with the issued token.`
        );
        setTimeout(
          () =>
            navigate(
              `/verify-email?token=${encodeURIComponent(response.data.verification_token)}`,
              { replace: true }
            ),
          900
        );
      } else {
        setSuccess(msg);
        setTimeout(() => navigate('/login', { replace: true }), 1800);
      }
    } catch (err) {
      setError(
        err.response?.data?.error?.message ||
          err.message ||
          'Unable to register hotel'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Stack spacing={2.5} component="form" onSubmit={onSubmit}>
      <Box>
        <Typography variant="h5" fontWeight={700}>
          Create Your Hotel
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Register your hotel to get a private billing workspace.
        </Typography>
      </Box>

      {error ? <Alert severity="error">{error}</Alert> : null}
      {success ? <Alert severity="success">{success}</Alert> : null}

      <Typography variant="subtitle2" color="text.secondary">
        Hotel Information
      </Typography>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, sm: 6 }}>
          <TextField label="Hotel Name" value={form.hotel_name} onChange={onChange('hotel_name')} required fullWidth />
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <TextField label="Business Name" value={form.business_name} onChange={onChange('business_name')} fullWidth />
        </Grid>
        <Grid size={{ xs: 12 }}>
          <TextField label="Address" value={form.address} onChange={onChange('address')} fullWidth />
        </Grid>
        <Grid size={{ xs: 12, sm: 4 }}>
          <TextField label="City" value={form.city} onChange={onChange('city')} fullWidth />
        </Grid>
        <Grid size={{ xs: 12, sm: 4 }}>
          <TextField label="State" value={form.state} onChange={onChange('state')} fullWidth />
        </Grid>
        <Grid size={{ xs: 12, sm: 4 }}>
          <TextField label="Pincode" value={form.pincode} onChange={onChange('pincode')} fullWidth />
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <TextField label="Mobile Number" value={form.mobile} onChange={onChange('mobile')} fullWidth />
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <TextField
            label="Hotel Email (optional)"
            type="email"
            value={form.email}
            onChange={onChange('email')}
            fullWidth
            helperText="Defaults to owner email if left blank"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <TextField label="GST Number (optional)" value={form.gst_number} onChange={onChange('gst_number')} fullWidth />
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <TextField label="FSSAI Number (optional)" value={form.fssai_number} onChange={onChange('fssai_number')} fullWidth />
        </Grid>
      </Grid>

      <Divider />

      <Typography variant="subtitle2" color="text.secondary">
        Owner Information
      </Typography>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, sm: 6 }}>
          <TextField label="Owner Name" value={form.owner_name} onChange={onChange('owner_name')} required fullWidth />
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <TextField
            label="Owner Email"
            type="email"
            value={form.owner_email}
            onChange={onChange('owner_email')}
            required
            fullWidth
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <TextField
            label="Password"
            type="password"
            value={form.password}
            onChange={onChange('password')}
            required
            fullWidth
            autoComplete="new-password"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <TextField
            label="Confirm Password"
            type="password"
            value={form.confirm_password}
            onChange={onChange('confirm_password')}
            required
            fullWidth
            autoComplete="new-password"
          />
        </Grid>
      </Grid>

      <Button
        type="submit"
        variant="contained"
        size="large"
        disabled={loading || Boolean(success)}
        startIcon={loading ? <CircularProgress size={16} color="inherit" /> : null}
      >
        Create Hotel Account
      </Button>

      <Typography variant="body2" color="text.secondary">
        Already have an account?{' '}
        <Link component={RouterLink} to="/login">
          Login
        </Link>
      </Typography>
    </Stack>
  );
}
