import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import {
  Alert,
  Button,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  FormControlLabel,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import PageShell from '../../components/PageShell';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import { PageActions } from '../../context/PageActionsContext';
import {
  createPlan,
  listPlans,
  setPlanStatus,
  updatePlan,
} from '../../services/masterService';

const emptyForm = {
  name: '',
  description: '',
  price: '550',
  billing_cycle: 'MONTHLY',
  trial_eligible: true,
  is_public: true,
  is_active: true,
  display_order: '1',
  features: '',
};

function cycleLabel(cycle) {
  if (cycle === 'YEARLY') return 'Yearly';
  return 'Monthly';
}

function money(value) {
  return `₹${Number(value || 0).toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export default function MasterPlansPage() {
  const [rows, setRows] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [editing, setEditing] = useState(null);
  const [deactivate, setDeactivate] = useState(null);

  const load = async () => {
    setError('');
    try {
      const response = await listPlans({ include_inactive: true });
      setRows(response.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load plans.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const openCreate = () => {
    setEditing('new');
    setForm(emptyForm);
  };

  const openEdit = (row) => {
    setEditing(row);
    setForm({
      name: row.name || '',
      description: row.description || '',
      price: String(row.price ?? ''),
      billing_cycle: row.billing_cycle || 'MONTHLY',
      trial_eligible: Boolean(row.trial_eligible),
      is_public: Boolean(row.is_public),
      is_active: Boolean(row.is_active),
      display_order: String(row.display_order ?? 0),
      features: (row.features || []).join('\n'),
    });
  };

  const payloadFromForm = () => ({
    name: form.name.trim(),
    description: form.description.trim(),
    price: Number(form.price),
    billing_cycle: form.billing_cycle,
    trial_eligible: form.trial_eligible,
    is_public: form.is_public,
    is_active: form.is_active,
    display_order: Number(form.display_order || 0),
    features: form.features
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean),
  });

  const onSave = async () => {
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const payload = payloadFromForm();
      if (editing === 'new') {
        await createPlan(payload);
        setSuccess('Plan created.');
      } else {
        await updatePlan(editing.id, payload);
        setSuccess('Plan updated. Existing subscriptions keep their original billed price.');
      }
      setEditing(null);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to save plan.');
    } finally {
      setSaving(false);
    }
  };

  const onToggle = async () => {
    if (!deactivate) return;
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await setPlanStatus(deactivate.id, !deactivate.is_active);
      setSuccess(
        deactivate.is_active
          ? 'Plan deactivated. Existing subscriptions were not deleted.'
          : 'Plan activated.'
      );
      setDeactivate(null);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to update plan status.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <PageActions>
        <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={openCreate}>
          Create plan
        </Button>
      </PageActions>

      <PageShell>
        {error ? <Alert severity="error">{error}</Alert> : null}
        {success ? <Alert severity="success">{success}</Alert> : null}

        {loading ? (
          <Stack alignItems="center" py={6}>
            <CircularProgress size={28} />
          </Stack>
        ) : rows.length === 0 ? (
          <EmptyState
            title="No plans yet"
            description="Create a plan to use for subscriptions and, later, the public landing page."
            actionLabel="Create plan"
            onAction={openCreate}
          />
        ) : (
          <TableCard>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Order</TableCell>
                  <TableCell>Plan</TableCell>
                  <TableCell>Price</TableCell>
                  <TableCell>Cycle</TableCell>
                  <TableCell>Public</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Subscribers</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {rows.map((row) => (
                  <TableRow key={row.id} hover>
                    <TableCell>{row.display_order}</TableCell>
                    <TableCell>
                      <TruncateText value={row.name} />
                    </TableCell>
                    <TableCell>{money(row.price)}</TableCell>
                    <TableCell>{cycleLabel(row.billing_cycle)}</TableCell>
                    <TableCell>{row.is_public ? 'Yes' : 'No'}</TableCell>
                    <TableCell>
                      <Chip
                        size="small"
                        color={row.is_active ? 'success' : 'default'}
                        label={row.is_active ? 'ACTIVE' : 'INACTIVE'}
                      />
                    </TableCell>
                    <TableCell>{row.subscriber_count ?? 0}</TableCell>
                    <TableCell align="right">
                      <Button size="small" onClick={() => openEdit(row)}>
                        Edit
                      </Button>
                      <Button size="small" onClick={() => setDeactivate(row)}>
                        {row.is_active ? 'Deactivate' : 'Activate'}
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableCard>
        )}
      </PageShell>

      <Dialog open={Boolean(editing)} onClose={() => setEditing(null)} maxWidth="sm" fullWidth>
        <DialogTitle>{editing === 'new' ? 'Create plan' : 'Edit plan'}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            <TextField
              label="Plan name"
              value={form.name}
              onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))}
              required
              fullWidth
            />
            <TextField
              label="Description"
              value={form.description}
              onChange={(event) => setForm((prev) => ({ ...prev, description: event.target.value }))}
              fullWidth
              multiline
              minRows={2}
            />
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                label="Price (INR)"
                type="number"
                value={form.price}
                onChange={(event) => setForm((prev) => ({ ...prev, price: event.target.value }))}
                required
                fullWidth
                inputProps={{ min: 0, step: '0.01' }}
              />
              <FormControl fullWidth>
                <InputLabel id="plan-cycle-label">Billing cycle</InputLabel>
                <Select
                  labelId="plan-cycle-label"
                  label="Billing cycle"
                  value={form.billing_cycle}
                  onChange={(event) =>
                    setForm((prev) => ({ ...prev, billing_cycle: event.target.value }))
                  }
                >
                  <MenuItem value="MONTHLY">Monthly</MenuItem>
                  <MenuItem value="YEARLY">Yearly</MenuItem>
                </Select>
              </FormControl>
            </Stack>
            <TextField
              label="Display order"
              type="number"
              value={form.display_order}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, display_order: event.target.value }))
              }
              helperText="Landing page will use this order in a later sprint."
            />
            <TextField
              label="Features (one per line)"
              value={form.features}
              onChange={(event) => setForm((prev) => ({ ...prev, features: event.target.value }))}
              fullWidth
              multiline
              minRows={4}
            />
            <FormControlLabel
              control={
                <Switch
                  checked={form.trial_eligible}
                  onChange={(event) =>
                    setForm((prev) => ({ ...prev, trial_eligible: event.target.checked }))
                  }
                />
              }
              label="Trial eligible"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={form.is_public}
                  onChange={(event) =>
                    setForm((prev) => ({ ...prev, is_public: event.target.checked }))
                  }
                />
              }
              label="Show on public landing (when pricing API ships)"
            />
            {editing === 'new' ? (
              <FormControlLabel
                control={
                  <Switch
                    checked={form.is_active}
                    onChange={(event) =>
                      setForm((prev) => ({ ...prev, is_active: event.target.checked }))
                    }
                  />
                }
                label="Active"
              />
            ) : null}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditing(null)}>Cancel</Button>
          <Button variant="contained" onClick={onSave} disabled={saving}>
            Save
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(deactivate)} onClose={() => setDeactivate(null)}>
        <DialogTitle>{deactivate?.is_active ? 'Deactivate plan?' : 'Activate plan?'}</DialogTitle>
        <DialogContent>
          <Typography>
            {deactivate?.is_active
              ? `${deactivate?.name || 'This plan'} will no longer be available for new subscriptions. Existing subscriptions are not deleted.`
              : `${deactivate?.name || 'This plan'} will be available again for new subscriptions.`}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeactivate(null)}>Cancel</Button>
          <Button
            color={deactivate?.is_active ? 'error' : 'primary'}
            variant="contained"
            onClick={onToggle}
            disabled={saving}
          >
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
