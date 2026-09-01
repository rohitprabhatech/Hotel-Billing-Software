import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import FlightTakeoffOutlinedIcon from '@mui/icons-material/FlightTakeoffOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  Stack,
  Switch,
  TextField,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import StatusBadge from '../../components/ui/StatusBadge';
import { PageActions } from '../../context/PageActionsContext';
import { useAuth } from '../../context/AuthContext';
import { useModuleGate } from '../../context/ModulesContext';
import {
  billTourPackage,
  createTourPackage,
  listTourPackages,
  updateTourPackage,
} from '../../services/tourPackageService';

function money(v) {
  return `₹${Number(v || 0).toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

const emptyForm = {
  code: '',
  name: '',
  destination: '',
  duration_days: '',
  base_price: '',
  gst_percentage: '0',
  description: '',
  notes: '',
  is_active: true,
};

export default function TourPackagesPage() {
  const moduleEnabled = useModuleGate('tour_packages');
  const { role } = useAuth();
  const canWrite = role === 'OWNER' || role === 'MANAGER';

  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [open, setOpen] = useState(false);
  const [editId, setEditId] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [billingId, setBillingId] = useState(null);

  const load = useCallback(async () => {
    if (!moduleEnabled) return;
    setLoading(true);
    setError('');
    try {
      const res = await listTourPackages({ per_page: 100 });
      setRows(res.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load packages');
    } finally {
      setLoading(false);
    }
  }, [moduleEnabled]);

  useEffect(() => {
    load();
  }, [load]);

  const openCreate = () => {
    setEditId(null);
    setForm(emptyForm);
    setOpen(true);
  };

  const openEdit = (row) => {
    setEditId(row.id);
    setForm({
      code: row.code || '',
      name: row.name || '',
      destination: row.destination || '',
      duration_days: row.duration_days != null ? String(row.duration_days) : '',
      base_price: String(row.base_price ?? ''),
      gst_percentage: String(row.gst_percentage ?? '0'),
      description: row.description || '',
      notes: row.notes || '',
      is_active: !!row.is_active,
    });
    setOpen(true);
  };

  const onSave = async () => {
    if (!form.code.trim() || !form.name.trim() || form.base_price === '') {
      setError('Code, name, and price are required.');
      return;
    }
    setSaving(true);
    setError('');
    try {
      const payload = {
        code: form.code.trim(),
        name: form.name.trim(),
        destination: form.destination.trim() || null,
        duration_days: form.duration_days ? Number(form.duration_days) : null,
        base_price: Number(form.base_price),
        gst_percentage: Number(form.gst_percentage || 0),
        description: form.description.trim() || null,
        notes: form.notes.trim() || null,
        is_active: form.is_active,
      };
      if (editId) {
        await updateTourPackage(editId, payload);
        setSuccess('Package updated');
      } else {
        await createTourPackage(payload);
        setSuccess('Package created');
      }
      setOpen(false);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not save package');
    } finally {
      setSaving(false);
    }
  };

  const onBill = async (row) => {
    setBillingId(row.id);
    setError('');
    try {
      const res = await billTourPackage(row.id, {
        quantity: 1,
        payment_method: 'cash',
      });
      setSuccess(`Bill ${res.data?.bill?.bill_number} created for ${row.name}`);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not create bill');
    } finally {
      setBillingId(null);
    }
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <EmptyState
          icon={<FlightTakeoffOutlinedIcon />}
          title="Tour packages not enabled"
          description="Available for travel agency tenants."
        />
      </PageShell>
    );
  }

  return (
    <PageShell>
      <PageActions>
        {canWrite ? (
          <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={openCreate}>
            Package
          </Button>
        ) : null}
      </PageActions>

      {error ? <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert> : null}
      {success ? <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert> : null}

      {loading ? (
        <LoadingBlock />
      ) : rows.length === 0 ? (
        <EmptyState
          icon={<FlightTakeoffOutlinedIcon />}
          title="No tour packages yet"
          description="Create service packages with pricing — no inventory stock."
        />
      ) : (
        <Box
          sx={{
            display: 'grid',
            gap: 2,
            gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr' },
          }}
        >
          {rows.map((row) => (
            <Card key={row.id} variant="outlined">
              <CardContent>
                <Stack direction="row" justifyContent="space-between" alignItems="flex-start" spacing={1}>
                  <Typography variant="h6" component="h2">
                    {row.name}
                  </Typography>
                  <StatusBadge label={row.is_active ? 'Active' : 'Inactive'} />
                </Stack>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                  {row.code}
                  {row.destination ? ` · ${row.destination}` : ''}
                  {row.duration_days ? ` · ${row.duration_days} days` : ''}
                </Typography>
                <Typography variant="h5" sx={{ mt: 1.5 }}>
                  {money(row.base_price)}
                </Typography>
                {Number(row.gst_percentage) > 0 ? (
                  <Typography variant="caption" color="text.secondary">
                    GST {row.gst_percentage}%
                  </Typography>
                ) : null}
                {row.description ? (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    {row.description}
                  </Typography>
                ) : null}
                <StatusBadge label="No stock tracking" variant="info" sx={{ mt: 1.5 }} />
              </CardContent>
              <CardActions>
                {canWrite ? (
                  <Button size="small" onClick={() => openEdit(row)}>
                    Edit
                  </Button>
                ) : null}
                <Button
                  size="small"
                  variant="contained"
                  disabled={!row.is_active || billingId === row.id}
                  onClick={() => onBill(row)}
                >
                  {billingId === row.id ? 'Billing…' : 'Create bill'}
                </Button>
              </CardActions>
            </Card>
          ))}
        </Box>
      )}

      <Dialog open={open} onClose={() => !saving && setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>{editId ? 'Edit package' : 'New tour package'}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Code"
              value={form.code}
              onChange={(e) => setForm((f) => ({ ...f, code: e.target.value }))}
              fullWidth
              disabled={!!editId}
            />
            <TextField
              label="Name"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              fullWidth
            />
            <TextField
              label="Destination"
              value={form.destination}
              onChange={(e) => setForm((f) => ({ ...f, destination: e.target.value }))}
              fullWidth
            />
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                label="Duration (days)"
                type="number"
                value={form.duration_days}
                onChange={(e) => setForm((f) => ({ ...f, duration_days: e.target.value }))}
                fullWidth
              />
              <TextField
                label="Base price"
                type="number"
                value={form.base_price}
                onChange={(e) => setForm((f) => ({ ...f, base_price: e.target.value }))}
                fullWidth
                required
              />
              <TextField
                label="GST %"
                type="number"
                value={form.gst_percentage}
                onChange={(e) => setForm((f) => ({ ...f, gst_percentage: e.target.value }))}
                fullWidth
              />
            </Stack>
            <TextField
              label="Description"
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              fullWidth
              multiline
              minRows={2}
            />
            <TextField
              label="Notes"
              value={form.notes}
              onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))}
              fullWidth
            />
            <FormControlLabel
              control={
                <Switch
                  checked={form.is_active}
                  onChange={(e) => setForm((f) => ({ ...f, is_active: e.target.checked }))}
                />
              }
              label="Active"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)} disabled={saving}>
            Cancel
          </Button>
          <Button variant="contained" onClick={onSave} disabled={saving}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
