import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import PageShell from '../../components/PageShell';
import { useAuth } from '../../context/AuthContext';
import { PATHS } from '../../routes/paths';
import {
  fetchProfile,
  requestEmailChange,
  updateProfileRequest,
} from '../../services/authService';
import { fetchMyTenant, updateMyTenant } from '../../services/tenantService';

const emptyHotel = {
  name: '',
  business_name: '',
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
  const [hotel, setHotel] = useState(emptyHotel);
  const [profileName, setProfileName] = useState('');
  const [profilePhone, setProfilePhone] = useState('');
  const [profileEmail, setProfileEmail] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [savingHotel, setSavingHotel] = useState(false);
  const [savingProfile, setSavingProfile] = useState(false);
  const [emailLoading, setEmailLoading] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([fetchMyTenant(), fetchProfile()])
      .then(([tenantRes, profileRes]) => {
        const t = tenantRes.data || {};
        setHotel({
          name: t.name || '',
          business_name: t.business_name || '',
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

  const onHotelChange = (field) => (event) => {
    setHotel((prev) => ({ ...prev, [field]: event.target.value }));
  };

  const onSaveHotel = async (event) => {
    event.preventDefault();
    setSavingHotel(true);
    setError('');
    setSuccess('');
    try {
      await updateMyTenant(hotel);
      setSuccess('Hotel information updated successfully.');
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to save hotel settings');
    } finally {
      setSavingHotel(false);
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
      <Box sx={{ py: 10, display: 'grid', placeItems: 'center' }}>
        <CircularProgress size={28} />
      </Box>
    );
  }

  return (
    <PageShell spacing={3} maxWidth={880}>
      {error ? <Alert severity="error">{error}</Alert> : null}
      {success ? <Alert severity="success">{success}</Alert> : null}

      <SettingsSection
        title="Profile"
        description="Your personal account details for this hotel."
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
        title="Hotel Information"
        description="Details shown on receipts and used across billing."
      >
        <Stack component="form" spacing={2.5} onSubmit={onSaveHotel}>
          <Box
            sx={{
              display: 'grid',
              gap: 2.5,
              gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
            }}
          >
            <TextField
              label="Hotel Name"
              value={hotel.name}
              onChange={onHotelChange('name')}
              required
              fullWidth
            />
            <TextField
              label="Business Name"
              value={hotel.business_name}
              onChange={onHotelChange('business_name')}
              required
              fullWidth
            />
            <TextField
              label="Address"
              value={hotel.address}
              onChange={onHotelChange('address')}
              fullWidth
              sx={{ gridColumn: { sm: '1 / -1' } }}
            />
            <TextField label="City" value={hotel.city} onChange={onHotelChange('city')} fullWidth />
            <TextField label="State" value={hotel.state} onChange={onHotelChange('state')} fullWidth />
            <TextField
              label="Pincode"
              value={hotel.pincode}
              onChange={onHotelChange('pincode')}
              fullWidth
            />
            <TextField
              label="Phone"
              value={hotel.phone}
              onChange={onHotelChange('phone')}
              fullWidth
            />
            <TextField
              label="Hotel Email"
              value={hotel.email}
              onChange={onHotelChange('email')}
              fullWidth
            />
            <TextField
              label="GSTIN"
              value={hotel.gst_number}
              onChange={onHotelChange('gst_number')}
              fullWidth
            />
            <TextField
              label="FSSAI"
              value={hotel.fssai_number}
              onChange={onHotelChange('fssai_number')}
              fullWidth
            />
            <TextField
              label="Bill Number Prefix"
              value={hotel.bill_number_prefix}
              onChange={onHotelChange('bill_number_prefix')}
              helperText="Example: INV-A-"
              fullWidth
              sx={{ gridColumn: { sm: '1 / -1' } }}
            />
          </Box>
          <Button
            type="submit"
            variant="contained"
            disabled={savingHotel}
            sx={{ alignSelf: 'flex-start' }}
          >
            {savingHotel ? 'Saving...' : 'Save Changes'}
          </Button>
        </Stack>
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
