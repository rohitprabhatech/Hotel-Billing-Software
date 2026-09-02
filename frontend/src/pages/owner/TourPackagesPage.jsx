import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
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
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Stack,
  Switch,
  TextField,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import EmptyState from '../../components/EmptyState';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import StatusBadge from '../../components/ui/StatusBadge';
import { PageActions } from '../../context/PageActionsContext';
import { useAuth } from '../../context/AuthContext';
import { useModuleGate } from '../../context/ModulesContext';
import { usePermissions } from '../../hooks/usePermissions';
import { billPrintPath } from '../../services/billService';
import {
  DEFAULT_PAYMENT_METHOD,
  PAYMENT_CASH,
  PAYMENT_ONLINE,
  isAllowedPaymentMethod,
} from '../../utils/paymentMethod';
import {
  TOUR_TRANSPORT_OPTIONS,
  TOUR_TRANSPORT_OTHER,
  resolveTourTransportPayload,
  splitTourTransportValue,
  tourTransportLabel,
} from '../../utils/tourTransport';
import {
  billTourPackage,
  createTourPackage,
  deleteTourPackage,
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
  transport_type: '',
  transport_type_other: '',
  duration_days: '',
  base_price: '',
  gst_percentage: '0',
  description: '',
  notes: '',
  is_active: true,
};

export default function TourPackagesPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const moduleEnabled = useModuleGate('tour_packages');
  const { role } = useAuth();
  const { isOwner } = usePermissions();
  const canWrite = role === 'OWNER' || role === 'MANAGER';
  const canRemove = isOwner && location.pathname.startsWith('/owner');

  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [open, setOpen] = useState(false);
  const [editId, setEditId] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [billingId, setBillingId] = useState(null);
  const [billDialogOpen, setBillDialogOpen] = useState(false);
  const [billTarget, setBillTarget] = useState(null);
  const [billCustomerName, setBillCustomerName] = useState('');
  const [billPaymentMethod, setBillPaymentMethod] = useState(DEFAULT_PAYMENT_METHOD);
  const [createdBill, setCreatedBill] = useState(null);
  const [removeTarget, setRemoveTarget] = useState(null);
  const [removing, setRemoving] = useState(false);

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
    const transport = splitTourTransportValue(row.transport_type);
    setEditId(row.id);
    setForm({
      code: row.code || '',
      name: row.name || '',
      destination: row.destination || '',
      transport_type: transport.transport_type,
      transport_type_other: transport.transport_type_other,
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
    const transportType = resolveTourTransportPayload(form.transport_type, form.transport_type_other);
    if (!transportType) {
      setError('Select a transport type (Bus, Car, etc.).');
      return;
    }
    if (form.transport_type === TOUR_TRANSPORT_OTHER && !form.transport_type_other.trim()) {
      setError('Enter the transport type when Other is selected.');
      return;
    }
    setSaving(true);
    setError('');
    try {
      const payload = {
        code: form.code.trim(),
        name: form.name.trim(),
        destination: form.destination.trim() || null,
        transport_type: transportType,
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

  const openBillDialog = (row) => {
    setBillTarget(row);
    setBillCustomerName('');
    setBillPaymentMethod(DEFAULT_PAYMENT_METHOD);
    setBillDialogOpen(true);
    setError('');
  };

  const onBill = async () => {
    if (!billTarget) return;
    const customerName = billCustomerName.trim();
    if (!customerName) {
      setError('Customer name is required for the bill.');
      return;
    }
    if (!isAllowedPaymentMethod(billPaymentMethod)) {
      setError('Please select a payment method.');
      return;
    }
    setBillingId(billTarget.id);
    setError('');
    try {
      const res = await billTourPackage(billTarget.id, {
        quantity: 1,
        payment_method: billPaymentMethod,
        customer_name: customerName,
      });
      setBillDialogOpen(false);
      setCreatedBill(res.data?.bill || null);
      setSuccess(`Bill ${res.data?.bill?.bill_number} created for ${customerName}`);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not create bill');
    } finally {
      setBillingId(null);
    }
  };

  const onRemove = async () => {
    if (!removeTarget) return;
    setRemoving(true);
    setError('');
    try {
      await deleteTourPackage(removeTarget.id);
      setSuccess(`Package ${removeTarget.name} removed`);
      setRemoveTarget(null);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not remove package');
    } finally {
      setRemoving(false);
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
      {!canWrite ? (
        <Alert severity="info" sx={{ mb: 2 }}>
          Billing users can view packages and create bills. Owner/manager creates and edits packages.
        </Alert>
      ) : null}

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
                  {row.transport_type_label || row.transport_type
                    ? ` · ${row.transport_type_label || tourTransportLabel(row.transport_type)}`
                    : ''}
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
                {canRemove && row.is_active ? (
                  <Button
                    size="small"
                    color="error"
                    onClick={() => setRemoveTarget(row)}
                  >
                    Remove
                  </Button>
                ) : null}
                <Button
                  size="small"
                  variant="contained"
                  disabled={!row.is_active || billingId === row.id}
                  onClick={() => openBillDialog(row)}
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
            <TextField
              select
              label="Transport type"
              value={form.transport_type}
              onChange={(e) =>
                setForm((f) => ({
                  ...f,
                  transport_type: e.target.value,
                  transport_type_other:
                    e.target.value === TOUR_TRANSPORT_OTHER ? f.transport_type_other : '',
                }))
              }
              fullWidth
              required
              helperText="How travellers go — bus, car, train, flight, etc."
            >
              <MenuItem value="">
                <em>Select transport</em>
              </MenuItem>
              {TOUR_TRANSPORT_OPTIONS.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
            {form.transport_type === TOUR_TRANSPORT_OTHER ? (
              <TextField
                label="Other transport"
                value={form.transport_type_other}
                onChange={(e) => setForm((f) => ({ ...f, transport_type_other: e.target.value }))}
                fullWidth
                required
                placeholder="e.g. Luxury coach, Helicopter"
                inputProps={{ maxLength: 60 }}
              />
            ) : null}
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

      <Dialog
        open={billDialogOpen}
        onClose={() => !billingId && setBillDialogOpen(false)}
        fullWidth
        maxWidth="xs"
      >
        <DialogTitle>Create bill — {billTarget?.name}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Customer name"
              value={billCustomerName}
              onChange={(e) => setBillCustomerName(e.target.value)}
              fullWidth
              required
              autoFocus
              placeholder="Walk-in Traveler"
              helperText="Printed on the bill receipt"
              inputProps={{ maxLength: 120 }}
            />
            <FormControl fullWidth size="small">
              <InputLabel id="pkg-bill-payment">Payment method</InputLabel>
              <Select
                labelId="pkg-bill-payment"
                label="Payment method"
                value={billPaymentMethod}
                onChange={(e) => setBillPaymentMethod(e.target.value)}
              >
                <MenuItem value={PAYMENT_CASH}>Cash</MenuItem>
                <MenuItem value={PAYMENT_ONLINE}>Online</MenuItem>
              </Select>
            </FormControl>
            {billTarget ? (
              <Typography variant="body2" color="text.secondary">
                Package total: {money(billTarget.base_price)}
                {Number(billTarget.gst_percentage) > 0
                  ? ` + GST ${billTarget.gst_percentage}%`
                  : ''}
              </Typography>
            ) : null}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBillDialogOpen(false)} disabled={Boolean(billingId)}>
            Cancel
          </Button>
          <Button variant="contained" onClick={onBill} disabled={Boolean(billingId)}>
            {billingId ? 'Creating…' : 'Create bill'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(createdBill)} onClose={() => setCreatedBill(null)} fullWidth maxWidth="xs">
        <DialogTitle>Bill created</DialogTitle>
        <DialogContent>
          <Stack spacing={1.5} sx={{ mt: 0.5 }}>
            <Typography>
              Bill <strong>#{createdBill?.bill_number}</strong> saved.
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Customer: {createdBill?.customer_name || '—'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total: {money(createdBill?.grand_total)}
            </Typography>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreatedBill(null)}>Close</Button>
          <Button
            variant="contained"
            onClick={() => {
              const billId = createdBill?.id;
              setCreatedBill(null);
              if (billId) {
                navigate(billPrintPath(billId, { auto: true }));
              }
            }}
          >
            Print bill
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(removeTarget)} onClose={() => !removing && setRemoveTarget(null)} maxWidth="xs" fullWidth>
        <DialogTitle>Remove tour package?</DialogTitle>
        <DialogContent>
          <Typography>
            Deactivate <strong>{removeTarget?.name}</strong>? It will no longer appear for new bookings or bills.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRemoveTarget(null)} disabled={removing}>
            Cancel
          </Button>
          <Button color="error" variant="contained" onClick={onRemove} disabled={removing}>
            {removing ? 'Removing…' : 'Remove'}
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
