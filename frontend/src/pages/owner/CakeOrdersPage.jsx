import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import CakeOutlinedIcon from '@mui/icons-material/CakeOutlined';
import RefreshOutlinedIcon from '@mui/icons-material/RefreshOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useMemo, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import { PageActions } from '../../context/PageActionsContext';
import { useAuth } from '../../context/AuthContext';
import { useModuleGate } from '../../context/ModulesContext';
import {
  createCustomOrder,
  listCustomOrders,
  recordCustomOrderAdvance,
  updateCustomOrderStatus,
} from '../../services/customOrderService';

const COLUMNS = [
  { key: 'BOOKED', label: 'Booked', color: '#ffb74d' },
  { key: 'CONFIRMED', label: 'Confirmed', color: '#64b5f6' },
  { key: 'IN_PRODUCTION', label: 'In production', color: '#ba68c8' },
  { key: 'READY', label: 'Ready', color: '#81c784' },
  { key: 'DELIVERED', label: 'Delivered', color: '#90a4ae' },
];

const NEXT_ACTIONS = {
  BOOKED: [{ status: 'CONFIRMED', label: 'Confirm' }],
  CONFIRMED: [{ status: 'IN_PRODUCTION', label: 'Start production' }],
  IN_PRODUCTION: [{ status: 'READY', label: 'Mark ready' }],
  READY: [{ status: 'DELIVERED', label: 'Mark delivered' }],
  DELIVERED: [],
};

function OrderCard({ order, onStatusChange, onAdvance, updating, canManage, canAdvance }) {
  const actions = NEXT_ACTIONS[order.status] || [];
  return (
    <Card
      sx={{
        bgcolor: '#1e1e1e',
        color: '#f5f5f5',
        border: '1px solid rgba(255,255,255,0.08)',
      }}
    >
      <CardContent sx={{ pb: 1 }}>
        <Stack spacing={1}>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Typography variant="h6" sx={{ fontWeight: 700 }}>
              {order.order_number}
            </Typography>
            <Chip size="small" label={order.status.replaceAll('_', ' ')} />
          </Stack>
          <Typography variant="body1">{order.title}</Typography>
          <Typography variant="body2" color="rgba(255,255,255,0.72)">
            {[order.size, order.flavor].filter(Boolean).join(' · ') || 'Custom cake'}
          </Typography>
          {order.customer_name ? (
            <Typography variant="body2" color="rgba(255,255,255,0.72)">
              {order.customer_name}
              {order.customer_phone ? ` · ${order.customer_phone}` : ''}
            </Typography>
          ) : null}
          {order.delivery_at ? (
            <Typography variant="body2">Delivery {new Date(order.delivery_at).toLocaleString()}</Typography>
          ) : null}
          <Typography variant="body2">
            Total ₹{Number(order.total_amount).toFixed(2)} · Advance ₹
            {Number(order.advance_paid).toFixed(2)} · Due ₹
            {Number(order.remaining_amount).toFixed(2)}
          </Typography>
        </Stack>
      </CardContent>
      <CardActions sx={{ flexWrap: 'wrap', gap: 1, px: 2, pb: 2 }}>
        {canManage
          ? actions.map((action) => (
              <Button
                key={action.status}
                size="small"
                variant="contained"
                disabled={updating}
                onClick={() => onStatusChange(order.id, action.status)}
              >
                {action.label}
              </Button>
            ))
          : null}
        {canAdvance && Number(order.remaining_amount) > 0 && order.status !== 'CANCELLED' ? (
          <Button size="small" variant="outlined" color="inherit" disabled={updating} onClick={() => onAdvance(order)}>
            Record advance
          </Button>
        ) : null}
      </CardActions>
    </Card>
  );
}

const emptyForm = {
  title: '',
  size: '',
  flavor: '',
  customer_name: '',
  customer_phone: '',
  total_amount: '',
  advance_amount: '',
  payment_method: 'cash',
  delivery_at: '',
  notes: '',
};

export default function CakeOrdersPage() {
  const moduleEnabled = useModuleGate('custom_orders');
  const { user } = useAuth();
  const canManage = user?.role === 'OWNER' || user?.role === 'MANAGER';
  const canCreate = Boolean(user);

  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updating, setUpdating] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [advanceTarget, setAdvanceTarget] = useState(null);
  const [advanceAmount, setAdvanceAmount] = useState('');
  const [advanceMethod, setAdvanceMethod] = useState('cash');

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const res = await listCustomOrders({ order_type: 'bakery', per_page: 200 });
      setOrders(res.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load cake orders');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!moduleEnabled) return;
    load();
  }, [moduleEnabled, load]);

  const byStatus = useMemo(() => {
    const map = Object.fromEntries(COLUMNS.map((col) => [col.key, []]));
    for (const order of orders) {
      if (map[order.status]) map[order.status].push(order);
    }
    return map;
  }, [orders]);

  const submit = async () => {
    if (!form.title.trim() || !form.total_amount) {
      setError('Title and total amount are required');
      return;
    }
    setUpdating(true);
    setError('');
    try {
      await createCustomOrder({
        order_type: 'bakery',
        title: form.title.trim(),
        size: form.size || undefined,
        flavor: form.flavor || undefined,
        customer_name: form.customer_name || undefined,
        customer_phone: form.customer_phone || undefined,
        total_amount: form.total_amount,
        advance_amount: form.advance_amount || 0,
        payment_method: form.payment_method,
        delivery_at: form.delivery_at ? new Date(form.delivery_at).toISOString() : undefined,
        notes: form.notes || undefined,
      });
      setDialogOpen(false);
      setForm(emptyForm);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to create order');
    } finally {
      setUpdating(false);
    }
  };

  const onStatusChange = async (id, status) => {
    setUpdating(true);
    setError('');
    try {
      await updateCustomOrderStatus(id, { status });
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to update status');
    } finally {
      setUpdating(false);
    }
  };

  const submitAdvance = async () => {
    if (!advanceTarget || !advanceAmount) return;
    setUpdating(true);
    setError('');
    try {
      await recordCustomOrderAdvance(advanceTarget.id, {
        amount: advanceAmount,
        payment_method: advanceMethod,
      });
      setAdvanceTarget(null);
      setAdvanceAmount('');
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to record advance');
    } finally {
      setUpdating(false);
    }
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="info">Custom orders are not enabled for this business type.</Alert>
      </PageShell>
    );
  }

  return (
    <PageShell>
      <PageActions>
        <Button startIcon={<RefreshOutlinedIcon />} onClick={load} disabled={loading}>
          Refresh
        </Button>
        {canCreate ? (
          <Button
            variant="contained"
            startIcon={<AddOutlinedIcon />}
            onClick={() => {
              setForm(emptyForm);
              setDialogOpen(true);
            }}
          >
            New cake order
          </Button>
        ) : null}
      </PageActions>

      {error ? (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      ) : null}

      {loading ? (
        <LoadingBlock />
      ) : orders.length === 0 ? (
        <EmptyState
          title="No cake orders"
          description="Book a custom cake with size, flavor, advance, and delivery time."
          icon={<CakeOutlinedIcon />}
        />
      ) : (
        <Grid container spacing={2} alignItems="flex-start">
          {COLUMNS.map((col) => (
            <Grid item xs={12} sm={6} md={2.4} key={col.key} sx={{ minWidth: 200, flex: 1 }}>
              <Box
                sx={{
                  borderTop: `3px solid ${col.color}`,
                  bgcolor: 'rgba(0,0,0,0.04)',
                  borderRadius: 1,
                  p: 1,
                  minHeight: 120,
                }}
              >
                <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 700 }}>
                  {col.label} ({byStatus[col.key].length})
                </Typography>
                <Stack spacing={1.5}>
                  {byStatus[col.key].map((order) => (
                    <OrderCard
                      key={order.id}
                      order={order}
                      updating={updating}
                      canManage={canManage}
                      canAdvance={canCreate}
                      onStatusChange={onStatusChange}
                      onAdvance={setAdvanceTarget}
                    />
                  ))}
                </Stack>
              </Box>
            </Grid>
          ))}
        </Grid>
      )}

      <Dialog open={dialogOpen} onClose={() => !updating && setDialogOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>New cake order</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Cake / title"
              value={form.title}
              onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
              required
            />
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                label="Size"
                value={form.size}
                onChange={(e) => setForm((f) => ({ ...f, size: e.target.value }))}
                fullWidth
                placeholder="1 kg / 2 tier"
              />
              <TextField
                label="Flavor"
                value={form.flavor}
                onChange={(e) => setForm((f) => ({ ...f, flavor: e.target.value }))}
                fullWidth
                placeholder="Chocolate"
              />
            </Stack>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                label="Customer name"
                value={form.customer_name}
                onChange={(e) => setForm((f) => ({ ...f, customer_name: e.target.value }))}
                fullWidth
              />
              <TextField
                label="Phone"
                value={form.customer_phone}
                onChange={(e) => setForm((f) => ({ ...f, customer_phone: e.target.value }))}
                fullWidth
              />
            </Stack>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                label="Total amount"
                type="number"
                value={form.total_amount}
                onChange={(e) => setForm((f) => ({ ...f, total_amount: e.target.value }))}
                required
                fullWidth
              />
              <TextField
                label="Advance (less than total)"
                type="number"
                value={form.advance_amount}
                onChange={(e) => setForm((f) => ({ ...f, advance_amount: e.target.value }))}
                fullWidth
              />
            </Stack>
            <TextField
              select
              label="Advance method"
              value={form.payment_method}
              onChange={(e) => setForm((f) => ({ ...f, payment_method: e.target.value }))}
            >
              {['cash', 'upi', 'card', 'other'].map((m) => (
                <MenuItem key={m} value={m}>
                  {m}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              label="Delivery date & time"
              type="datetime-local"
              value={form.delivery_at}
              onChange={(e) => setForm((f) => ({ ...f, delivery_at: e.target.value }))}
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              label="Notes"
              value={form.notes}
              onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))}
              multiline
              minRows={2}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)} disabled={updating}>
            Cancel
          </Button>
          <Button variant="contained" onClick={submit} disabled={updating}>
            {updating ? 'Saving…' : 'Book order'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(advanceTarget)} onClose={() => !updating && setAdvanceTarget(null)} fullWidth maxWidth="xs">
        <DialogTitle>Record advance — {advanceTarget?.order_number}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Typography variant="body2">
              Remaining due ₹{Number(advanceTarget?.remaining_amount || 0).toFixed(2)}
            </Typography>
            <TextField
              label="Amount"
              type="number"
              value={advanceAmount}
              onChange={(e) => setAdvanceAmount(e.target.value)}
              required
            />
            <TextField
              select
              label="Method"
              value={advanceMethod}
              onChange={(e) => setAdvanceMethod(e.target.value)}
            >
              {['cash', 'upi', 'card', 'other'].map((m) => (
                <MenuItem key={m} value={m}>
                  {m}
                </MenuItem>
              ))}
            </TextField>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAdvanceTarget(null)} disabled={updating}>
            Cancel
          </Button>
          <Button variant="contained" onClick={submitAdvance} disabled={updating || !advanceAmount}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
