import {
  Alert,
  Button,
  CircularProgress,
  Stack,
  TextField,
} from '@mui/material';
import { useEffect, useState } from 'react';
import FormSection from '../../components/FormSection';
import PageShell from '../../components/PageShell';
import { useAuth } from '../../context/AuthContext';
import {
  fetchProfile,
  requestEmailChange,
  updateProfileRequest,
} from '../../services/authService';

export default function ProfilePage() {
  const { user, login } = useAuth();
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [emailLoading, setEmailLoading] = useState(false);

  useEffect(() => {
    fetchProfile()
      .then((res) => {
        const profile = res.data || {};
        setName(profile.name || '');
        setEmail(profile.email || '');
        setPhone(profile.phone || '');
        setNewEmail('');
      })
      .catch((err) => {
        setError(err.response?.data?.error?.message || 'Failed to load profile');
      });
  }, []);

  const onSaveProfile = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const response = await updateProfileRequest({ name, phone });
      setSuccess('Profile updated');
      if (user && response.data) {
        const token = localStorage.getItem('access_token');
        login(token, { ...user, ...response.data, tenant: response.data.tenant || user.tenant });
      }
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to update profile');
    } finally {
      setLoading(false);
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
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to request email change');
    } finally {
      setEmailLoading(false);
    }
  };

  return (
    <PageShell maxWidth={880}>
      {error ? <Alert severity="error">{error}</Alert> : null}
      {success ? <Alert severity="success">{success}</Alert> : null}

      <FormSection
        title="Profile"
        description="Update your name and contact phone used across the business account."
      >
        <Stack spacing={2.5} component="form" onSubmit={onSaveProfile}>
          <TextField label="Name" value={name} onChange={(e) => setName(e.target.value)} required fullWidth />
          <TextField label="Current Email" value={email} fullWidth disabled />
          <TextField
            label="Phone"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            fullWidth
            helperText="Updates business contact phone used on receipts"
          />
          <Button
            type="submit"
            variant="contained"
            disabled={loading}
            startIcon={loading ? <CircularProgress size={16} color="inherit" /> : null}
            sx={{ alignSelf: 'flex-start' }}
          >
            Save Profile
          </Button>
        </Stack>
      </FormSection>

      <FormSection
        title="Change Email"
        description="A verification link will be sent to the new email before it is updated."
      >
        <Stack spacing={2.5} component="form" onSubmit={onRequestEmailChange}>
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
            variant="outlined"
            disabled={emailLoading}
            startIcon={emailLoading ? <CircularProgress size={16} color="inherit" /> : null}
            sx={{ alignSelf: 'flex-start' }}
          >
            Send Verification
          </Button>
        </Stack>
      </FormSection>
    </PageShell>
  );
}
