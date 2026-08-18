import {
  Alert,
  Button,
  CircularProgress,
  FormControlLabel,
  Stack,
  Switch,
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import PageShell from '../../components/PageShell';
import { fetchTrialSettings, updateTrialSettings } from '../../services/masterService';

export default function MasterTrialSettingsPage() {
  const [trialEnabled, setTrialEnabled] = useState(true);
  const [trialDays, setTrialDays] = useState(15);
  const [expiryWarningDays, setExpiryWarningDays] = useState(5);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let active = true;
    fetchTrialSettings()
      .then((payload) => {
        if (!active) return;
        const data = payload.data || {};
        setTrialEnabled(Boolean(data.trial_enabled));
        setTrialDays(Number(data.trial_days || 15));
        setExpiryWarningDays(Number(data.expiry_warning_days || 5));
      })
      .catch((err) => {
        if (active) {
          setError(err.response?.data?.error?.message || 'Unable to load trial settings.');
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const onSave = async (event) => {
    event.preventDefault();
    setError('');
    setSuccess('');
    const days = Number(trialDays);
    if (!Number.isInteger(days) || days < 1 || days > 365) {
      setError('Trial duration must be a whole number from 1 to 365 days.');
      return;
    }
    const warningDays = Number(expiryWarningDays);
    if (!Number.isInteger(warningDays) || warningDays < 1 || warningDays > 30) {
      setError('Expiry warning must be a whole number from 1 to 30 days.');
      return;
    }
    setSaving(true);
    try {
      const payload = await updateTrialSettings({
        trial_enabled: trialEnabled,
        trial_days: days,
        expiry_warning_days: warningDays,
      });
      const data = payload.data || {};
      setTrialEnabled(Boolean(data.trial_enabled));
      setTrialDays(Number(data.trial_days));
      setExpiryWarningDays(Number(data.expiry_warning_days));
      setSuccess(
        data.trial_enabled
          ? `Saved. New approvals receive a ${data.trial_days}-day trial. Existing trials are unchanged. Expiry notices use a ${data.expiry_warning_days}-day warning window.`
          : `Saved. New approvals will not receive a free trial. Existing trials are unchanged. Expiry notices use a ${data.expiry_warning_days}-day warning window.`
      );
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to save trial settings.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <PageShell>
        <Stack alignItems="center" py={6}>
          <CircularProgress size={28} />
        </Stack>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <Stack component="form" onSubmit={onSave} spacing={2.5} maxWidth={480}>
        {error ? <Alert severity="error">{error}</Alert> : null}
        {success ? <Alert severity="success">{success}</Alert> : null}

        <FormControlLabel
          control={
            <Switch
              checked={trialEnabled}
              onChange={(event) => setTrialEnabled(event.target.checked)}
            />
          }
          label={trialEnabled ? 'Free trial: ON' : 'Free trial: OFF'}
        />

        <TextField
          label="Trial duration (days)"
          type="number"
          value={trialDays}
          onChange={(event) => setTrialDays(event.target.value)}
          inputProps={{ min: 1, max: 365, step: 1 }}
          required
          helperText="Used only when free trial is ON. 0 days is not allowed — turn the trial off instead."
        />

        <TextField
          label="Expiry warning window (days)"
          type="number"
          value={expiryWarningDays}
          onChange={(event) => setExpiryWarningDays(event.target.value)}
          inputProps={{ min: 1, max: 30, step: 1 }}
          required
          helperText="Businesses inside this window receive expiring notices and appear in the expiring filter."
        />

        <Typography variant="body2" color="text.secondary">
          Current status: {trialEnabled ? 'Active' : 'Inactive'}. Changing these values does not
          rewrite trial dates already granted to businesses. Expiry warnings use the value above
          for both Owner notices and Master expiring counts.
        </Typography>

        <Button type="submit" variant="contained" disabled={saving}>
          {saving ? 'Saving…' : 'Save changes'}
        </Button>
      </Stack>
    </PageShell>
  );
}
