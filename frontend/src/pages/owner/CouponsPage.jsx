import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import {
  Alert,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  FormControlLabel,
  IconButton,
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
  Tooltip,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import TableCard from '../../components/TableCard';
import { PageActions } from '../../context/PageActionsContext';
import { useModuleGate } from '../../context/ModulesContext';
import { usePermissions } from '../../hooks/usePermissions';
import {
  createCoupon,
  deactivateCoupon,
  listCoupons,
  updateCoupon,
} from '../../services/couponService';

const emptyForm = () => ({
  code: '',
  name: '',
  description: '',
  discount_type: 'amount',
  discount_value: '',
  min_order_amount: '',
  max_discount_amount: '',
  starts_on: '',
  ends_on: '',
  usage_limit: '',
  is_active: true,
});

function money(value) {
  if (value == null || value === '') return '—';
  return `₹${Number(value).toFixed(2)}`;
}

export default function CouponsPage() {
  const moduleEnabled = useModuleGate('addons_combos');
  const { canManageAddons } = usePermissions();
  const [coupons, setCoupons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState(emptyForm());

  const load = useCallback(async () => {
    if (!moduleEnabled) return;
    setLoading(true);
    setError('');
    try {
      const res = await listCoupons();
      setCoupons(res.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load coupons.');
    } finally {
      setLoading(false);
    }
  }, [moduleEnabled]);

  useEffect(() => {
    load();
  }, [load]);

  const resetForm = () => {
    setEditing(null);
    setForm(emptyForm());
  };

  const openCreate = () => {
    resetForm();
    setOpen(true);
  };

  const openEdit = (coupon) => {
    setEditing(coupon);
    setForm({
      code: coupon.code || '',
      name: coupon.name || '',
      description: coupon.description || '',
      discount_type: coupon.discount_type || 'amount',
      discount_value: String(coupon.discount_value ?? ''),
      min_order_amount: coupon.min_order_amount != null ? String(coupon.min_order_amount) : '',
      max_discount_amount:
        coupon.max_discount_amount != null ? String(coupon.max_discount_amount) : '',
      starts_on: coupon.starts_on || '',
      ends_on: coupon.ends_on || '',
      usage_limit: coupon.usage_limit != null ? String(coupon.usage_limit) : '',
      is_active: Boolean(coupon.is_active),
    });
    setOpen(true);
  };

  const onSave = async () => {
    if (!form.code.trim() || !form.name.trim() || form.discount_value === '') {
      setError('Code, name, and discount value are required.');
      return;
    }
    setSaving(true);
    setError('');
    setSuccess('');
    const payload = {
      code: form.code.trim(),
      name: form.name.trim(),
      description: form.description.trim() || null,
      discount_type: form.discount_type,
      discount_value: Number(form.discount_value),
      min_order_amount: form.min_order_amount === '' ? null : Number(form.min_order_amount),
      max_discount_amount:
        form.max_discount_amount === '' ? null : Number(form.max_discount_amount),
      starts_on: form.starts_on || null,
      ends_on: form.ends_on || null,
      usage_limit: form.usage_limit === '' ? null : Number(form.usage_limit),
      is_active: Boolean(form.is_active),
    };
    try {
      if (editing) {
        await updateCoupon(editing.id, payload);
        setSuccess('Coupon updated.');
      } else {
        await createCoupon(payload);
        setSuccess('Coupon created.');
      }
      setOpen(false);
      resetForm();
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to save coupon.');
    } finally {
      setSaving(false);
    }
  };

  const onDeactivate = async (id) => {
    if (!window.confirm('Deactivate this coupon?')) return;
    setError('');
    try {
      await deactivateCoupon(id);
      setSuccess('Coupon deactivated.');
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to deactivate coupon.');
    }
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="warning">Coupons are not enabled for this business type.</Alert>
      </PageShell>
    );
  }

  return (
    <>
      {canManageAddons ? (
        <PageActions>
          <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={openCreate}>
            New coupon
          </Button>
        </PageActions>
      ) : null}

      <PageShell>
        <Stack spacing={2}>
          <Typography variant="body2" color="text.secondary">
            Cafe-only promo codes applied at Cafe POS settle. Percent or flat amount; optional
            min order and usage limits.
          </Typography>
          {error ? <Alert severity="error">{error}</Alert> : null}
          {success ? <Alert severity="success">{success}</Alert> : null}
          <TableCard>
            {loading ? (
              <LoadingBlock />
            ) : coupons.length === 0 ? (
              <EmptyState
                title="No coupons yet"
                description="Create a code like CHAI10 for Cafe POS."
                actionLabel={canManageAddons ? 'New coupon' : undefined}
                onAction={canManageAddons ? openCreate : undefined}
              />
            ) : (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Code</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Discount</TableCell>
                    <TableCell>Usage</TableCell>
                    <TableCell>Active</TableCell>
                    {canManageAddons ? <TableCell align="right">Actions</TableCell> : null}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {coupons.map((coupon) => (
                    <TableRow key={coupon.id}>
                      <TableCell>
                        <Typography variant="body2" fontWeight={600}>
                          {coupon.code}
                        </Typography>
                      </TableCell>
                      <TableCell>{coupon.name}</TableCell>
                      <TableCell>
                        {coupon.discount_type === 'percent'
                          ? `${coupon.discount_value}%`
                          : money(coupon.discount_value)}
                      </TableCell>
                      <TableCell>
                        {coupon.usage_count}
                        {coupon.usage_limit != null ? ` / ${coupon.usage_limit}` : ''}
                      </TableCell>
                      <TableCell>{coupon.is_active ? 'Yes' : 'No'}</TableCell>
                      {canManageAddons ? (
                        <TableCell align="right">
                          <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                            <Tooltip title="Edit">
                              <IconButton size="small" onClick={() => openEdit(coupon)}>
                                <EditOutlinedIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            {coupon.is_active ? (
                              <Tooltip title="Deactivate">
                                <IconButton
                                  size="small"
                                  color="error"
                                  onClick={() => onDeactivate(coupon.id)}
                                >
                                  <DeleteOutlinedIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            ) : null}
                          </Stack>
                        </TableCell>
                      ) : null}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </TableCard>
        </Stack>
      </PageShell>

      <Dialog
        open={open}
        onClose={() => {
          setOpen(false);
          resetForm();
        }}
        fullWidth
        maxWidth="sm"
      >
        <DialogTitle>{editing ? 'Edit coupon' : 'New coupon'}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Code"
              value={form.code}
              onChange={(e) => setForm((prev) => ({ ...prev, code: e.target.value.toUpperCase() }))}
              required
              helperText="Stored uppercase — e.g. CHAI10"
            />
            <TextField
              label="Name"
              value={form.name}
              onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
              required
            />
            <TextField
              label="Description"
              value={form.description}
              onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))}
              multiline
              minRows={2}
            />
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <FormControl sx={{ minWidth: 160 }}>
                <InputLabel id="coupon-type-label">Type</InputLabel>
                <Select
                  labelId="coupon-type-label"
                  label="Type"
                  value={form.discount_type}
                  onChange={(e) => setForm((prev) => ({ ...prev, discount_type: e.target.value }))}
                >
                  <MenuItem value="amount">Flat ₹</MenuItem>
                  <MenuItem value="percent">Percent %</MenuItem>
                </Select>
              </FormControl>
              <TextField
                label={form.discount_type === 'percent' ? 'Percent' : 'Amount ₹'}
                type="number"
                value={form.discount_value}
                onChange={(e) => setForm((prev) => ({ ...prev, discount_value: e.target.value }))}
                required
                fullWidth
              />
            </Stack>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                label="Min order ₹"
                type="number"
                value={form.min_order_amount}
                onChange={(e) => setForm((prev) => ({ ...prev, min_order_amount: e.target.value }))}
                fullWidth
              />
              <TextField
                label="Max discount ₹"
                type="number"
                value={form.max_discount_amount}
                onChange={(e) =>
                  setForm((prev) => ({ ...prev, max_discount_amount: e.target.value }))
                }
                fullWidth
                helperText="Optional cap for percent coupons"
              />
            </Stack>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                label="Starts on"
                type="date"
                value={form.starts_on}
                onChange={(e) => setForm((prev) => ({ ...prev, starts_on: e.target.value }))}
                InputLabelProps={{ shrink: true }}
                fullWidth
              />
              <TextField
                label="Ends on"
                type="date"
                value={form.ends_on}
                onChange={(e) => setForm((prev) => ({ ...prev, ends_on: e.target.value }))}
                InputLabelProps={{ shrink: true }}
                fullWidth
              />
            </Stack>
            <TextField
              label="Usage limit"
              type="number"
              value={form.usage_limit}
              onChange={(e) => setForm((prev) => ({ ...prev, usage_limit: e.target.value }))}
              helperText="Leave blank for unlimited"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={form.is_active}
                  onChange={(e) => setForm((prev) => ({ ...prev, is_active: e.target.checked }))}
                />
              }
              label="Active"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => {
              setOpen(false);
              resetForm();
            }}
          >
            Cancel
          </Button>
          <Button variant="contained" disabled={saving} onClick={onSave}>
            {saving ? 'Saving…' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
