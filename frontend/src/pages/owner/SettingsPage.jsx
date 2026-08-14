import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import PageShell from '../../components/PageShell';
import SubscriptionPlanInfo from '../../components/SubscriptionPlanInfo';
import ThemeModeToggle from '../../components/ThemeModeToggle';
import { useAuth } from '../../context/AuthContext';
import { useColorMode } from '../../context/ColorModeContext';
import { PATHS } from '../../routes/paths';
import { SUBSCRIPTION_PLAN } from '../../constants/company';
import {
  fetchProfile,
  requestEmailChange,
  updateProfileRequest,
} from '../../services/authService';
import {
  fetchBusinessTypes,
  fetchMyTenant,
  updateMyTenant,
} from '../../services/tenantService';

const emptyBusiness = {
  name: '',
  business_name: '',
  business_type: 'other',
  address: '',
  city: '',
  state: '',
  pincode: '',
  phone: '',
  email: '',
  gst_number: '',
  fssai_number: '',
  bill_number_prefix: '',
};

function SettingsSection({ title, description, children, actions }) {
  return (
    <Card>
      <CardContent sx={{ p: { xs: 2.5, sm: 3 }, '&:last-child': { pb: { xs: 2.5, sm: 3 } } }}>
        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          justifyContent="space-between"
          alignItems={{ xs: 'stretch', sm: 'flex-start' }}
          spacing={2}
          sx={{ mb: 3 }}
        >
          <Box sx={{ minWidth: 0 }}>
            <Typography variant="h6" component="h2">
              {title}
            </Typography>
            {description ? (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.75, maxWidth: 560 }}>
                {description}
              </Typography>
            ) : null}
          </Box>
          {actions}
        </Stack>
        {children}
      </CardContent>
    </Card>
  );
}

export default function SettingsPage() {
  const { user, login } = useAuth();
  const { mode } = useColorMode();
  const [business, setBusiness] = useState(emptyBusiness);
  const [businessTypes, setBusinessTypes] = useState([]);
  const [profileName, setProfileName] = useState('');
  const [profilePhone, setProfilePhone] = useState('');
  const [profileEmail, setProfileEmail] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [savingBusiness, setSavingBusiness] = useState(false);
  const [savingProfile, setSavingProfile] = useState(false);
  const [emailLoading, setEmailLoading] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([fetchMyTenant(), fetchProfile(), fetchBusinessTypes()])
      .then(([tenantRes, profileRes, typesRes]) => {
        const t = tenantRes.data || {};
        setBusiness({
          name: t.name || '',
          business_name: t.business_name || '',
          business_type: t.business_type || 'other',
          address: t.address || '',
          city: t.city || '',
          state: t.state || '',
          pincode: t.pincode || '',
          phone: t.phone || '',
          email: t.email || '',
          gst_number: t.gst_number || '',
          fssai_number: t.fssai_number || '',
          bill_number_prefix: t.bill_number_prefix || '',
        });
        setBusinessTypes(typesRes.data?.business_types || []);
        const profile = profileRes.data || {};
        setProfileName(profile.name || '');
        setProfilePhone(profile.phone || '');
        setProfileEmail(profile.email || '');
      })
      .catch((err) => {
        setError(err.response?.data?.error?.message || 'Unable to load settings.');
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (loading) return undefined;
    if (window.location.hash !== '#subscription') return undefined;
    const timer = window.setTimeout(() => {
      document.getElementById('subscription')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 50);
    return () => window.clearTimeout(timer);
  }, [loading]);

  const onBusinessChange = (field) => (event) => {
    setBusiness((prev) => ({ ...prev, [field]: event.target.value }));
  };

  const selectedType = businessTypes.find((row) => row.code === business.business_type);
  const showFssaiHint = selectedType?.fssai_relevant ?? false;

  const onSaveBusiness = async (event) => {
    event.preventDefault();
    setSavingBusiness(true);
    setError('');
    setSuccess('');
    try {
      const response = await updateMyTenant(business);
      if (response.data) {
        setBusiness((prev) => ({
          ...prev,
          ...response.data,
          business_type: response.data.business_type || prev.business_type,
        }));
      }
      setSuccess('Business information updated successfully.');
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to save business settings');
    } finally {
      setSavingBusiness(false);
    }
  };

  const onSaveProfile = async (event) => {
    event.preventDefault();
    setSavingProfile(true);
    setError('');
    setSuccess('');
    try {
      const response = await updateProfileRequest({ name: profileName, phone: profilePhone });
      setSuccess('Profile updated successfully.');
      if (user && response.data) {
        const token = localStorage.getItem('access_token');
        login(token, {
          ...user,
          ...response.data,
          tenant: response.data.tenant || user.tenant,
        });
      }
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to save profile');
    } finally {
      setSavingProfile(false);
    }
  };

  const onRequestEmailChange = async (event) => {
    event.preventDefault();
    setEmailLoading(true);
    setError('');
    setSuccess('');
    try {
      const response = await requestEmailChange({ new_email: newEmail });
      setSuccess(response.data?.message || 'Verification email sent.');
      setNewEmail('');
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to request email change');
    } finally {
      setEmailLoading(false);
    }
  };

  if (loading) {
    return (
      <PageShell maxWidth={880}>
        <Box sx={{ py: 6, display: 'grid', placeItems: 'center' }}>
          <CircularProgress size={28} />
        </Box>
      </PageShell>
    );
  }

  return (
    <PageShell maxWidth={880}>
      {error ? <Alert severity="error">{error}</Alert> : null}
      {success ? <Alert severity="success">{success}</Alert> : null}

      <SettingsSection
        title="Profile"
        description="Your personal account details for this business."
      >
        <Stack component="form" spacing={2.5} onSubmit={onSaveProfile}>
          <Box
            sx={{
              display: 'grid',
              gap: 2.5,
              gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
            }}
          >
            <TextField
              label="Owner Name"
              value={profileName}
              onChange={(e) => setProfileName(e.target.value)}
              required
              fullWidth
            />
            <TextField
              label="Mobile"
              value={profilePhone}
              onChange={(e) => setProfilePhone(e.target.value)}
              fullWidth
            />
            <TextField
              label="Email"
              value={profileEmail}
              fullWidth
              disabled
              helperText="Use Email / Account below to change email"
              sx={{ gridColumn: { sm: '1 / -1' } }}
            />
          </Box>
          <Button
            type="submit"
            variant="contained"
            disabled={savingProfile}
            sx={{ alignSelf: 'flex-start' }}
          >
            {savingProfile ? 'Saving...' : 'Save Changes'}
          </Button>
        </Stack>
      </SettingsSection>

      <SettingsSection
        title="Business Information"
        description="Details shown on receipts and used across billing."
      >
        <Stack component="form" spacing={2.5} onSubmit={onSaveBusiness}>
          <Box
            sx={{
              display: 'grid',
              gap: 2.5,
              gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
            }}
          >
            <TextField
              label="Display Name"
              value={business.name}
              onChange={onBusinessChange('name')}
              required
              fullWidth
            />
            <TextField
              label="Business Name"
              value={business.business_name}
              onChange={onBusinessChange('business_name')}
              required
              fullWidth
            />
            <FormControl fullWidth required>
              <InputLabel id="settings-business-type-label">Business Type</InputLabel>
              <Select
                labelId="settings-business-type-label"
                label="Business Type"
                value={business.business_type || 'other'}
                onChange={onBusinessChange('business_type')}
              >
                {businessTypes.map((row) => (
                  <MenuItem key={row.code} value={row.code}>
                    {row.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="Address"
              value={business.address}
              onChange={onBusinessChange('address')}
              fullWidth
              sx={{ gridColumn: { sm: '1 / -1' } }}
            />
            <TextField label="City" value={business.city} onChange={onBusinessChange('city')} fullWidth />
            <TextField label="State" value={business.state} onChange={onBusinessChange('state')} fullWidth />
            <TextField
              label="Pincode"
              value={business.pincode}
              onChange={onBusinessChange('pincode')}
              fullWidth
            />
            <TextField
              label="Phone"
              value={business.phone}
              onChange={onBusinessChange('phone')}
              fullWidth
            />
            <TextField
              label="Business Email"
              value={business.email}
              onChange={onBusinessChange('email')}
              fullWidth
            />
            <TextField
              label="GSTIN"
              value={business.gst_number}
              onChange={onBusinessChange('gst_number')}
              fullWidth
            />
            <TextField
              label="FSSAI (optional)"
              value={business.fssai_number}
              onChange={onBusinessChange('fssai_number')}
              fullWidth
              helperText={
                showFssaiHint
                  ? 'Relevant for restaurants and hotels'
                  : 'Optional — usually not required for this business type'
              }
            />
            <TextField
              label="Bill Number Prefix"
              value={business.bill_number_prefix}
              onChange={onBusinessChange('bill_number_prefix')}
              helperText="Example: INV-A-"
              fullWidth
              sx={{ gridColumn: { sm: '1 / -1' } }}
            />
          </Box>
          <Button
            type="submit"
            variant="contained"
            disabled={savingBusiness}
            sx={{ alignSelf: 'flex-start' }}
          >
            {savingBusiness ? 'Saving...' : 'Save Changes'}
          </Button>
        </Stack>
      </SettingsSection>

      <Box id="subscription">
        <SettingsSection
          title="Subscription"
          description={`${SUBSCRIPTION_PLAN.priceDisplay} · informational plan details (no in-app payment).`}
        >
          <SubscriptionPlanInfo variant="owner" dense />
        </SettingsSection>
      </Box>

      <SettingsSection
        title="Appearance"
        description="Choose light or dark mode. Your preference is saved on this device."
        actions={<ThemeModeToggle />}
      >
        <Typography variant="body2" color="text.secondary">
          Current theme: <strong>{mode === 'dark' ? 'Dark' : 'Light'}</strong>
        </Typography>
      </SettingsSection>

      <SettingsSection
        title="Security"
        description="Keep your account secure with a strong password."
        actions={
          <Button
            component={RouterLink}
            to={PATHS.ownerChangePassword}
            variant="outlined"
            startIcon={<LockOutlinedIcon />}
          >
            Change Password
          </Button>
        }
      >
        <Typography variant="body2" color="text.secondary">
          You will be signed out after a successful password update.
        </Typography>
      </SettingsSection>

      <SettingsSection
        title="Email / Account"
        description="Request a change to your login email address."
      >
        <Stack component="form" spacing={2.5} onSubmit={onRequestEmailChange} maxWidth={480}>
          <TextField label="Current Email" value={profileEmail} fullWidth disabled />
          <TextField
            label="New Email"
            type="email"
            value={newEmail}
            onChange={(e) => setNewEmail(e.target.value)}
            required
            fullWidth
          />
          <Button
            type="submit"
            variant="contained"
            disabled={emailLoading}
            sx={{ alignSelf: 'flex-start' }}
          >
            {emailLoading ? 'Sending...' : 'Request Email Change'}
          </Button>
        </Stack>
      </SettingsSection>
    </PageShell>
  );
}
