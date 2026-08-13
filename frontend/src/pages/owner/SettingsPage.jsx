import {
  Alert,
  Button,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { fetchMyTenant, updateMyTenant } from '../../services/tenantService';

const empty = {
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

export default function SettingsPage() {
  const [form, setForm] = useState(empty);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchMyTenant()
      .then((res) => {
        const t = res.data || {};
        setForm({
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
      })
      .catch((err) => {
        setError(err.response?.data?.error?.message || 'Failed to load hotel settings');
      });
  }, []);

  const onChange = (field) => (event) => {
    setForm((prev) => ({ ...prev, [field]: event.target.value }));
  };

  const onSave = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await updateMyTenant(form);
      setSuccess('Hotel profile updated');
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <Typography variant="h5" gutterBottom>
        Hotel Settings
      </Typography>
      {error ? <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert> : null}
      {success ? <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert> : null}
      <Stack component="form" spacing={2} onSubmit={onSave} maxWidth={720}>
        <TextField label="Internal Name" value={form.name} onChange={onChange('name')} required />
        <TextField
          label="Business Name (on receipt)"
          value={form.business_name}
          onChange={onChange('business_name')}
          required
        />
        <TextField label="Address" value={form.address} onChange={onChange('address')} />
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <TextField label="City" value={form.city} onChange={onChange('city')} fullWidth />
          <TextField label="State" value={form.state} onChange={onChange('state')} fullWidth />
          <TextField label="Pincode" value={form.pincode} onChange={onChange('pincode')} fullWidth />
        </Stack>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <TextField label="Phone" value={form.phone} onChange={onChange('phone')} fullWidth />
          <TextField label="Email" value={form.email} onChange={onChange('email')} fullWidth />
        </Stack>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
          <TextField label="GSTIN" value={form.gst_number} onChange={onChange('gst_number')} fullWidth />
          <TextField label="FSSAI" value={form.fssai_number} onChange={onChange('fssai_number')} fullWidth />
        </Stack>
        <TextField
          label="Bill Number Prefix"
          value={form.bill_number_prefix}
          onChange={onChange('bill_number_prefix')}
          helperText="Example: INV-A-"
        />
        <Button type="submit" variant="contained" disabled={saving} sx={{ alignSelf: 'flex-start' }}>
          Save Settings
        </Button>
      </Stack>
    </>
  );
}