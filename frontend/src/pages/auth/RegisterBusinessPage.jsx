import {
  Alert,
  Button,
  CircularProgress,
  Divider,
  FormControl,
  Grid,
  InputLabel,
  Link,
  MenuItem,
  Select,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { Link as RouterLink, Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { registerBusinessRequest } from '../../services/authService';
import { fetchBusinessTypes } from '../../services/tenantService';
import { homePathForRole, isValidRole } from '../../utils/authRouting';

const initial = {
  business_name: '',
  business_type: 'other',
  address: '',
  city: '',
  state: '',
  pincode: '',
  mobile: '',
  gst_number: '',
  fssai_number: '',
  owner_name: '',
  owner_email: '',
  password: '',
  confirm_password: '',
};

export default function RegisterBusinessPage() {
  const { isAuthenticated, role } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState(initial);
  const [businessTypes, setBusinessTypes] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchBusinessTypes()
      .then((res) => setBusinessTypes(res.data?.business_types || []))
      .catch(() => setBusinessTypes([]));
  }, []);

  if (isAuthenticated && isValidRole(role)) {
    return <Navigate to={homePathForRole(role)} replace />;
  }

  const onChange = (field) => (event) => {
    setForm((prev) => ({ ...prev, [field]: event.target.value }));
  };

  const selectedType = businessTypes.find((row) => row.code === form.business_type);
  const showFssai = selectedType?.fssai_relevant ?? false;

  const onSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSuccess('');
    if (!form.business_name.trim()) {
      setError('Business name is required');
      return;
    }
    if (form.password !== form.confirm_password) {
      setError('Password and confirm password do not match');
      return;
    }
    setLoading(true);
    try {
      const payload = {
        business_name: form.business_name.trim(),
        name: form.business_name.trim(),
        business_type: form.business_type,
        address: form.address,
        city: form.city,
        state: form.state,
        pincode: form.pincode,
        mobile: form.mobile,
        owner_name: form.owner_name,
        owner_email: form.owner_email,
        password: form.password,
        confirm_password: form.confirm_password,
        email: form.owner_email,
        fssai_number: showFssai ? form.fssai_number || '' : '',
        gst_number: form.gst_number || '',
      };
      const response = await registerBusinessRequest(payload);
      if (!response.success) {
        throw new Error(response.error?.message || 'Registration failed');
      }
      const msg =
        response.data?.message ||
        'Business registered. Please verify your email, then sign in.';
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
          'Unable to register business'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Stack spacing={2.5} component="form" onSubmit={onSubmit}>
      {error ? <Alert severity="error">{error}</Alert> : null}
      {success ? <Alert severity="success">{success}</Alert> : null}

      <Typography variant="subtitle2" color="text.secondary">
        Business Details
      </Typography>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, sm: 6 }}>
          <TextField
            label="Business Name"
            value={form.business_name}
            onChange={onChange('business_name')}
            required
            fullWidth
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <FormControl fullWidth required>
            <InputLabel id="business-type-label">Business Type</InputLabel>
            <Select
              labelId="business-type-label"
              label="Business Type"
              value={form.business_type}
              onChange={onChange('business_type')}
            >
              {businessTypes.map((row) => (
                <MenuItem key={row.code} value={row.code}>
                  {row.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid size={{ xs: 12 }}>
          <TextField
            label="Business Address"
            value={form.address}
            onChange={onChange('address')}
            fullWidth
            multiline
            minRows={2}
          />
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
          <TextField
            label="Mobile"
            value={form.mobile}
            onChange={onChange('mobile')}
            required
            fullWidth
          />
        </Grid>
        {showFssai ? (
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              label="FSSAI Number (optional)"
              value={form.fssai_number || ''}
              onChange={onChange('fssai_number')}
              fullWidth
            />
          </Grid>
        ) : null}
      </Grid>

      <Divider />

      <Typography variant="subtitle2" color="text.secondary">
        Owner Account
      </Typography>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, sm: 6 }}>
          <TextField
            label="Owner Name"
            value={form.owner_name}
            onChange={onChange('owner_name')}
            required
            fullWidth
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <TextField
            label="Email"
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
        fullWidth
        disabled={loading || Boolean(success)}
        startIcon={loading ? <CircularProgress size={16} color="inherit" /> : null}
      >
        Register Business
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
