import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import LocalShippingOutlinedIcon from '@mui/icons-material/LocalShippingOutlined';
import RefreshOutlinedIcon from '@mui/icons-material/RefreshOutlined';
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useMemo, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import StatusBadge from '../../components/ui/StatusBadge';
import { PageActions } from '../../context/PageActionsContext';
import { useAuth } from '../../context/AuthContext';
import { useModuleGate } from '../../context/ModulesContext';
import { listCustomOrders } from '../../services/customOrderService';
import {
  createDelivery,
  listDeliveries,
  updateDeliveryStatus,
} from '../../services/deliveryService';

const COLUMNS = [
  { key: 'SCHEDULED', label: 'Scheduled', color: '#ffb74d' },
  { key: 'OUT_FOR_DELIVERY', label: 'Out for delivery', color: '#64b5f6' },
  { key: 'DELIVERED', label: 'Delivered', color: '#81c784' },
];

const NEXT_ACTIONS = {
  SCHEDULED: [{ status: 'OUT_FOR_DELIVERY', label: 'Out for delivery' }],
  OUT_FOR_DELIVERY: [{ status: 'DELIVERED', label: 'Mark delivered' }],
  DELIVERED: [],
};

function formatWhen(value) {
  if (!value) return 'Unscheduled';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

function deliveryStatusVariant(status) {
  if (status === 'SCHEDULED') return 'pending';
  if (status === 'OUT_FOR_DELIVERY') return 'info';
  if (status === 'DELIVERED') return 'active';
  return 'info';
}

function DeliveryCard({ job, onStatusChange, updating, canWrite }) {
  const actions = NEXT_ACTIONS[job.status] || [];

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
              {job.delivery_number}
            </Typography>
            <StatusBadge
              label={job.status.replaceAll('_', ' ')}
              variant={deliveryStatusVariant(job.status)}
            />
          </Stack>
          <Typography variant="body2" color="rgba(255,255,255,0.72)">
            {job.custom_order_number} · {job.custom_order_title}
          </Typography>
          <Typography variant="body2" color="rgba(255,255,255,0.72)">
            {formatWhen(job.scheduled_at)}
          </Typography>
          {job.customer_name ? (
            <Typography variant="body2" color="rgba(255,255,255,0.72)">
              {job.customer_name}
              {job.customer_phone ? ` · ${job.customer_phone}` : ''}
            </Typography>
          ) : null}
          {job.delivery_address ? (
            <Typography variant="body1">{job.delivery_address}</Typography>
          ) : null}
          {job.driver_name ? (
            <Typography variant="body2">
              Driver: {job.driver_name}
              {job.vehicle_number ? ` · ${job.vehicle_number}` : ''}
            </Typography>
          ) : null}
          {job.notes ? (
            <Typography variant="body2" color="warning.light">
              Note: {job.notes}
            </Typography>
          ) : null}
        </Stack>
      </CardContent>
      {canWrite && actions.length ? (
        <CardActions sx={{ px: 2, pb: 2, flexDirection: 'column', gap: 1 }}>
          {actions.map((action) => (
            <Button
              key={action.status}
              fullWidth
              variant="contained"
              size="large"
              disabled={updating === job.id}
              onClick={() => onStatusChange(job.id, action.status)}
              sx={{ minHeight: 48 }}
            >
              {action.label}
            </Button>
          ))}
        </CardActions>
      ) : null}
    </Card>
  );
}

export default function DeliveriesPage() {
  const moduleEnabled = useModuleGate('delivery_tracking');
  const { role } = useAuth();
  const canWrite = role === 'OWNER' || role === 'MANAGER';

  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updating, setUpdating] = useState('');

  const [createOpen, setCreateOpen] = useState(false);
  const [orderOptions, setOrderOptions] = useState([]);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [deliveryAddress, setDeliveryAddress] = useState('');
  const [scheduledAt, setScheduledAt] = useState('');
  const [customerName, setCustomerName] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');
  const [driverName, setDriverName] = useState('');
  const [vehicleNumber, setVehicleNumber] = useState('');
  const [notes, setNotes] = useState('');
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    if (!moduleEnabled) return;
    setError('');
    try {
      const response = await listDeliveries({ per_page: 200 });
      setJobs(response.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load delivery jobs.');
    } finally {
      setLoading(false);
    }
  }, [moduleEnabled]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (!moduleEnabled) return undefined;
    const timer = window.setInterval(load, 30000);
    return () => window.clearInterval(timer);
  }, [load, moduleEnabled]);

  const groupedByStatus = useMemo(() => {
    const map = Object.fromEntries(COLUMNS.map((col) => [col.key, []]));
    jobs.forEach((job) => {
      if (map[job.status]) map[job.status].push(job);
    });
    return map;
  }, [jobs]);

  const openCreate = async () => {
    setCreateOpen(true);
    setSelectedOrder(null);
    setDeliveryAddress('');
    setScheduledAt('');
    setCustomerName('');
    setCustomerPhone('');
    setDriverName('');
    setVehicleNumber('');
    setNotes('');
    setError('');
    try {
      const res = await listCustomOrders({ order_type: 'furniture', status: 'READY', per_page: 100 });
      setOrderOptions(res.data || []);
    } catch {
      setOrderOptions([]);
    }
  };

  const onStatusChange = async (deliveryId, status) => {
    setUpdating(deliveryId);
    setError('');
    try {
      await updateDeliveryStatus(deliveryId, { status });
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to update delivery status.');
    } finally {
      setUpdating('');
    }
  };

  const submitCreate = async () => {
    if (!selectedOrder) {
      setError('Select a ready furniture order.');
      return;
    }
    if (!deliveryAddress.trim()) {
      setError('Delivery address is required.');
      return;
    }
    setSaving(true);
    setError('');
    try {
      await createDelivery({
        custom_order_id: selectedOrder.id,
        delivery_address: deliveryAddress.trim(),
        scheduled_at: scheduledAt
          ? scheduledAt.length === 16
            ? `${scheduledAt}:00`
            : scheduledAt
          : undefined,
        customer_name: customerName.trim() || undefined,
        customer_phone: customerPhone.trim() || undefined,
        driver_name: driverName.trim() || undefined,
        vehicle_number: vehicleNumber.trim() || undefined,
        notes: notes.trim() || undefined,
      });
      setCreateOpen(false);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not schedule delivery.');
    } finally {
      setSaving(false);
    }
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="warning">Delivery tracking is not enabled for this business type.</Alert>
      </PageShell>
    );
  }

  return (
    <>
      <PageActions>
        <Button variant="outlined" startIcon={<RefreshOutlinedIcon />} onClick={load}>
          Refresh
        </Button>
        {canWrite ? (
          <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={openCreate}>
            Schedule delivery
          </Button>
        ) : null}
      </PageActions>

      <PageShell>
        <Box
          sx={{
            bgcolor: '#121212',
            color: '#f5f5f5',
            borderRadius: 2,
            p: { xs: 2, md: 3 },
            minHeight: '60vh',
          }}
        >
          <Stack spacing={3}>
            <Stack direction="row" spacing={1} alignItems="center">
              <LocalShippingOutlinedIcon />
              <Typography variant="h5" sx={{ fontWeight: 700 }}>
                Delivery board
              </Typography>
            </Stack>
            {!canWrite ? (
              <Alert severity="info">
                Billing users can view deliveries. Owner or manager updates status.
              </Alert>
            ) : null}
            {error && !createOpen ? <Alert severity="error">{error}</Alert> : null}
            {loading ? (
              <LoadingBlock />
            ) : jobs.length === 0 ? (
              <EmptyState
                title="No delivery jobs yet"
                description="Schedule delivery when a furniture order is ready."
                actionLabel={canWrite ? 'Schedule delivery' : undefined}
                onAction={canWrite ? openCreate : undefined}
              />
            ) : (
              <Grid container spacing={2}>
                {COLUMNS.map((column) => (
                  <Grid item xs={12} md={4} key={column.key}>
                    <Stack spacing={1.5}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 700, color: column.color }}>
                        {column.label} ({groupedByStatus[column.key].length})
                      </Typography>
                      {groupedByStatus[column.key].map((job) => (
                        <DeliveryCard
                          key={job.id}
                          job={job}
                          onStatusChange={onStatusChange}
                          updating={updating}
                          canWrite={canWrite}
                        />
                      ))}
                    </Stack>
                  </Grid>
                ))}
              </Grid>
            )}
          </Stack>
        </Box>
      </PageShell>

      <Dialog open={createOpen} onClose={() => !saving && setCreateOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Schedule delivery</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            {error && createOpen ? <Alert severity="error">{error}</Alert> : null}
            <Autocomplete
              options={orderOptions}
              getOptionLabel={(option) =>
                `${option.order_number} · ${option.title} (${option.customer_name || 'Walk-in'})`
              }
              value={selectedOrder}
              onChange={(_, value) => {
                setSelectedOrder(value);
                if (value) {
                  setCustomerName(value.customer_name || '');
                  setCustomerPhone(value.customer_phone || '');
                }
              }}
              renderInput={(params) => <TextField {...params} label="Ready furniture order" required />}
            />
            <TextField
              label="Delivery address"
              value={deliveryAddress}
              onChange={(e) => setDeliveryAddress(e.target.value)}
              multiline
              minRows={2}
              required
              fullWidth
            />
            <TextField
              label="Scheduled at"
              type="datetime-local"
              value={scheduledAt}
              onChange={(e) => setScheduledAt(e.target.value)}
              fullWidth
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              label="Customer name"
              value={customerName}
              onChange={(e) => setCustomerName(e.target.value)}
              fullWidth
            />
            <TextField
              label="Customer phone"
              value={customerPhone}
              onChange={(e) => setCustomerPhone(e.target.value)}
              fullWidth
            />
            <TextField
              label="Driver"
              value={driverName}
              onChange={(e) => setDriverName(e.target.value)}
              fullWidth
            />
            <TextField
              label="Vehicle number"
              value={vehicleNumber}
              onChange={(e) => setVehicleNumber(e.target.value)}
              fullWidth
            />
            <TextField
              label="Notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              multiline
              minRows={2}
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateOpen(false)} disabled={saving}>
            Cancel
          </Button>
          <Button variant="contained" onClick={submitCreate} disabled={saving}>
            {saving ? 'Saving…' : 'Schedule'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
